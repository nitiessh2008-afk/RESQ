"""
RESQ — AI-Powered Disaster Resource Allocation & Evacuation Hub
Smart India Hackathon | SIH 26206 - Student Innovation in Disaster Management

A single-file Streamlit application with two login roles (Citizen / Official),
a simulated AI photo-verification step, an official approval + dispatch
pipeline, and cross-session notifications. State that must be shared between
different people/devices (reports, inventory, dispatch log, notifications) is
persisted to a small JSON file on disk, so two browsers hitting the same
deployed app genuinely see each other's actions.

No external API keys required. Run with:  streamlit run disaster.py
"""

import base64
import hashlib
import io
import json
import os
import random
import time
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# ──────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RESQ | Disaster Response Hub",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ──────────────────────────────────────────────────────────────────────────
ZONE_NAMES = [
    "Kochi Backwaters – Ward 7", "Guwahati Riverside", "Chennai Coastal Belt",
    "Uttarakhand Hill Track – Sector 3", "Mumbai Low-Lying – Dharavi Edge",
    "Bhubaneswar Cyclone Corridor", "Patna Ganga Basin", "Srinagar Valley Rim",
]
BASE_COORDS = {
    "Kochi Backwaters – Ward 7": (9.9312, 76.2673),
    "Guwahati Riverside": (26.1445, 91.7362),
    "Chennai Coastal Belt": (13.0827, 80.2707),
    "Uttarakhand Hill Track – Sector 3": (30.0668, 79.0193),
    "Mumbai Low-Lying – Dharavi Edge": (19.0448, 72.8575),
    "Bhubaneswar Cyclone Corridor": (20.2961, 85.8245),
    "Patna Ganga Basin": (25.5941, 85.1376),
    "Srinagar Valley Rim": (34.0837, 74.7973),
}
DISASTER_TYPES = ["Flood", "Cyclone", "Landslide", "Earthquake Aftershock", "Flash Flood", "Fire", "Structural Collapse"]
SEVERITIES = ["Critical", "High", "Moderate", "Stable"]
SEVERITY_WEIGHTS = [0.2, 0.3, 0.3, 0.2]
RESOURCE_TYPES = ["Food Kits", "Medical Kits", "Rescue Boats", "Water (L)", "Tents", "Blankets"]
SOS_TYPES = ["Trapped / Stranded", "Medical Emergency", "Need Food/Water", "Need Shelter", "Missing Person", "Fire Hazard"]
RESOURCE_SUGGEST_BASE = {"Food Kits": 1.2, "Medical Kits": 0.4, "Water (L)": 3.0, "Tents": 0.3, "Blankets": 1.0, "Rescue Boats": 0.05}

STATUS_FLOW = ["Pending AI Verification", "AI Verified", "Approved", "Dispatched", "Delivered"]
STATUS_STYLE = {
    "Pending AI Verification": ("badge-moderate", "⏳"),
    "AI Verified":             ("badge-moderate", "🤖"),
    "Approved":                ("badge-info",     "✅"),
    "Dispatched":              ("badge-high",     "🚚"),
    "Delivered":               ("badge-stable",   "📦"),
    "Rejected":                ("badge-critical", "❌"),
}

# Mock official credentials for this prototype (no real auth backend).
OFFICIAL_CREDENTIALS = {
    "admin": "resq2026",
    "official1": "ndrf@123",
}

# ──────────────────────────────────────────────────────────────────────────
# SHARED STATE (JSON file on disk — visible to every browser/session hitting
# this same running app, which is what makes cross-device demo work).
# ──────────────────────────────────────────────────────────────────────────
STORE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resq_shared_store.json")


def _seed_inventory_dict():
    rng = np.random.default_rng(7)
    inv = {}
    for res in RESOURCE_TYPES:
        total = int(rng.integers(2000, 20000))
        allocated = int(total * rng.uniform(0.3, 0.85))
        inv[res] = {
            "Total Stock": total,
            "Allocated": allocated,
            "Available": total - allocated,
            "Depletion Rate (%/day)": round(float(rng.uniform(3, 18)), 1),
        }
    return inv


def _default_store():
    return {
        "reports": [],
        "dispatch_log": [],
        "inventory": _seed_inventory_dict(),
        "custom_zones": [],
    }


def _write_store(store):
    tmp_path = STORE_PATH + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(store, f, default=str)
    os.replace(tmp_path, STORE_PATH)


def load_store():
    if not os.path.exists(STORE_PATH):
        store = _default_store()
        _write_store(store)
        return store
    try:
        with open(STORE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        store = _default_store()
        _write_store(store)
        return store


def save_store(store):
    _write_store(store)


def new_ticket_id(store):
    existing = {r["id"] for r in store["reports"]}
    while True:
        tid = f"RESQ-{random.randint(10000, 99999)}"
        if tid not in existing:
            return tid


# ──────────────────────────────────────────────────────────────────────────
# MOCK DATA (deterministic — identical for every user, cheap to recompute)
# ──────────────────────────────────────────────────────────────────────────
@st.cache_data
def generate_zone_data(seed=42):
    rng = np.random.default_rng(seed)
    rows = []
    for zone in ZONE_NAMES:
        lat, lon = BASE_COORDS[zone]
        lat += rng.uniform(-0.05, 0.05)
        lon += rng.uniform(-0.05, 0.05)
        severity = rng.choice(SEVERITIES, p=SEVERITY_WEIGHTS)
        affected_pop = int(rng.integers(800, 42000))
        rescued = int(affected_pop * rng.uniform(0.15, 0.7))
        rows.append({
            "Zone": zone, "Disaster Type": rng.choice(DISASTER_TYPES[:5]), "Severity": severity,
            "Latitude": lat, "Longitude": lon, "Affected Population": affected_pop, "Rescued": rescued,
            "Active Distress Signals": int(rng.integers(0, 60)), "Shelters Active": int(rng.integers(1, 12)),
            "Last Updated": (datetime.now() - timedelta(minutes=int(rng.integers(1, 90)))).strftime("%H:%M:%S"),
            "Source": "Official Zone",
        })
    df = pd.DataFrame(rows)
    df["_rank"] = df["Severity"].map({"Critical": 0, "High": 1, "Moderate": 2, "Stable": 3})
    return df.sort_values("_rank").drop(columns="_rank").reset_index(drop=True)


@st.cache_data
def generate_trend_data():
    days = pd.date_range(end=datetime.now(), periods=14, freq="D")
    rng = np.random.default_rng(11)
    rows = []
    pop_base = 95000
    for i, d in enumerate(days):
        pop_base += rng.integers(-1500, 4500)
        pop_base = max(pop_base, 20000)
        for res in RESOURCE_TYPES:
            depletion = max(5, 100 - i * rng.uniform(4, 9) + rng.uniform(-5, 5))
            rows.append({"Date": d, "Affected Population": pop_base, "Resource": res, "Stock Remaining (%)": round(min(100, depletion), 1)})
    return pd.DataFrame(rows)


# ──────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────
def sev_badge(sev):
    cls_map = {"Critical": "badge-critical", "High": "badge-high", "Moderate": "badge-moderate", "Stable": "badge-stable"}
    return f'<span class="badge {cls_map.get(sev, "badge-stable")}">{sev.upper()}</span>'


def status_badge(status):
    cls, icon = STATUS_STYLE.get(status, ("badge-moderate", "•"))
    return f'<span class="badge {cls}">{icon} {status.upper()}</span>'


def sev_card_class(sev):
    return {"Critical": "zone-critical", "High": "zone-high", "Moderate": "zone-moderate", "Stable": "zone-stable"}.get(sev, "zone-stable")


def suggest_resources(people_count, emergency_type, resources_wanted):
    mult = 1.5 if emergency_type in ("Trapped / Stranded", "Need Shelter") else 1.0
    return {res: max(1, int(people_count * RESOURCE_SUGGEST_BASE.get(res, 0.5) * mult)) for res in resources_wanted}


def simulate_ai_verification(photo_bytes, emergency_type, details_text):
    """Deterministic pseudo-random 'AI' check — clearly a prototype simulation,
    not a trained model. Confidence/label derived from a hash so the same
    photo always yields the same read (feels consistent across reruns)."""
    if photo_bytes:
        h = int(hashlib.sha256(photo_bytes).hexdigest(), 16)
    else:
        h = int(hashlib.sha256((emergency_type + details_text + str(time.time())).encode()).hexdigest(), 16)
    confidence = 55 + (h % 40)  # 55–94
    mismatch = (h % 7 == 0)
    candidates = [t for t in DISASTER_TYPES if t != emergency_type]
    ai_label = random.Random(h).choice(candidates) if mismatch else emergency_type
    flag_review = confidence < 70 or photo_bytes is None
    return confidence, ai_label, flag_review


def dispatch_resource(store, zone, resource, qty, priority, note="", ticket_id=None):
    inv = store["inventory"][resource]
    qty_final = min(qty, inv["Available"])
    inv["Available"] -= qty_final
    inv["Allocated"] += qty_final
    store["dispatch_log"].insert(0, {
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Zone": zone, "Resource": resource,
        "Quantity": qty_final, "Priority": priority, "Status": "Dispatched ✅", "Note": note, "Ticket": ticket_id or "—",
    })
    return qty_final


def add_history(report, status, note=""):
    report["history"].append({"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "status": status, "note": note})
    report["status"] = status


def get_all_zones(store):
    base = generate_zone_data()
    custom = pd.DataFrame(store["custom_zones"]) if store["custom_zones"] else pd.DataFrame(columns=base.columns)
    if not custom.empty:
        custom = custom[base.columns]
    return pd.concat([base, custom], ignore_index=True)


def approved_reports_as_zones(store):
    rows = []
    for r in store["reports"]:
        if r["status"] in ("Approved", "Dispatched", "Delivered"):
            rows.append({
                "Zone": f"{r['location_name']} · {r['id']}", "Disaster Type": r["emergency_type"],
                "Severity": "Critical" if r["ai_confidence"] >= 85 else ("High" if r["ai_confidence"] >= 70 else "Moderate"),
                "Latitude": r["latitude"], "Longitude": r["longitude"], "Affected Population": r["people_count"],
                "Rescued": r["people_count"] if r["status"] == "Delivered" else 0,
                "Active Distress Signals": 0 if r["status"] == "Delivered" else 1,
                "Shelters Active": 0, "Last Updated": r["time"].split(" ")[-1], "Source": "Citizen Report",
            })
    cols = ["Zone", "Disaster Type", "Severity", "Latitude", "Longitude", "Affected Population", "Rescued", "Active Distress Signals", "Shelters Active", "Last Updated", "Source"]
    return pd.DataFrame(rows, columns=cols)


# ──────────────────────────────────────────────────────────────────────────
# THEME / CUSTOM CSS
# ──────────────────────────────────────────────────────────────────────────
LIGHT_CSS = """
<style>
:root{
    --bg-primary:#f4f6fa; --bg-card:#ffffff;
    --accent-red:#d9291c; --accent-red-bg:#ffe4e1;
    --accent-amber:#b8720a; --accent-amber-bg:#fff2d9;
    --accent-green:#127a3d; --accent-green-bg:#dff7e6;
    --accent-orange:#c8481a; --accent-orange-bg:#ffe6da;
    --accent-blue:#1d4ed8; --accent-blue-bg:#dfe8ff;
    --text-main:#12161f; --text-dim:#5b6473; --border-col:#dde2ea;
}
html, body, .stApp{background:var(--bg-primary)!important;color:var(--text-main)!important;}

section[data-testid="stSidebar"]{background:#ffffff;border-right:2px solid var(--border-col);}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] li,
section[data-testid="stSidebar"] span:not(.sg-sidebar-logo *),
section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"]:not(.sg-sidebar-logo *) {
    color:var(--text-main)!important;
}

h1,h2,h3,h4{color:var(--text-main)!important; font-family:'Segoe UI',sans-serif; font-weight:800!important;}
h1{font-size:36px!important;} h2{font-size:29px!important;} h3{font-size:23px!important;} h4{font-size:19px!important;}
p, label, li{font-size:17px;}
.stMarkdown p, .stCaption{font-size:17px!important;}

.stTabs [data-baseweb="tab-list"]{gap:6px;}
.stTabs [data-baseweb="tab"]{background:#eef1f6;border-radius:8px 8px 0 0;padding:10px 18px;color:var(--text-dim);font-weight:700;font-size:16px;}
.stTabs [aria-selected="true"]{background:var(--accent-red)!important;color:white!important;}
.stTabs [aria-selected="true"] p{color:white!important;}

.sg-sidebar-logo{
    background:linear-gradient(135deg, #d9291c 0%, #b8720a 100%);
    border-radius:14px;padding:18px 16px;margin-bottom:14px;
    box-shadow:0 4px 14px rgba(217,41,28,0.25);
}
.sg-sidebar-logo.sg-sidebar-logo *{color:#ffffff!important;}
.sg-sidebar-logo h2{font-size:23px!important;margin:0!important;}
.sg-sidebar-logo p{font-size:14px!important;opacity:0.95;margin:2px 0 0 0!important;}
.sg-sidebar-section{background:#f7f9fc;border:1.5px solid var(--border-col);border-radius:10px;padding:10px 12px;margin-top:10px;font-size:14px;}
.sg-sidebar-section.sg-sidebar-section *{color:var(--text-main)!important;}
.sg-sidebar-section b{font-size:15px;}
.sg-role-tag{display:inline-block;padding:4px 12px;border-radius:999px;font-size:12px;font-weight:800;background:var(--accent-blue-bg);color:var(--accent-blue)!important;}

.sg-banner{
    background:linear-gradient(90deg, #fff5f4 0%, #fff9ec 100%);
    border:2px solid var(--accent-red); border-radius:16px;padding:22px 28px;margin-bottom:22px;
    display:flex;align-items:center;justify-content:space-between;box-shadow:0 4px 18px rgba(217,41,28,0.10);
}
.sg-title{font-size:36px;font-weight:900;letter-spacing:0.3px;color:var(--text-main)!important;margin:0;}
.sg-subtitle{color:var(--text-dim)!important;font-size:16px;margin-top:4px;font-weight:600;}
.sg-live-pill.sg-live-pill{
    background:var(--accent-red);color:#ffffff!important;border:1px solid var(--accent-red);
    padding:7px 18px;border-radius:999px;font-size:14px;font-weight:800;animation:pulse 1.8s infinite;
}
.sg-live-pill.sg-live-pill-blue{background:var(--accent-blue);border-color:var(--accent-blue);}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(217,41,28,0.45);}70%{box-shadow:0 0 0 10px rgba(217,41,28,0);}100%{box-shadow:0 0 0 0 rgba(217,41,28,0);}}

.sg-card{background:var(--bg-card);border:2px solid var(--border-col);border-radius:14px;padding:18px 20px;margin-bottom:14px;box-shadow:0 2px 8px rgba(20,25,40,0.05);}
.sg-card h4{margin:0 0 8px 0;font-size:19px;color:var(--text-main)!important;font-weight:800;letter-spacing:0.2px;}
.sg-card, .sg-card span:not(.badge), .sg-card div:not(.badge){color:var(--text-main);}

.zone-critical{border-left:7px solid var(--accent-red); background:linear-gradient(90deg, var(--accent-red-bg) 0%, #fff 14%);}
.zone-high{border-left:7px solid var(--accent-orange); background:linear-gradient(90deg, var(--accent-orange-bg) 0%, #fff 14%);}
.zone-moderate{border-left:7px solid var(--accent-amber); background:linear-gradient(90deg, var(--accent-amber-bg) 0%, #fff 14%);}
.zone-stable{border-left:7px solid var(--accent-green); background:linear-gradient(90deg, var(--accent-green-bg) 0%, #fff 14%);}
.zone-info{border-left:7px solid var(--accent-blue); background:linear-gradient(90deg, var(--accent-blue-bg) 0%, #fff 14%);}

.badge{padding:6px 15px;border-radius:999px;font-size:14px;font-weight:800;display:inline-block;letter-spacing:0.3px;}
.badge.badge-critical{background:var(--accent-red);color:#ffffff!important;}
.badge.badge-high{background:var(--accent-orange);color:#ffffff!important;}
.badge.badge-moderate{background:var(--accent-amber);color:#ffffff!important;}
.badge.badge-stable{background:var(--accent-green);color:#ffffff!important;}
.badge.badge-info{background:var(--accent-blue);color:#ffffff!important;}

.stButton>button{border-radius:8px;font-weight:700;font-size:17px;border:1.5px solid var(--border-col);color:var(--text-main)!important;}
.stButton>button p{font-size:17px!important;color:var(--text-main)!important;}
.stButton>button[kind="primary"]{background:var(--accent-red);border-color:var(--accent-red);}
.stButton>button[kind="primary"], .stButton>button[kind="primary"] p{color:#ffffff!important;}

div[data-testid="stMetric"]{background:var(--bg-card);border:2px solid var(--border-col);border-radius:12px;padding:16px 18px;box-shadow:0 2px 8px rgba(20,25,40,0.05);}
div[data-testid="stMetricValue"]{font-size:30px!important;font-weight:900!important;}
div[data-testid="stMetricValue"], div[data-testid="stMetricValue"] *{color:var(--text-main)!important;}
div[data-testid="stMetricLabel"]{font-size:15px!important;font-weight:700!important;}
div[data-testid="stMetricLabel"], div[data-testid="stMetricLabel"] *{color:var(--text-dim)!important;}
div[data-testid="stMetricDelta"]{font-size:15px!important;font-weight:700!important;}
hr{border-color:var(--border-col);}
.footer-note{color:var(--text-dim)!important;font-size:14px;text-align:center;margin-top:30px;}

.sg-contact-card{background:#fff;border:2px solid var(--accent-red);border-radius:14px;padding:16px 18px;font-size:17px;line-height:2;}
.sg-contact-card, .sg-contact-card *{color:var(--text-main)!important;}

.sg-login-card{background:#fff;border:2px solid var(--border-col);border-radius:18px;padding:34px 36px;box-shadow:0 6px 24px rgba(20,25,40,0.08);max-width:520px;margin:0 auto;}
.sg-login-title{font-size:30px;font-weight:900;text-align:center;margin-bottom:4px;}
.sg-login-sub{text-align:center;color:var(--text-dim)!important;font-size:15px;margin-bottom:20px;}
.sg-timeline-step{display:flex;align-items:center;gap:10px;padding:6px 0;font-size:15px;}
.sg-timeline-dot{width:12px;height:12px;border-radius:50%;flex-shrink:0;}

[data-testid="stWidgetLabel"] p, [data-testid="stMarkdownContainer"] p, [data-testid="stCaptionContainer"] *,
[data-testid="stExpander"] p, [data-testid="stForm"] label p, div[data-baseweb="select"] *,
div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea, [data-testid="stThumbValue"],
[data-testid="stTickBarMin"], [data-testid="stTickBarMax"], [data-testid="stFileUploaderDropzoneInstructions"] *,
ul[role="listbox"] * { color:var(--text-main)!important; font-size:17px; }
[data-testid="stCaptionContainer"] *{color:var(--text-dim)!important; font-size:14px!important;}
::placeholder{color:var(--text-dim)!important; opacity:1;}

[data-testid="stAlertContentSuccess"], [data-testid="stAlertContentInfo"],
[data-testid="stAlertContentWarning"], [data-testid="stAlertContentError"] { font-size:16px!important; }

header[data-testid="stHeader"]{background:transparent!important; box-shadow:none!important;}
[data-testid="stToolbar"]{right:8px;}
[data-testid="stDataFrame"]{border:2px solid var(--border-col); border-radius:10px;}
[data-testid="stFileUploaderDropzone"]{background:#f7f9fc!important;border:2px dashed var(--border-col)!important;border-radius:12px;}
[data-testid="stExpander"]{border:2px solid var(--border-col)!important;border-radius:12px!important;background:#fff;}
</style>
"""
st.markdown(LIGHT_CSS, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────
# LOGIN GATE
# ──────────────────────────────────────────────────────────────────────────
if "role" not in st.session_state:
    st.session_state.role = None
if "my_tickets" not in st.session_state:
    st.session_state.my_tickets = []
if "official_seen_ts" not in st.session_state:
    st.session_state.official_seen_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if st.session_state.role is None:
    st.markdown(
        """
        <div style="text-align:center;margin:30px 0 20px 0;">
            <div style="font-size:44px;font-weight:900;">🚨 RESQ</div>
            <div style="color:#5b6473;font-size:16px;font-weight:600;">AI-Powered Disaster Resource Allocation & Evacuation Hub</div>
            <div style="color:#5b6473;font-size:13px;">SIH 26206 · Student Innovation in Disaster Management</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _, mid, _ = st.columns([1, 1.3, 1])
    with mid:
        st.markdown('<div class="sg-login-card">', unsafe_allow_html=True)
        tab_citizen, tab_official = st.tabs(["👤 Citizen Login", "🛡️ Official Login"])

        with tab_citizen:
            st.markdown('<p style="font-size:15px;color:#5b6473;margin-top:8px;">Report emergencies and track relief status. No password required.</p>', unsafe_allow_html=True)
            with st.form("citizen_login_form"):
                c_name = st.text_input("Your Name", placeholder="e.g. Rahul Verma")
                c_phone = st.text_input("Contact Number (optional)", placeholder="+91 98XXXXXXXX")
                c_submit = st.form_submit_button("Continue as Citizen →", use_container_width=True, type="primary")
            if c_submit:
                if c_name.strip():
                    st.session_state.role = "citizen"
                    st.session_state.citizen_name = c_name.strip()
                    st.session_state.citizen_phone = c_phone.strip()
                    st.rerun()
                else:
                    st.error("Please enter your name to continue.")

        with tab_official:
            st.markdown('<p style="font-size:15px;color:#5b6473;margin-top:8px;">Verify reports, approve, and dispatch relief resources.</p>', unsafe_allow_html=True)
            with st.form("official_login_form"):
                o_user = st.text_input("Username", placeholder="e.g. admin")
                o_pass = st.text_input("Password", type="password")
                o_submit = st.form_submit_button("Login as Official →", use_container_width=True, type="primary")
            if o_submit:
                if OFFICIAL_CREDENTIALS.get(o_user) == o_pass:
                    st.session_state.role = "official"
                    st.session_state.official_name = o_user
                    st.session_state.official_seen_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
            with st.expander("Demo credentials (for judges/testers)"):
                st.caption("admin / resq2026   ·   official1 / ndrf@123")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ──────────────────────────────────────────────────────────────────────────
# LOAD SHARED STATE (fresh from disk every run — this is what makes two
# different browsers/devices see each other's actions)
# ──────────────────────────────────────────────────────────────────────────
store = load_store()
trend_df = generate_trend_data()
role = st.session_state.role

pending_count = sum(1 for r in store["reports"] if r["status"] in ("Pending AI Verification", "AI Verified"))

# ──────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sg-sidebar-logo"><h2>🚨 RESQ</h2><p>SIH 26206 · Disaster Management</p></div>', unsafe_allow_html=True)

    if role == "citizen":
        st.markdown(f'<span class="sg-role-tag">👤 CITIZEN — {st.session_state.citizen_name}</span>', unsafe_allow_html=True)
        page_options = ["🗺️ Command Center & Live Map", "🆘 Citizen SOS Portal", "📈 Predictive Risk & Analytics"]
    else:
        st.markdown(f'<span class="sg-role-tag">🛡️ OFFICIAL — {st.session_state.official_name}</span>', unsafe_allow_html=True)
        badge_txt = f" ({pending_count} new)" if pending_count else ""
        page_options = [
            "🗺️ Command Center & Live Map",
            f"🛡️ Official Approval Queue{badge_txt}",
            "📦 Resource Allocation & Logistics",
            "📈 Predictive Risk & Analytics",
        ]

    st.markdown("#### 🧭 Navigate")
    page_raw = st.radio("Navigate", page_options, label_visibility="collapsed")
    page = page_raw.split(" (")[0]  # strip "(N new)" suffix if present

    st.markdown(
        f"""<div class="sg-sidebar-section"><b>🟢 System Status: Operational</b><br/>
        Last sync: {datetime.now().strftime('%H:%M:%S')}</div>""",
        unsafe_allow_html=True,
    )

    auto_refresh = st.checkbox("🔁 Auto-refresh every 15s", value=False, help="Reloads the page automatically so new reports/approvals from other devices show up without clicking Refresh.")
    if st.button("🔄 Refresh Now", use_container_width=True):
        st.rerun()

    if role == "official" and pending_count:
        st.markdown(
            f"""<div class="sg-sidebar-section" style="border-color:var(--accent-red);background:#fff5f4;">
            <b>🔔 {pending_count} report(s) awaiting review</b></div>""",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        for k in ["role", "citizen_name", "citizen_phone", "official_name", "my_tickets"]:
            st.session_state.pop(k, None)
        st.rerun()

if auto_refresh:
    st.markdown('<meta http-equiv="refresh" content="15">', unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────
# TOP BANNER
# ──────────────────────────────────────────────────────────────────────────
all_zones = get_all_zones(store)
citizen_zone_rows = approved_reports_as_zones(store)
combined_zones = pd.concat([all_zones, citizen_zone_rows], ignore_index=True) if not citizen_zone_rows.empty else all_zones
total_signals = int(combined_zones["Active Distress Signals"].sum())
active_critical = (combined_zones["Severity"] == "Critical").sum()

if role == "citizen":
    pill_html = f'<span class="sg-live-pill">● LIVE — {total_signals} active distress signals</span>'
    sub_html = f"{active_critical} zone(s) at CRITICAL severity"
else:
    pill_html = f'<span class="sg-live-pill sg-live-pill-blue">🔔 {pending_count} report(s) awaiting your review</span>'
    sub_html = f"{total_signals} active distress signals · {active_critical} zone(s) CRITICAL"

st.markdown(
    f"""
    <div class="sg-banner">
        <div>
            <p class="sg-title">🛡️ RESQ Command Dashboard</p>
            <p class="sg-subtitle">AI-Powered Disaster Resource Allocation & Evacuation Hub</p>
        </div>
        <div style="text-align:right;">{pill_html}<br/><span class="sg-subtitle">{sub_html}</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────
# PAGE: COMMAND CENTER & LIVE MAP  (both roles)
# ──────────────────────────────────────────────────────────────────────────
if page == "🗺️ Command Center & Live Map":
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Active Disaster Zones", len(combined_zones), delta=f"{active_critical} critical", delta_color="inverse")
    c2.metric("Total Affected Population", f"{combined_zones['Affected Population'].sum():,}")
    c3.metric("People Rescued", f"{combined_zones['Rescued'].sum():,}")
    c4.metric("Active Distress Signals", total_signals)

    st.markdown("### 🗺️ Live Disaster Zone Map")
    map_col, filter_col = st.columns([3, 1])
    with filter_col:
        sev_filter = st.multiselect("Filter by severity", SEVERITIES, default=SEVERITIES)
        show_labels = st.checkbox("Show zone size by population", value=True)
        basemap_choice = st.selectbox("Map style", ["Colorful (streets)", "Colorful (voyager)", "Minimal (light)"], index=0)
    filtered = combined_zones[combined_zones["Severity"].isin(sev_filter)] if sev_filter else combined_zones

    style_lookup = {"Colorful (streets)": "open-street-map", "Colorful (voyager)": "carto-voyager", "Minimal (light)": "carto-positron"}
    chosen_style = style_lookup[basemap_choice]
    color_map = {"Critical": "#d9291c", "High": "#c8481a", "Moderate": "#b8720a", "Stable": "#127a3d"}

    with map_col:
        if not filtered.empty:
            map_kwargs = dict(
                lat="Latitude", lon="Longitude", color="Severity",
                size="Affected Population" if show_labels else None, size_max=42, opacity=0.9,
                hover_name="Zone",
                hover_data={"Disaster Type": True, "Source": True, "Affected Population": True, "Active Distress Signals": True, "Latitude": False, "Longitude": False},
                color_discrete_map=color_map, category_orders={"Severity": ["Critical", "High", "Moderate", "Stable"]},
                zoom=3.6, height=500,
            )
            try:
                fig = px.scatter_map(filtered, **map_kwargs)
                fig.update_layout(map_style=chosen_style, map_center=dict(lat=22.5, lon=80), margin=dict(l=0, r=0, t=0, b=0),
                                   paper_bgcolor="rgba(0,0,0,0)", legend=dict(bgcolor="rgba(255,255,255,0.92)", bordercolor="#dde2ea", borderwidth=1, font=dict(color="#12161f", size=14)))
            except AttributeError:
                fallback_style = "carto-positron" if chosen_style == "carto-voyager" else chosen_style
                fig = px.scatter_mapbox(filtered, **map_kwargs)
                fig.update_layout(mapbox_style=fallback_style, mapbox_center=dict(lat=22.5, lon=80), margin=dict(l=0, r=0, t=0, b=0),
                                   paper_bgcolor="rgba(0,0,0,0)", legend=dict(bgcolor="rgba(255,255,255,0.92)", bordercolor="#dde2ea", borderwidth=1, font=dict(color="#12161f", size=14)))
            fig.update_traces(marker=dict(sizemin=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No zones match the selected filters.")

    st.markdown("### 📋 Zone Status Board")
    for _, row in filtered.iterrows():
        source_tag = ' <span class="badge badge-info">CITIZEN REPORT</span>' if row["Source"] == "Citizen Report" else ""
        st.markdown(
            f"""<div class="sg-card {sev_card_class(row['Severity'])}"><h4>{row['Zone']}{source_tag}</h4>
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div><b>{row['Disaster Type']}</b> {sev_badge(row['Severity'])}<br/>
                <span style="color:var(--text-dim);font-size:14px;">Affected: {row['Affected Population']:,} · Rescued: {row['Rescued']:,} ·
                Distress Signals: {row['Active Distress Signals']} · Shelters: {row['Shelters Active']}</span></div>
                <div style="text-align:right;color:var(--text-dim);font-size:12px;">Updated {row['Last Updated']}</div>
            </div></div>""",
            unsafe_allow_html=True,
        )

# ──────────────────────────────────────────────────────────────────────────
# PAGE: OFFICIAL APPROVAL QUEUE  (official only)
# ──────────────────────────────────────────────────────────────────────────
elif page == "🛡️ Official Approval Queue":
    st.markdown("### 🛡️ Official Approval Queue")
    st.caption("Every citizen SOS report lands here with a simulated AI verification pass. Review, adjust resource quantities, and approve or reject.")

    open_reports = [r for r in store["reports"] if r["status"] not in ("Delivered", "Rejected")]
    closed_reports = [r for r in store["reports"] if r["status"] in ("Delivered", "Rejected")]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Pending Review", sum(1 for r in store["reports"] if r["status"] in ("Pending AI Verification", "AI Verified")))
    m2.metric("Approved / In Progress", sum(1 for r in store["reports"] if r["status"] in ("Approved", "Dispatched")))
    m3.metric("Delivered", sum(1 for r in store["reports"] if r["status"] == "Delivered"))
    m4.metric("Rejected", sum(1 for r in store["reports"] if r["status"] == "Rejected"))

    if not open_reports:
        st.info("No open reports right now. New citizen SOS submissions will appear here automatically.")
    else:
        st.markdown(f"#### 📥 Open Reports ({len(open_reports)})")
        for r in open_reports:
            ai_flag = " ⚠️ Low confidence — manual review recommended" if r["ai_flag_review"] else ""
            with st.expander(f"{r['id']} · {r['location_name']} · {r['emergency_type']}  —  {r['status']}", expanded=(r["status"] == "Pending AI Verification")):
                col_a, col_b = st.columns([1.3, 1])
                with col_a:
                    st.markdown(status_badge(r["status"]), unsafe_allow_html=True)
                    st.markdown(f"**Reported by:** {r['citizen_name']} · {r.get('phone') or 'no phone given'}")
                    st.markdown(f"**People needing help:** {r['people_count']}")
                    st.markdown(f"**Details:** {r['details'] or '—'}")
                    st.markdown(f"**Location:** {r['location_name']} ({r['latitude']:.4f}, {r['longitude']:.4f}){' — *new/custom location*' if r['is_custom_location'] else ''}")
                    st.markdown(
                        f"**🤖 AI Verification (Prototype):** {r['ai_confidence']}% confidence · predicted type: *{r['ai_label']}*{ai_flag}",
                    )
                    if r.get("photo_b64"):
                        img_bytes = base64.b64decode(r["photo_b64"])
                        st.image(io.BytesIO(img_bytes), caption="Citizen-uploaded photo", width=280)
                    else:
                        st.caption("No photo was attached to this report.")

                with col_b:
                    st.markdown("**Resources to allocate**")
                    alloc = {}
                    for res, qty in r["requested_resources"].items():
                        alloc[res] = st.number_input(res, min_value=0, value=int(qty), step=5, key=f"alloc_{r['id']}_{res}")
                    add_as_zone = st.checkbox("Add this location as a permanent monitored zone", value=True, key=f"addzone_{r['id']}")
                    note = st.text_input("Note (optional)", key=f"note_{r['id']}")

                    btn_cols = st.columns(2)
                    if r["status"] in ("Pending AI Verification", "AI Verified"):
                        if btn_cols[0].button("✅ Approve & Dispatch", key=f"approve_{r['id']}", type="primary", use_container_width=True):
                            for res, qty in alloc.items():
                                if qty > 0:
                                    dispatch_resource(store, r["location_name"], res, qty, "Critical – Airlift", note, r["id"])
                            add_history(r, "Approved", note or "Approved by official")
                            if add_as_zone:
                                store["custom_zones"].append({
                                    "Zone": r["location_name"], "Disaster Type": r["emergency_type"], "Severity": "High",
                                    "Latitude": r["latitude"], "Longitude": r["longitude"], "Affected Population": r["people_count"],
                                    "Rescued": 0, "Active Distress Signals": 1, "Shelters Active": 0,
                                    "Last Updated": datetime.now().strftime("%H:%M:%S"), "Source": "Official Zone",
                                })
                            save_store(store)
                            st.rerun()
                        if btn_cols[1].button("❌ Reject", key=f"reject_{r['id']}", use_container_width=True):
                            add_history(r, "Rejected", note or "Rejected by official")
                            save_store(store)
                            st.rerun()
                    elif r["status"] == "Approved":
                        if st.button("🚚 Mark Dispatched", key=f"dispatch_{r['id']}", type="primary", use_container_width=True):
                            add_history(r, "Dispatched", note or "Resources en route")
                            save_store(store)
                            st.rerun()
                    elif r["status"] == "Dispatched":
                        if st.button("📦 Mark Delivered", key=f"deliver_{r['id']}", type="primary", use_container_width=True):
                            add_history(r, "Delivered", note or "Delivery confirmed")
                            save_store(store)
                            st.rerun()

    if closed_reports:
        with st.expander(f"📁 Closed reports ({len(closed_reports)})"):
            for r in closed_reports:
                st.markdown(f"**{r['id']}** · {r['location_name']} · {status_badge(r['status'])}", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────
# PAGE: RESOURCE ALLOCATION & LOGISTICS  (official only)
# ──────────────────────────────────────────────────────────────────────────
elif page == "📦 Resource Allocation & Logistics":
    inventory_df = pd.DataFrame([{"Resource": k, **v} for k, v in store["inventory"].items()])

    st.markdown("### 📦 Resource Inventory Overview")
    inv_cols = st.columns(len(RESOURCE_TYPES))
    for col, (_, r) in zip(inv_cols, inventory_df.iterrows()):
        pct_avail = r["Available"] / r["Total Stock"] * 100
        col.metric(r["Resource"], f"{r['Available']:,}", delta=f"{pct_avail:.0f}% available", delta_color="off")

    fig_inv = px.bar(inventory_df, x="Resource", y=["Allocated", "Available"], barmode="stack",
                      title="Stock Allocation by Resource Type", color_discrete_map={"Allocated": "#c8481a", "Available": "#127a3d"})
    fig_inv.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#12161f", size=14), legend_title_text="")
    st.plotly_chart(fig_inv, use_container_width=True)

    st.markdown("---")
    st.markdown("### 🚚 Smart Dispatch Calculator")
    st.caption("Manually allocate relief resources to any zone. Recommended quantity auto-scales with severity & affected population.")

    with st.form("dispatch_form"):
        f1, f2, f3 = st.columns(3)
        with f1:
            zone_choice = st.selectbox("Target Zone", all_zones["Zone"].tolist())
            zone_row = all_zones[all_zones["Zone"] == zone_choice].iloc[0]
        with f2:
            resource_choice = st.selectbox("Resource Type", RESOURCE_TYPES)
        with f3:
            priority = st.selectbox("Priority Level", ["Critical – Airlift", "High – Road Convoy", "Standard – Scheduled"])

        sev_multiplier = {"Critical": 3.5, "High": 2.2, "Moderate": 1.4, "Stable": 0.8}
        recommended_qty = int(zone_row["Affected Population"] * 0.02 * sev_multiplier[zone_row["Severity"]])
        recommended_qty = max(50, min(recommended_qty, 5000))
        qty = st.slider(f"Quantity to dispatch (AI-recommended: {recommended_qty:,})", min_value=10, max_value=6000, value=recommended_qty, step=10)
        note = st.text_area("Dispatch notes (optional)", placeholder="e.g. Route via NH-66, coordinate with local NDRF unit...")
        submitted = st.form_submit_button("🚀 Confirm & Dispatch", use_container_width=True)

    if submitted:
        available_stock = int(store["inventory"][resource_choice]["Available"])
        if qty > available_stock:
            st.warning(f"⚠️ Requested {qty:,} units of **{resource_choice}** exceeds available stock ({available_stock:,}). Dispatch capped to available stock.")
        qty_final = dispatch_resource(store, zone_choice, resource_choice, qty, priority, note)
        save_store(store)
        st.success(f"✅ Dispatched **{qty_final:,} units of {resource_choice}** to **{zone_choice}** with priority *{priority}*.")
        st.balloons()

    st.markdown("### 📜 Dispatch Log")
    if not store["dispatch_log"]:
        st.info("No dispatches recorded yet. Submit the form above to log one.")
    else:
        st.dataframe(pd.DataFrame(store["dispatch_log"]), use_container_width=True, hide_index=True)

# ──────────────────────────────────────────────────────────────────────────
# PAGE: CITIZEN SOS PORTAL  (citizen only)
# ──────────────────────────────────────────────────────────────────────────
elif page == "🆘 Citizen SOS Portal":
    st.markdown("### 🆘 Citizen Emergency Reporting")
    st.caption("Submit a report with your exact location and photo. It's automatically screened, then routed to an official for approval and dispatch.")

    if st.session_state.my_tickets:
        st.markdown("#### 🔔 Your Tracked Reports")
        for tid in st.session_state.my_tickets:
            match = next((r for r in store["reports"] if r["id"] == tid), None)
            if not match:
                continue
            st.markdown(
                f"""<div class="sg-card zone-info"><h4>{match['id']} — {match['location_name']} {status_badge(match['status'])}</h4>
                <span style="color:var(--text-dim);font-size:14px;">{match['history'][-1]['note'] if match['history'] else ''} · last update {match['history'][-1]['time'] if match['history'] else match['time']}</span>
                </div>""",
                unsafe_allow_html=True,
            )
        st.markdown("---")

    with st.expander("🔍 Track a report by Ticket ID (e.g. from another device)"):
        lookup_id = st.text_input("Ticket ID", placeholder="RESQ-83920")
        if lookup_id:
            match = next((r for r in store["reports"] if r["id"] == lookup_id.strip().upper()), None)
            if match:
                st.markdown(status_badge(match["status"]), unsafe_allow_html=True)
                for h in match["history"]:
                    st.markdown(f"- `{h['time']}` **{h['status']}** — {h['note']}")
            else:
                st.warning("No report found with that ticket ID.")

    left, right = st.columns([1.1, 1])
    with left:
        with st.form("sos_form", clear_on_submit=True):
            name = st.text_input("Your Name", value=st.session_state.citizen_name)
            phone = st.text_input("Contact Number (optional)", value=st.session_state.get("citizen_phone", ""))

            st.markdown("**Location**")
            zone_list = all_zones["Zone"].tolist()
            location_mode = st.radio("How do you want to set your location?", ["Select a known zone", "Enter a new/custom location"], horizontal=True)
            if location_mode == "Select a known zone":
                zone_sel = st.selectbox("Nearest Zone / Locality", zone_list)
                zone_row = all_zones[all_zones["Zone"] == zone_sel].iloc[0]
                loc_name, lat_val, lon_val, is_custom = zone_sel, float(zone_row["Latitude"]), float(zone_row["Longitude"]), False
            else:
                loc_name = st.text_input("Location name / landmark", placeholder="e.g. Sector 12 Market, near river bridge")
                lc1, lc2 = st.columns(2)
                lat_val = lc1.number_input("Latitude", value=22.5, format="%.4f", help="Tip: long-press your spot in Google Maps to get exact coordinates.")
                lon_val = lc2.number_input("Longitude", value=80.0, format="%.4f")
                is_custom = True

            emergency_type = st.selectbox("Emergency Type", SOS_TYPES)
            people_count = st.slider("Number of people needing help", 1, 50, 1)
            details = st.text_area("Additional details", placeholder="Describe your situation, landmark, floor number, etc.")
            resources_wanted = st.multiselect("Resources most needed", RESOURCE_TYPES, default=["Food Kits", "Water (L)"])
            photo = st.file_uploader("📷 Upload a photo of the situation (optional, helps AI + official verification)", type=["png", "jpg", "jpeg"])
            gps_sim = st.checkbox("📍 Attach exact GPS with this report", value=True)
            sos_submit = st.form_submit_button("🆘 SEND SOS ALERT", use_container_width=True, type="primary")

        if sos_submit:
            if location_mode == "Enter a new/custom location" and not loc_name.strip():
                st.error("Please enter a location name for your custom location.")
            else:
                photo_bytes = photo.getvalue() if photo is not None else None
                confidence, ai_label, flag_review = simulate_ai_verification(photo_bytes, emergency_type, details or "")
                ticket_id = new_ticket_id(store)
                report = {
                    "id": ticket_id, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "citizen_name": name or "Anonymous", "phone": phone,
                    "location_name": loc_name, "is_custom_location": is_custom,
                    "latitude": lat_val + (random.uniform(-0.01, 0.01) if gps_sim else 0),
                    "longitude": lon_val + (random.uniform(-0.01, 0.01) if gps_sim else 0),
                    "emergency_type": emergency_type, "people_count": people_count, "details": details,
                    "requested_resources": suggest_resources(people_count, emergency_type, resources_wanted),
                    "photo_b64": base64.b64encode(photo_bytes).decode() if photo_bytes else None,
                    "ai_confidence": confidence, "ai_label": ai_label, "ai_flag_review": flag_review,
                    "status": "AI Verified" if not flag_review else "Pending AI Verification",
                    "history": [],
                }
                add_history(report, report["status"], "AI screening complete" if not flag_review else "Flagged for manual review — low confidence or no photo")
                store["reports"].insert(0, report)
                save_store(store)
                st.session_state.my_tickets.insert(0, ticket_id)

                st.success(f"✅ SOS Alert sent! Your ticket ID is **{ticket_id}** — save this to track status. An official has been notified.")
                st.info(f"🤖 AI Verification (Prototype): {confidence}% confidence · predicted type: {ai_label}" + (" — flagged for manual review." if flag_review else "."))
                if gps_sim:
                    st.info(f"📍 GPS attached: {report['latitude']:.4f}, {report['longitude']:.4f}")
                if photo_bytes:
                    st.image(io.BytesIO(photo_bytes), caption="Uploaded situation photo", width=320)
                st.toast("Emergency responders alerted!", icon="🚨")

    with right:
        st.markdown("#### 📞 Quick Emergency Contacts")
        st.markdown(
            """<div class="sg-contact-card">🚑 <b>National Disaster Helpline:</b> 1078<br/>
            👮 <b>Police:</b> 112<br/>🚒 <b>Fire:</b> 101<br/>🏥 <b>Ambulance:</b> 108<br/>
            🌊 <b>NDRF Control Room:</b> 011-24363260</div>""",
            unsafe_allow_html=True,
        )
        st.markdown("#### 🕒 Recent Reports (all citizens)")
        if not store["reports"]:
            st.info("No SOS reports submitted yet. Use the form to file one.")
        else:
            recent = pd.DataFrame(store["reports"][:10])[["id", "time", "location_name", "emergency_type", "status"]]
            recent.columns = ["Ticket", "Time", "Location", "Type", "Status"]
            st.dataframe(recent, use_container_width=True, hide_index=True, height=300)

    st.markdown("---")
    st.markdown("### 🌍 All-Zone Distress Signal Snapshot")
    fig_sos = px.bar(combined_zones.sort_values("Active Distress Signals", ascending=True), x="Active Distress Signals", y="Zone", orientation="h",
                      color="Severity", color_discrete_map={"Critical": "#d9291c", "High": "#c8481a", "Moderate": "#b8720a", "Stable": "#127a3d"},
                      title="Active Distress Signals by Zone")
    fig_sos.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#12161f", size=14))
    st.plotly_chart(fig_sos, use_container_width=True)

# ──────────────────────────────────────────────────────────────────────────
# PAGE: PREDICTIVE RISK & ANALYTICS  (both roles)
# ──────────────────────────────────────────────────────────────────────────
elif page == "📈 Predictive Risk & Analytics":
    st.markdown("### 📈 Predictive Risk & Analytics")
    st.caption("14-day trend simulation of affected population and resource depletion, used to forecast restocking needs.")

    t1, t2 = st.columns([2, 1])
    with t1:
        pop_trend = trend_df.drop_duplicates(subset="Date")[["Date", "Affected Population"]]
        fig_pop = px.area(pop_trend, x="Date", y="Affected Population", title="Affected Population Trend (14 Days)", color_discrete_sequence=["#d9291c"])
        fig_pop.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#12161f", size=14))
        st.plotly_chart(fig_pop, use_container_width=True)
    with t2:
        st.markdown("#### 🔮 7-Day Forecast")
        last_pop = int(pop_trend["Affected Population"].iloc[-1])
        proj_growth = st.slider("Assumed daily growth rate (%)", -5.0, 10.0, 2.5, 0.5)
        forecast_pop = int(last_pop * ((1 + proj_growth / 100) ** 7))
        st.metric("Projected population affected (Day +7)", f"{forecast_pop:,}", delta=f"{forecast_pop - last_pop:+,}")
        risk_level = "🔴 High" if proj_growth > 5 else ("🟡 Moderate" if proj_growth > 0 else "🟢 Low")
        st.metric("Escalation Risk", risk_level)

    st.markdown("### 🧯 Resource Depletion Forecast")
    resource_pick = st.multiselect("Select resources to compare", RESOURCE_TYPES, default=["Medical Kits", "Water (L)", "Food Kits"])
    dep_data = trend_df[trend_df["Resource"].isin(resource_pick)] if resource_pick else trend_df
    if not dep_data.empty:
        fig_dep = px.line(dep_data, x="Date", y="Stock Remaining (%)", color="Resource", markers=True, title="Projected Stock Remaining Over Time")
        fig_dep.add_hline(y=20, line_dash="dash", line_color="#d9291c", annotation_text="Critical Threshold (20%)")
        fig_dep.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#12161f", size=14))
        st.plotly_chart(fig_dep, use_container_width=True)
    else:
        st.info("Select at least one resource to view the depletion forecast.")

    st.markdown("### 🎯 Zone Risk Matrix")
    risk_fig = px.scatter(combined_zones, x="Affected Population", y="Active Distress Signals", size="Rescued", color="Severity", text="Zone",
                           color_discrete_map={"Critical": "#d9291c", "High": "#c8481a", "Moderate": "#b8720a", "Stable": "#127a3d"},
                           title="Risk Matrix — Population vs. Active Distress Signals")
    risk_fig.update_traces(textposition="top center", textfont=dict(size=11, color="#5b6473"))
    risk_fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#12161f", size=14), height=480)
    st.plotly_chart(risk_fig, use_container_width=True)

    with st.expander("📊 View Raw Zone & Inventory Data"):
        st.markdown("**Zone Data**")
        st.dataframe(combined_zones, use_container_width=True, hide_index=True)
        st.markdown("**Inventory Data**")
        st.dataframe(pd.DataFrame([{"Resource": k, **v} for k, v in store["inventory"].items()]), use_container_width=True, hide_index=True)

# ──────────────────────────────────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────────────────────────────────
st.markdown(
    """<p class="footer-note">RESQ · Prototype for Smart India Hackathon (SIH 26206) — Student Innovation in Disaster Management.<br/>
    AI verification is a simulated prototype module. All data shown is mock/demo data.</p>""",
    unsafe_allow_html=True,
)
