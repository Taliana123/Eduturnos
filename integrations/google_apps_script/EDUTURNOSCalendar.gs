/**
 * EDUTURNOS -> Google Calendar bridge.
 * Deploy as a web app that executes as the script owner. Keep the webhook
 * secret in Script Properties; never place it in this source file.
 */
const EDUTURNOS_TAG = 'eduturnos_external_id';
const EDUTURNOS_MAX_SKEW_SECONDS = 300;
const EDUTURNOS_PROTOCOL = 'payload-json-v2';

function doGet() {
  return json_({ ok: true, service: 'EDUTURNOS Calendar bridge', protocol: EDUTURNOS_PROTOCOL });
}

function doPost(e) {
  try {
    const envelope = JSON.parse(e && e.postData && e.postData.contents || '{}');
    const payloadJson = typeof envelope.payload_json === 'string' ? envelope.payload_json : '';
    const payload = payloadJson ? JSON.parse(payloadJson) : envelope.payload;
    if (!payload || !verify_(envelope, payloadJson)) return json_({ ok: false, status: 403, error: 'Firma no válida o vencida.' });

    const cache = CacheService.getScriptCache();
    const nonceKey = 'nonce_' + String(envelope.nonce);
    if (cache.get(nonceKey)) return json_({ ok: false, status: 409, error: 'Solicitud repetida.' });
    cache.put(nonceKey, '1', EDUTURNOS_MAX_SKEW_SECONDS);

    const calendar = getCalendar_();
    if (payload.action === 'test') {
      return json_({ ok: true, protocol: EDUTURNOS_PROTOCOL, calendar: calendar.getName(), calendarId: calendar.getId() });
    }
    if (payload.action === 'upsert') return json_(upsert_(calendar, payload));
    if (payload.action === 'delete') return json_(delete_(calendar, payload));
    return json_({ ok: false, status: 400, error: 'Operación desconocida.' });
  } catch (error) {
    console.error('EDUTURNOS Calendar bridge failed: ' + String(error));
    return json_({ ok: false, status: 503, error: 'No se pudo completar la operación de calendario.' });
  }
}

function verify_(envelope, payloadJson) {
  const secret = PropertiesService.getScriptProperties().getProperty('EDUTURNOS_WEBHOOK_SECRET') || '';
  const timestamp = String(envelope.timestamp || '');
  const nonce = String(envelope.nonce || '');
  if (secret.length < 32 || !/^\d{10}$/.test(timestamp) || !/^[a-f0-9]{32}$/.test(nonce)) return false;
  if (Math.abs(Math.floor(Date.now() / 1000) - Number(timestamp)) > EDUTURNOS_MAX_SKEW_SECONDS) return false;
  // Prefer the exact canonical JSON bytes supplied and signed by Flask.
  // This avoids cross-runtime JSON serialization differences; the fallback
  // keeps compatibility with older EDUTURNOS deployments.
  const canonicalPayload = payloadJson || canonical_(envelope.payload);
  const message = timestamp + '\n' + nonce + '\n' + canonicalPayload;
  const expected = Utilities.base64EncodeWebSafe(
    Utilities.computeHmacSha256Signature(message, secret),
  ).replace(/=+$/, '');
  return constantTimeEqual_(expected, String(envelope.signature || ''));
}

function canonical_(value) {
  if (Array.isArray(value)) return '[' + value.map(canonical_).join(',') + ']';
  if (value && typeof value === 'object') {
    return '{' + Object.keys(value).sort().map(function (key) {
      return JSON.stringify(key) + ':' + canonical_(value[key]);
    }).join(',') + '}';
  }
  return JSON.stringify(value);
}

function constantTimeEqual_(left, right) {
  if (left.length !== right.length) return false;
  let diff = 0;
  for (let i = 0; i < left.length; i++) diff |= left.charCodeAt(i) ^ right.charCodeAt(i);
  return diff === 0;
}

function getCalendar_() {
  const id = (PropertiesService.getScriptProperties().getProperty('EDUTURNOS_CALENDAR_ID') || 'primary').trim();
  const calendar = id === 'primary' ? CalendarApp.getDefaultCalendar() : CalendarApp.getCalendarById(id);
  if (!calendar) throw new Error('No se encontró el calendario configurado.');
  return calendar;
}

function upsert_(calendar, payload) {
  if (!payload.external_id || !payload.start || !payload.end) {
    return { ok: false, status: 400, error: 'Faltan datos obligatorios del evento.' };
  }
  const start = new Date(payload.start);
  const end = new Date(payload.end);
  if (isNaN(start.getTime()) || isNaN(end.getTime()) || end <= start) {
    return { ok: false, status: 400, error: 'La fecha u hora del evento no es válida.' };
  }

  let event = null;
  if (payload.google_event_id) event = calendar.getEventById(payload.google_event_id);
  if (event) {
    const storedExternalId = event.getTag(EDUTURNOS_TAG);
    if (storedExternalId && storedExternalId !== payload.external_id) {
      event = null;
    } else if (!storedExternalId) {
      // Adopt existing generic events created by the previous EDUTURNOS OAuth integration.
      const wasCreatedByEduturnos = event.getTitle() === 'Citación escolar'
        && event.getDescription() === 'Consulta los detalles de la cita en EDUTURNOS.';
      if (wasCreatedByEduturnos) event.setTag(EDUTURNOS_TAG, payload.external_id);
      else event = null;
    }
  }
  if (!event) {
    const nearby = calendar.getEvents(new Date(start.getTime() - 86400000), new Date(end.getTime() + 86400000));
    event = nearby.find(function (candidate) {
      return candidate.getTag(EDUTURNOS_TAG) === payload.external_id;
    }) || null;
  }
  if (event) {
    event.setTitle(payload.title || 'Citación escolar');
    event.setDescription(payload.description || 'Consulta los detalles de la cita en EDUTURNOS.');
    event.setLocation(payload.location || '');
    event.setTime(start, end);
  } else {
    event = calendar.createEvent(payload.title || 'Citación escolar', start, end, {
      description: payload.description || 'Consulta los detalles de la cita en EDUTURNOS.',
      location: payload.location || '',
    });
    event.setTag(EDUTURNOS_TAG, payload.external_id);
  }
  const attendees = Array.from(new Set((Array.isArray(payload.attendees) ? payload.attendees : [])
    .map(function (email) { return String(email || '').trim().toLowerCase(); })
    .filter(function (email) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email); })));
  const apiEvent = findCalendarApiEvent_(calendar, event.getId());
  if (!apiEvent) throw new Error('No se pudo localizar el evento creado en Google Calendar.');

  Calendar.Events.patch({
    attendees: attendees.map(function (email) { return { email: email }; }),
    guestsCanModify: false,
    guestsCanInviteOthers: false,
    guestsCanSeeOtherGuests: false,
    reminders: { useDefault: false, overrides: [
      { method: 'popup', minutes: 1440 },
      { method: 'popup', minutes: 120 },
    ] },
  }, calendar.getId(), apiEvent.id, { sendUpdates: 'all' });
  return { ok: true, eventId: event.getId(), invited: attendees.length };
}

function delete_(calendar, payload) {
  let event = payload.google_event_id ? calendar.getEventById(payload.google_event_id) : null;
  if (event && payload.external_id && event.getTag(EDUTURNOS_TAG) !== payload.external_id) event = null;
  if (!event && payload.external_id && payload.start) {
    const start = new Date(payload.start);
    if (!isNaN(start.getTime())) {
      const nearby = calendar.getEvents(new Date(start.getTime() - 86400000), new Date(start.getTime() + 86400000));
      event = nearby.find(function (candidate) { return candidate.getTag(EDUTURNOS_TAG) === payload.external_id; }) || null;
    }
  }
  if (event) {
    const apiEvent = findCalendarApiEvent_(calendar, event.getId());
    if (apiEvent) Calendar.Events.remove(calendar.getId(), apiEvent.id, { sendUpdates: 'all' });
    else event.deleteEvent();
  }
  return { ok: true };
}

function findCalendarApiEvent_(calendar, iCalUID) {
  const result = Calendar.Events.list(calendar.getId(), { iCalUID: iCalUID, maxResults: 10, showDeleted: false });
  return (result.items || []).find(function (item) {
    return item.status === 'confirmed' && item.iCalUID === iCalUID && item.id;
  }) || null;
}

function json_(value) {
  return ContentService.createTextOutput(JSON.stringify(value))
    .setMimeType(ContentService.MimeType.JSON);
}

/** Run manually once from the Apps Script editor to request calendar access. */
function authorizeCalendarAccess() {
  const calendar = getCalendar_();
  console.log('Calendar access ready: ' + calendar.getName());
}
