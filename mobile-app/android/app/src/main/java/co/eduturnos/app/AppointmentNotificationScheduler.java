package co.eduturnos.app;

import android.Manifest;
import android.app.AlarmManager;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.os.Build;

import androidx.core.app.NotificationManagerCompat;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.HashSet;
import java.util.Set;

final class AppointmentNotificationScheduler {
    static final String CHANNEL_ID = "appointment_reminders";
    static final String ACTION_APPOINTMENT_NOTIFICATION =
            "co.eduturnos.app.ACTION_APPOINTMENT_NOTIFICATION";
    private static final String PREFERENCES = "eduturnos_appointment_notifications";
    private static final String SCHEDULED_KEY = "scheduled_reminders";
    private static final int[] REMINDER_MINUTES = {1440, 120};
    private static final long MINUTE_MILLIS = 60_000L;

    private AppointmentNotificationScheduler() {
    }

    static boolean hasPermission(Context context) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU
                && context.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)
                != PackageManager.PERMISSION_GRANTED) {
            return false;
        }
        return NotificationManagerCompat.from(context).areNotificationsEnabled();
    }

    static void createChannel(Context context, String channelId) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return;
        NotificationManager manager = context.getSystemService(NotificationManager.class);
        if (manager == null) {
            throw new IllegalStateException("Android notification service is unavailable.");
        }
        NotificationChannel channel = new NotificationChannel(
                channelId,
                "Recordatorios de citas",
                NotificationManager.IMPORTANCE_DEFAULT
        );
        channel.setDescription("Avisos locales de citas programadas en EDUTURNOS.");
        manager.createNotificationChannel(channel);
    }

    static int replaceSchedule(Context context, JSONArray appointments) throws JSONException {
        cancelStoredSchedule(context, true);
        JSONArray scheduled = new JSONArray();
        Set<Integer> ids = new HashSet<>();
        long now = System.currentTimeMillis();

        for (int index = 0; index < appointments.length(); index++) {
            JSONObject appointment = appointments.optJSONObject(index);
            if (appointment == null) continue;
            long appointmentId = appointment.optLong("id", 0);
            long startAt = appointment.optLong("startAt", 0);
            if (appointmentId <= 0 || startAt <= now) continue;

            for (int reminderMinutes : REMINDER_MINUTES) {
                long triggerAt = startAt - reminderMinutes * MINUTE_MILLIS;
                if (triggerAt <= now) continue;
                int notificationId = notificationId(appointmentId, reminderMinutes);
                if (!ids.add(notificationId)) continue;
                scheduleOne(context, notificationId, appointmentId, triggerAt, reminderMinutes);
                scheduled.put(new JSONObject()
                        .put("notificationId", notificationId)
                        .put("appointmentId", appointmentId)
                        .put("triggerAt", triggerAt)
                        .put("reminderMinutes", reminderMinutes));
            }
        }
        saveSchedule(context, scheduled);
        return scheduled.length();
    }

    static void cancelAll(Context context) {
        cancelStoredSchedule(context, true);
        saveSchedule(context, new JSONArray());
    }

    static void restoreSchedule(Context context) throws JSONException {
        JSONArray stored = readSchedule(context);
        JSONArray remaining = new JSONArray();
        long now = System.currentTimeMillis();
        for (int index = 0; index < stored.length(); index++) {
            JSONObject reminder = stored.optJSONObject(index);
            if (reminder == null) continue;
            long triggerAt = reminder.optLong("triggerAt", 0);
            if (triggerAt <= now) continue;
            scheduleOne(
                    context,
                    reminder.getInt("notificationId"),
                    reminder.getLong("appointmentId"),
                    triggerAt,
                    reminder.getInt("reminderMinutes")
            );
            remaining.put(reminder);
        }
        saveSchedule(context, remaining);
    }

    private static void cancelStoredSchedule(Context context, boolean clearShown) {
        JSONArray stored = readSchedule(context);
        AlarmManager manager = context.getSystemService(AlarmManager.class);
        if (manager == null && stored.length() > 0) {
            throw new IllegalStateException("Android alarm service is unavailable.");
        }
        for (int index = 0; index < stored.length(); index++) {
            JSONObject reminder = stored.optJSONObject(index);
            if (reminder == null) continue;
            int notificationId = reminder.optInt("notificationId", 0);
            if (notificationId == 0) continue;
            manager.cancel(alarmIntent(context, notificationId, 0, 0));
            if (clearShown) {
                NotificationManagerCompat.from(context).cancel(notificationId);
            }
        }
    }

    private static JSONArray readSchedule(Context context) {
        String json = preferences(context).getString(SCHEDULED_KEY, "[]");
        try {
            return new JSONArray(json);
        } catch (JSONException error) {
            throw new IllegalStateException("Stored appointment reminder schedule is invalid.", error);
        }
    }

    private static void saveSchedule(Context context, JSONArray schedule) {
        preferences(context).edit().putString(SCHEDULED_KEY, schedule.toString()).apply();
    }

    private static SharedPreferences preferences(Context context) {
        return context.getSharedPreferences(PREFERENCES, Context.MODE_PRIVATE);
    }

    private static void scheduleOne(
            Context context,
            int notificationId,
            long appointmentId,
            long triggerAt,
            int reminderMinutes
    ) {
        AlarmManager manager = context.getSystemService(AlarmManager.class);
        if (manager == null) {
            throw new IllegalStateException("Android alarm service is unavailable.");
        }
        manager.setAndAllowWhileIdle(
                AlarmManager.RTC_WAKEUP,
                triggerAt,
                alarmIntent(context, notificationId, appointmentId, reminderMinutes)
        );
    }

    private static PendingIntent alarmIntent(
            Context context,
            int notificationId,
            long appointmentId,
            int reminderMinutes
    ) {
        Intent intent = new Intent(context, AppointmentNotificationReceiver.class)
                .setAction(ACTION_APPOINTMENT_NOTIFICATION)
                .putExtra("notificationId", notificationId)
                .putExtra("appointmentId", appointmentId)
                .putExtra("reminderMinutes", reminderMinutes);
        return PendingIntent.getBroadcast(
                context,
                notificationId,
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );
    }

    private static int notificationId(long appointmentId, int reminderMinutes) {
        int id = ("eduturnos:" + appointmentId + ":" + reminderMinutes).hashCode() & 0x7fffffff;
        return id == 0 ? 1 : id;
    }
}
