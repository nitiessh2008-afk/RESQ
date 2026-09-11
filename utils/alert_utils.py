"""
alert_utils.py
---------------
- get_siren_bytes(): loads the siren wav for use with Streamlit's native
  st.audio(..., autoplay=True) - far more reliable than injecting audio
  via a JS iframe, which browsers usually block as not being a direct
  user gesture.
- browser_notification(): fires a Web Notification API popup.
- sos_button_css(): big pulsing SOS button + risk badges + alert-system
  (not dashboard) visual language, used across every phase.
"""

import streamlit.components.v1 as components


def get_siren_bytes(path="assets/alert_siren.wav"):
    try:
        with open(path, "rb") as f:
            return f.read()
    except FileNotFoundError:
        return None


def browser_notification(title="RESQ ALERT", message="Disaster risk detected."):
    """Injects JS to show a native OS/browser push notification (no audio here)."""
    js = f"""
    <script>
    if (window.Notification) {{
        if (Notification.permission === "granted") {{
            new Notification("{title}", {{ body: "{message}" }});
        }} else if (Notification.permission !== "denied") {{
            Notification.requestPermission().then(function(p) {{
                if (p === "granted") {{
                    new Notification("{title}", {{ body: "{message}" }});
                }}
            }});
        }}
    }}
    </script>
    """
    components.html(js, height=0, width=0)


def sos_button_css():
    return """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {padding-top: 1rem; padding-bottom: 2rem;}
    body {background-color: #050608;}

    .sos-btn {
        display: flex; align-items: center; justify-content: center;
        width: 100%; padding: 22px 10px; border-radius: 14px;
        background: linear-gradient(135deg, #ff1f1f, #8f0000);
        color: white !important; font-size: 28px; font-weight: 900;
        letter-spacing: 3px; text-align: center;
        animation: pulse-red 1.3s infinite;
        border: 2px solid #ff5b5b; cursor: pointer; text-decoration: none;
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
        background: #0c0e12; border: 1px solid #2b2f3a; border-left: 5px solid #444;
        border-radius: 10px; padding: 16px 18px; margin-bottom: 12px;
    }
    .resq-card.critical {border-left-color:#b30000;}
    .resq-card.high {border-left-color:#ff6a00;}
    .resq-card.moderate {border-left-color:#ffb800;}
    .resq-card.low {border-left-color:#1fa855;}

    .factor-row {display:flex; align-items:center; gap:8px; margin:4px 0; font-size:12.5px; color:#c7cbd6;}
    .factor-bar-bg {flex:1; background:#1a1d24; border-radius:6px; height:8px; overflow:hidden;}
    .factor-bar-fill {height:8px; border-radius:6px; background:linear-gradient(90deg,#ffb800,#ff1f1f);}

    .siren-banner {
        background: repeating-linear-gradient(45deg, #4a0000, #4a0000 12px, #2a0000 12px, #2a0000 24px);
        border: 2px solid #ff1f1f; border-radius: 10px; padding: 14px 18px;
        color: #ffdcdc; font-weight: 700; margin-bottom: 14px;
    }

    .prev-incident {color:#9aa2b1; font-size:12.5px; border-top:1px dashed #2b2f3a; margin-top:8px; padding-top:6px;}
    </style>
    """
