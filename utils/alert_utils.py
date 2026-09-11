"""
alert_utils.py
---------------
Handles the "alert system" feel of RESQ:
  - Plays a unique siren sound (assets/alert_siren.wav) automatically.
  - Fires a browser push notification via the Web Notification API.
Both are injected as a small HTML/JS snippet through st.components.v1.html,
which keeps payload tiny -> works fine on low-bandwidth connections.
"""

import base64
import streamlit.components.v1 as components


def _load_audio_b64(path="assets/alert_siren.wav"):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def fire_alert(title="RESQ ALERT", message="Disaster risk detected.", play_sound=True, audio_path="assets/alert_siren.wav"):
    """Injects JS to show a browser notification + play the siren once."""
    audio_tag = ""
    if play_sound:
        try:
            b64 = _load_audio_b64(audio_path)
            audio_tag = f"""
            var audio = new Audio("data:audio/wav;base64,{b64}");
            audio.volume = 0.85;
            audio.play().catch(function(e){{console.log('autoplay blocked, user gesture needed', e);}});
            """
        except FileNotFoundError:
            audio_tag = ""

    js = f"""
    <script>
    {audio_tag}
    if (window.Notification) {{
        if (Notification.permission === "granted") {{
            new Notification("{title}", {{ body: "{message}", icon: "" }});
        }} else if (Notification.permission !== "denied") {{
            Notification.requestPermission().then(function(p) {{
                if (p === "granted") {{
                    new Notification("{title}", {{ body: "{message}", icon: "" }});
                }}
            }});
        }}
    }}
    </script>
    """
    components.html(js, height=0, width=0)


def sos_button_css():
    """Big pulsing SOS button CSS, injected once at app start."""
    return """
    <style>
    .sos-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        padding: 22px 10px;
        border-radius: 14px;
        background: linear-gradient(135deg, #ff1f1f, #b30000);
        color: white !important;
        font-size: 30px;
        font-weight: 900;
        letter-spacing: 3px;
        text-align: center;
        box-shadow: 0 0 0 rgba(255,0,0,0.6);
        animation: pulse-red 1.4s infinite;
        border: none;
        cursor: pointer;
        text-decoration: none;
    }
    @keyframes pulse-red {
        0%   { box-shadow: 0 0 0 0 rgba(255,0,0,0.55); }
        70%  { box-shadow: 0 0 0 22px rgba(255,0,0,0); }
        100% { box-shadow: 0 0 0 0 rgba(255,0,0,0); }
    }
    .risk-badge-critical {background:#b30000;color:#fff;padding:6px 14px;border-radius:20px;font-weight:800;}
    .risk-badge-high {background:#ff6a00;color:#fff;padding:6px 14px;border-radius:20px;font-weight:800;}
    .risk-badge-moderate {background:#ffb800;color:#111;padding:6px 14px;border-radius:20px;font-weight:800;}
    .risk-badge-low {background:#1fa855;color:#fff;padding:6px 14px;border-radius:20px;font-weight:800;}
    .resq-card {
        background: #0e1117;
        border: 1px solid #2b2f3a;
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 10px;
    }
    </style>
    """
