from pathlib import Path


def test_drone_mascot_is_shared_by_login_and_dashboard():
    login = Path("templates/auth/login.html").read_text(encoding="utf-8")
    dashboard = Path("templates/dashboard.html").read_text(encoding="utf-8")
    mascot = Path("templates/_page_mascot.html").read_text(encoding="utf-8")
    styles = Path("static/css/page-mascot.css").read_text(encoding="utf-8")
    script = Path("static/js/page-mascot.js").read_text(encoding="utf-8")

    assert "{% include '_page_mascot.html' %}" in login
    assert "{% include '_page_mascot.html' %}" not in dashboard
    assert "{% include '_page_mascot.html' %}" in Path("templates/base.html").read_text(encoding="utf-8")
    assert "{% include '_page_mascot.html' %}" in Path("templates/index.html").read_text(encoding="utf-8")
    assert "{% include '_page_mascot.html' %}" in Path("templates/publico/base_publica.html").read_text(encoding="utf-8")
    assert "20261109_release24_cache_v1" in login
    assert "20261109_release24_cache_v1" in Path("templates/base.html").read_text(encoding="utf-8")
    assert "20261109_release24_cache_v1" in mascot
    assert "mascots/drone-directions.webp" in mascot
    assert "mascots/drone-reactions.webp" in mascot
    assert "page-mascot--login" not in mascot
    assert Path("static/mascots/drone-directions.webp").is_file()
    assert Path("static/mascots/drone-reactions.webp").is_file()
    assert Path("static/mascots/LICENSE.page-mascot.txt").is_file()
    assert "background-size: 300% 300%" in styles
    assert "width: 136px !important" in styles
    assert "height: 136px !important" in styles
    assert "width: 128px !important" in styles
    assert "height: 128px !important" in styles
    assert ".page-mascot--floating" in styles
    assert "bottom: max(88px, calc(env(safe-area-inset-bottom) + 72px))" in styles
    assert "max-height: 136px !important" in styles
    assert "background: transparent !important" in styles
    assert "setPointerCapture" in script
    assert 'addEventListener("pointerdown"' in script
    assert "event.stopImmediatePropagation()" in script
    assert "localStorage" in script
    assert 'addEventListener("pointermove", updateGaze' in script
    assert 'addEventListener("click"' in script
    assert "prefers-reduced-motion" in script


def test_drone_sprite_sheets_are_served_by_flask():
    from app import app as flask_app

    client = flask_app.test_client()
    login = client.get("/auth/login")
    assert login.status_code == 200
    assert b'data-page-mascot' in login.data
    assert b"/static/mascots/drone-directions.webp" in login.data
    assert b"/static/mascots/drone-reactions.webp" in login.data
    assert b"data-assistant-public-call" in login.data
    assert b"/static/js/asistente.js?v=20261109_markdown_lists_v4" in login.data
    assert b"page-mascot--login" not in login.data
    assert login.data.index(b"page-mascot--floating") > login.data.index(b"</main>")

    for filename in ("drone-directions.webp", "drone-reactions.webp"):
        response = client.get(f"/static/mascots/{filename}")
        assert response.status_code == 200
        assert response.mimetype == "image/webp"
        assert response.data[:4] == b"RIFF"
        assert response.data[8:12] == b"WEBP"

    home = client.get("/")
    assert home.status_code == 200
    assert b"data-assistant-public-call" in home.data
    assert b"/static/js/asistente.js?v=20261109_markdown_lists_v4" in home.data


def test_legacy_floating_robot_widget_is_removed_without_removing_chat_avatar():
    sources = (
        Path("templates/_asistente_widget.html").read_text(encoding="utf-8"),
        Path("templates/auth/login.html").read_text(encoding="utf-8"),
        Path("templates/dashboard.html").read_text(encoding="utf-8"),
    )

    assert all("icons/edubot.png" not in source for source in sources)
    assert all("edubot-mascot" not in source for source in sources)
    assert not Path("templates/_edubot_mascot.html").exists()
    assert not Path("static/css/edubot-mascot.css").exists()
    assert not Path("static/js/edubot-mascot.js").exists()
    assert not Path("static/icons/edubot-avatar.png").exists()
    assert "assistant-drone-avatar" in sources[0]
    assert "mascots/drone-directions.webp" in sources[0]


def test_floating_agent_opens_voice_call_separate_from_help_chat():
    mascot = Path("templates/_page_mascot.html").read_text(encoding="utf-8")
    help_widget = Path("templates/_asistente_widget.html").read_text(encoding="utf-8")
    assistant_script = Path("static/js/asistente.js").read_text(encoding="utf-8")
    assistant_styles = Path("static/css/edubot.css").read_text(encoding="utf-8")
    base_template = Path("templates/base.html").read_text(encoding="utf-8")
    home_template = Path("templates/index.html").read_text(encoding="utf-8")
    public_template = Path("templates/publico/base_publica.html").read_text(encoding="utf-8")
    app_script = Path("static/js/app.js").read_text(encoding="utf-8")
    native_activity = Path(
        "mobile-app/android/app/src/main/java/co/eduturnos/app/MainActivity.java"
    ).read_text(encoding="utf-8")
    calendar_route = Path("routes/integraciones_google.py").read_text(encoding="utf-8")
    calendar_template = Path("templates/integraciones_google.html").read_text(encoding="utf-8")

    assert "data-assistant-voice-launch" in mascot
    assert "data-assistant-voice-launch" in assistant_script
    assert "data-assistant-toggle data-assistant-open" in help_widget
    assert 'data-assistant-voice-toggle' not in help_widget
    assert 'data-assistant-call-toggle' in help_widget
    assert 'data-assistant-call role="dialog"' in help_widget
    assert 'data-assistant-public-call role="dialog"' in mascot
    assert "assistant-voice-call__avatar assistant-drone-avatar" in help_widget
    assert "assistant-voice-call__wave" in help_widget
    assert "assistant-voice-call__hangup" in help_widget
    assert "navigator.mediaDevices.getUserMedia" not in assistant_script
    assert "recognition.interimResults = true" in assistant_script
    assert "eduturnos-native-voice-partial-result" in assistant_script
    assert "data-assistant-call-transcript" in help_widget
    assert "data-assistant-public-transcript" in mascot
    assert "onresult" in assistant_script
    assert "onstart" in assistant_script
    assert "onspeechstart" in assistant_script
    assert "EDUTURNOSNativeVoice" in assistant_script
    assert "eduturnos-native-voice-result" in assistant_script
    assert "eduturnos-native-voice-partial-result" in native_activity
    assert "EXTRA_PARTIAL_RESULTS, true" in native_activity
    assert "eduturnos-native-voice-result" in native_activity
    assert "SpeechRecognizer" in native_activity
    assert "startSystemVoiceInput()" in native_activity
    assert "RecognizerIntent.ACTION_RECOGNIZE_SPEECH" in native_activity
    assert "spanishFemaleVoicePattern" in assistant_script
    assert "selectSpanishVoice()" in assistant_script
    assert "speakWithNativeVoice" in assistant_script
    assert "TextToSpeech" in native_activity
    assert "FEMALE_VOICE_NAME" in native_activity
    assert "stopSpeaking" in native_activity
    assert assistant_script.count("utterance.voice = selectSpanishVoice();") == 2
    assert "Manifest.permission.RECORD_AUDIO" in native_activity
    assert "callPanel.hidden = false" in assistant_script
    assert "positionCallNearLauncher(launcher)" in assistant_script
    assert "enableCallPanelControls(panel)" in assistant_script
    assert "enableCallPanelControls(callPanel)" in assistant_script
    assert "data-assistant-call-resize=\"nw\"" in help_widget
    assert "data-assistant-call-resize=\"se\"" in help_widget
    assert "data-assistant-call-action-link" in help_widget
    assert "data-assistant-call-confirm" in help_widget
    assert "window.confirm(`¿Confirmas cancelar la cita #${citaId}?" in assistant_script
    assert "actionForm.action = actionUrl" in assistant_script
    assert "data-assistant-call-resize=\"nw\"" in mascot
    assert "data-assistant-call-resize=\"se\"" in mascot
    assert "panel.setPointerCapture(event.pointerId)" in assistant_script
    assert "initialSize.width" in assistant_script
    assert "assistant-voice-call.is-dragging" in assistant_styles
    assert ".assistant-voice-call__resize-se" in assistant_styles
    assert "placeChatNearLauncher" not in assistant_script
    assert "setChatOpen(true, launcher" not in assistant_script
    assert "No se concedió permiso al micrófono" not in assistant_script
    assert "permiso de EDUTURNOS" in assistant_script
    assert "data-assistant-voice-view" not in help_widget
    assert help_widget.index("assistant-avatar assistant-drone-avatar") < help_widget.index("id=\"dashboard-help-title\"")
    assert "is-voice-mode" not in assistant_script
    assert ".dashboard-help-chat.is-voice-mode" not in assistant_styles
    assert ".assistant-voice-call" in assistant_styles
    assert ".page-mascot:active" in assistant_styles
    assert "background-color: transparent !important" in assistant_styles
    assert "animation: assistant-mark-float" not in assistant_styles
    assert "assistant-voice-controls" not in help_widget
    assert "_page_mascot_avatar.html" not in base_template
    assert "_page_mascot_avatar.html" not in home_template
    assert "_page_mascot_avatar.html" not in public_template
    assert "launcher.openAt(Number(link.dataset.calendarStart)" in app_script
    assert "launcher.openEvent(eventUrl)" in app_script
    assert "openEvent(String eventUrl)" in native_activity
    assert "setPackage(\"com.google.android.calendar\")" in native_activity
    manifest = Path(
        "mobile-app/android/app/src/main/AndroidManifest.xml"
    ).read_text(encoding="utf-8")
    android_build = Path("mobile-app/android/app/build.gradle").read_text(encoding="utf-8")
    assert 'android:name="android.permission.RECORD_AUDIO"' in manifest
    assert 'android.speech.RecognitionService' in manifest
    assert 'android.speech.action.RECOGNIZE_SPEECH' in manifest
    assert 'versionName "3.1.2"' in android_build
    assert 'versionCode 32' in android_build
    assert "data-calendar-event-url=\"{{ calendar_open_event_url or '' }}\"" in calendar_template
    assert "calendar_open_event_url=calendar_open_event_url" in calendar_route
    assert "icons/edubot.png" not in Path("templates/_asistente_widget.html").read_text(encoding="utf-8")


def test_creators_page_places_agent_profile_after_team_photos():
    from app import app as flask_app

    template = Path("templates/publico/creadores.html").read_text(encoding="utf-8")
    assert template.index('class="creadores-grid"') < template.index('class="creadores-edubot"')
    assert "mascots/drone-directions.webp" in template
    assert "Es el agente de orientación de la plataforma" in template

    response = flask_app.test_client().get("/creadores")
    assert response.status_code == 200
    assert response.data.index(b"Participantes de la creaci") < response.data.index(b"EDUBOT")
