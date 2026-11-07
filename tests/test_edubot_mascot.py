from pathlib import Path


def test_edubot_mascot_is_shared_by_login_and_dashboard():
    login = Path("templates/auth/login.html").read_text(encoding="utf-8")
    dashboard = Path("templates/dashboard.html").read_text(encoding="utf-8")
    mascot = Path("templates/_edubot_mascot.html").read_text(encoding="utf-8")
    styles = Path("static/css/edubot-mascot.css").read_text(encoding="utf-8")
    script = Path("static/js/edubot-mascot.js").read_text(encoding="utf-8")

    assert "{% include '_edubot_mascot.html' %}" in login
    assert "{% include '_edubot_mascot.html' %}" in dashboard
    assert "css/edubot-mascot.css" in login
    assert "css/edubot-mascot.css" in dashboard
    assert "icons/edubot.png" in mascot
    assert Path("static/icons/edubot.png").is_file()
    assert "pointermove" in script
    assert "pointerdown" in script
    assert "prefers-reduced-motion" in script
    assert "prefers-reduced-motion" in styles
