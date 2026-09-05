"""
RESQ — AI-Powered Disaster Resource Allocation & Evacuation Hub
Smart India Hackathon | SIH 26206 - Student Innovation in Disaster Management

A single-file Streamlit application. Fully self-contained mock data —
no external API keys required.

Run with:  streamlit run surgeguard_app.py
"""

import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
# THEME / CUSTOM CSS  (bold white "command center" theme)
# ──────────────────────────────────────────────────────────────────────────
LIGHT_CSS = """
<style>
:root{
    --bg-primary:#f4f6fa;
    --bg-card:#ffffff;
    --accent-red:#d9291c;
    --accent-red-bg:#ffe4e1;
    --accent-amber:#b8720a;
    --accent-amber-bg:#fff2d9;
    --accent-green:#127a3d;
    --accent-green-bg:#dff7e6;
    --accent-orange:#c8481a;
    --accent-orange-bg:#ffe6da;
    --accent-blue:#1d4ed8;
    --text-main:#12161f;
    --text-dim:#5b6473;
    --border-col:#dde2ea;
}
html, body, .stApp{background:var(--bg-primary)!important;color:var(--text-main)!important;}

/* ── Sidebar: force dark text EXCEPT inside the colored logo block ── */
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

/* Sidebar logo block — colored bg needs its own text color, kept high-specificity */
.sg-sidebar-logo{
    background:linear-gradient(135deg, #d9291c 0%, #b8720a 100%);
    border-radius:14px;padding:18px 16px;margin-bottom:14px;
    box-shadow:0 4px 14px rgba(217,41,28,0.25);
}
.sg-sidebar-logo.sg-sidebar-logo *{color:#ffffff!important;}
.sg-sidebar-logo h2{font-size:23px!important;margin:0!important;}
.sg-sidebar-logo p{font-size:14px!important;opacity:0.95;margin:2px 0 0 0!important;}
.sg-sidebar-section{
    background:#f7f9fc;border:1.5px solid var(--border-col);border-radius:10px;
    padding:10px 12px;margin-top:10px;font-size:14px;
}
.sg-sidebar-section.sg-sidebar-section *{color:var(--text-main)!important;}
.sg-sidebar-section b{font-size:15px;}

.sg-banner{
    background:linear-gradient(90deg, #fff5f4 0%, #fff9ec 100%);
    border:2px solid var(--accent-red);
    border-radius:16px;padding:22px 28px;margin-bottom:22px;
    display:flex;align-items:center;justify-content:space-between;
    box-shadow:0 4px 18px rgba(217,41,28,0.10);
}
.sg-title{font-size:36px;font-weight:900;letter-spacing:0.3px;color:var(--text-main)!important;margin:0;}
.sg-subtitle{color:var(--text-dim)!important;font-size:16px;margin-top:4px;font-weight:600;}
.sg-live-pill.sg-live-pill{
    background:var(--accent-red);color:#ffffff!important;border:1px solid var(--accent-red);
    padding:7px 18px;border-radius:999px;font-size:14px;font-weight:800;
    animation:pulse 1.8s infinite;
}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(217,41,28,0.45);}70%{box-shadow:0 0 0 10px rgba(217,41,28,0);}100%{box-shadow:0 0 0 0 rgba(217,41,28,0);}}

.sg-card{
    background:var(--bg-card);border:2px solid var(--border-col);border-radius:14px;
    padding:18px 20px;margin-bottom:14px;box-shadow:0 2px 8px rgba(20,25,40,0.05);
}
.sg-card h4{margin:0 0 8px 0;font-size:19px;color:var(--text-main)!important;font-weight:800;letter-spacing:0.2px;}
.sg-card, .sg-card span:not(.badge), .sg-card div:not(.badge){color:var(--text-main);}

.zone-critical{border-left:7px solid var(--accent-red); background:linear-gradient(90deg, var(--accent-red-bg) 0%, #fff 14%);}
.zone-high{border-left:7px solid var(--accent-orange); background:linear-gradient(90deg, var(--accent-orange-bg) 0%, #fff 14%);}
.zone-moderate{border-left:7px solid var(--accent-amber); background:linear-gradient(90deg, var(--accent-amber-bg) 0%, #fff 14%);}
.zone-stable{border-left:7px solid var(--accent-green); background:linear-gradient(90deg, var(--accent-green-bg) 0%, #fff 14%);}

.badge{padding:6px 15px;border-radius:999px;font-size:14px;font-weight:800;display:inline-block;letter-spacing:0.3px;}
.badge.badge-critical{background:var(--accent-red);color:#ffffff!important;}
.badge.badge-high{background:var(--accent-orange);color:#ffffff!important;}
.badge.badge-moderate{background:var(--accent-amber);color:#ffffff!important;}
.badge.badge-stable{background:var(--accent-green);color:#ffffff!important;}

.stButton>button{
    border-radius:8px;font-weight:700;font-size:17px;border:1.5px solid var(--border-col);color:var(--text-main)!important;
}
.stButton>button p{font-size:17px!important;color:var(--text-main)!important;}
.stButton>button[kind="primary"]{background:var(--accent-red);border-color:var(--accent-red);}
.stButton>button[kind="primary"], .stButton>button[kind="primary"] p{color:#ffffff!important;}

div[data-testid="stMetric"]{
    background:var(--bg-card);border:2px solid var(--border-col);border-radius:12px;padding:16px 18px;
    box-shadow:0 2px 8px rgba(20,25,40,0.05);
}
div[data-testid="stMetricValue"]{font-size:30px!important;font-weight:900!important;}
div[data-testid="stMetricValue"], div[data-testid="stMetricValue"] *{color:var(--text-main)!important;}
div[data-testid="stMetricLabel"]{font-size:15px!important;font-weight:700!important;}
div[data-testid="stMetricLabel"], div[data-testid="stMetricLabel"] *{color:var(--text-dim)!important;}
div[data-testid="stMetricDelta"]{font-size:15px!important;font-weight:700!important;}
hr{border-color:var(--border-col);}
.footer-note{color:var(--text-dim)!important;font-size:14px;text-align:center;margin-top:30px;}

/* Quick-contact card */
.sg-contact-card{background:#fff;border:2px solid var(--accent-red);border-radius:14px;padding:16px 18px;font-size:17px;line-height:2;}
.sg-contact-card, .sg-contact-card *{color:var(--text-main)!important;}

/* ── Streamlit widget internals: force readable dark text (scoped to real
   Streamlit component testids, never touching our own sg-/badge- classes) ── */
[data-testid="stWidgetLabel"] p,
[data-testid="stMarkdownContainer"] p,
[data-testid="stCaptionContainer"] *,
[data-testid="stExpander"] p,
[data-testid="stForm"] label p,
div[data-baseweb="select"] *,
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea,
[data-testid="stThumbValue"],
[data-testid="stTickBarMin"], [data-testid="stTickBarMax"],
[data-testid="stFileUploaderDropzoneInstructions"] *,
ul[role="listbox"] * {
    color:var(--text-main)!important;
    font-size:17px;
}
[data-testid="stCaptionContainer"] *{color:var(--text-dim)!important; font-size:14px!important;}
::placeholder{color:var(--text-dim)!important; opacity:1;}

[data-testid="stAlertContentSuccess"], [data-testid="stAlertContentInfo"],
[data-testid="stAlertContentWarning"], [data-testid="stAlertContentError"] { font-size:16px!important; }

/* Hide the default black Streamlit top header bar for a cleaner, uninterrupted look */
header[data-testid="stHeader"]{background:transparent!important; box-shadow:none!important;}
[data-testid="stToolbar"]{right:8px;}

/* Dataframes/tables: keep readable on white */
[data-testid="stDataFrame"]{border:2px solid var(--border-col); border-radius:10px;}

/* File uploader box styling */
[data-testid="stFileUploaderDropzone"]{
    background:#f7f9fc!important;border:2px dashed var(--border-col)!important;border-radius:12px;
}
</style>
"""
st.markdown(LIGHT_CSS, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────
# MOCK DATA GENERATION (cached in session state so it feels "live" but stable)
# ──────────────────────────────────────────────────────────────────────────
ZONE_NAMES = [
    "Kochi Backwaters – Ward 7", "Guwahati Riverside", "Chennai Coastal Belt",
    "Uttarakhand Hill Track – Sector 3", "Mumbai Low-Lying – Dharavi Edge",
    "Bhubaneswar Cyclone Corridor", "Patna Ganga Basin", "Srinagar Valley Rim",
]

DISASTER_TYPES = ["Flood", "Cyclone", "Landslide", "Earthquake Aftershock", "Flash Flood"]
SEVERITIES = ["Critical", "High", "Moderate", "Stable"]
SEVERITY_WEIGHTS = [0.2, 0.3, 0.3, 0.2]
RESOURCE_TYPES = ["Food Kits", "Medical Kits", "Rescue Boats", "Water (L)", "Tents", "Blankets"]
SOS_TYPES = ["Trapped / Stranded", "Medical Emergency", "Need Food/Water", "Need Shelter", "Missing Person", "Fire Hazard"]


def _severity_rank(sev):
    order = {"Critical": 0, "High": 1, "Moderate": 2, "Stable": 3}
    return order.get(sev, 4)


@st.cache_data
def generate_zone_data(seed=42):
    rng = np.random.default_rng(seed)
    base_coords = {
        "Kochi Backwaters – Ward 7": (9.9312, 76.2673),
        "Guwahati Riverside": (26.1445, 91.7362),
        "Chennai Coastal Belt": (13.0827, 80.2707),
        "Uttarakhand Hill Track – Sector 3": (30.0668, 79.0193),
        "Mumbai Low-Lying – Dharavi Edge": (19.0448, 72.8575),
        "Bhubaneswar Cyclone Corridor": (20.2961, 85.8245),
        "Patna Ganga Basin": (25.5941, 85.1376),
        "Srinagar Valley Rim": (34.0837, 74.7973),
    }
    rows = []
    for zone in ZONE_NAMES:
        lat, lon = base_coords[zone]
        lat += rng.uniform(-0.05, 0.05)
        lon += rng.uniform(-0.05, 0.05)
        severity = rng.choice(SEVERITIES, p=SEVERITY_WEIGHTS)
        affected_pop = int(rng.integers(800, 42000))
        rescued = int(affected_pop * rng.uniform(0.15, 0.7))
        rows.append({
            "Zone": zone,
            "Disaster Type": rng.choice(DISASTER_TYPES),
            "Severity": severity,
            "Latitude": lat,
            "Longitude": lon,
            "Affected Population": affected_pop,
            "Rescued": rescued,
            "Active Distress Signals": int(rng.integers(0, 60)),
            "Shelters Active": int(rng.integers(1, 12)),
            "Last Updated": (datetime.now() - timedelta(minutes=int(rng.integers(1, 90)))).strftime("%H:%M:%S"),
        })
    df = pd.DataFrame(rows)
    df["_rank"] = df["Severity"].apply(_severity_rank)
    df = df.sort_values("_rank").drop(columns="_rank").reset_index(drop=True)
    return df


@st.cache_data
def generate_inventory():
    rng = np.random.default_rng(7)
    data = []
    for res in RESOURCE_TYPES:
        total = int(rng.integers(2000, 20000))
        allocated = int(total * rng.uniform(0.3, 0.85))
        data.append({
            "Resource": res,
            "Total Stock": total,
            "Allocated": allocated,
            "Available": total - allocated,
            "Depletion Rate (%/day)": round(rng.uniform(3, 18), 1),
        })
    return pd.DataFrame(data)


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
            rows.append({
                "Date": d,
                "Affected Population": pop_base,
                "Resource": res,
                "Stock Remaining (%)": round(min(100, depletion), 1),
            })
    return pd.DataFrame(rows)


def sev_badge(sev):
    cls_map = {"Critical": "badge-critical", "High": "badge-high", "Moderate": "badge-moderate", "Stable": "badge-stable"}
    return f'<span class="badge {cls_map.get(sev, "badge-stable")}">{sev.upper()}</span>'


def sev_card_class(sev):
    cls_map = {"Critical": "zone-critical", "High": "zone-high", "Moderate": "zone-moderate", "Stable": "zone-stable"}
    return cls_map.get(sev, "zone-stable")


# ──────────────────────────────────────────────────────────────────────────
# SESSION STATE INIT
# ──────────────────────────────────────────────────────────────────────────
if "zones_df" not in st.session_state:
    st.session_state.zones_df = generate_zone_data()
if "inventory_df" not in st.session_state:
    st.session_state.inventory_df = generate_inventory()
if "trend_df" not in st.session_state:
    st.session_state.trend_df = generate_trend_data()
if "sos_log" not in st.session_state:
    st.session_state.sos_log = pd.DataFrame(columns=["Time", "Name", "Zone", "Emergency Type", "Details", "Photo Attached", "Status"])
if "dispatch_log" not in st.session_state:
    st.session_state.dispatch_log = pd.DataFrame(columns=["Time", "Zone", "Resource", "Quantity", "Priority", "Status"])

# ──────────────────────────────────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ──────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div class="sg-sidebar-logo">
            <h2>🚨 RESQ</h2>
            <p>SIH 26206 · Disaster Management</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("#### 🧭 Navigate")
    page = st.radio(
        "Navigate",
        [
            "🗺️ Command Center & Live Map",
            "📦 Resource Allocation & Logistics",
            "🆘 Citizen SOS Portal",
            "📈 Predictive Risk & Analytics",
        ],
        label_visibility="collapsed",
    )

    st.markdown(
        f"""
        <div class="sg-sidebar-section">
            <b>🟢 System Status: Operational</b><br/>
            All systems operational<br/>
            Last sync: {datetime.now().strftime('%H:%M:%S')}
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("🔄 Refresh Live Feed", use_container_width=True):
        st.cache_data.clear()
        for key in ["zones_df", "inventory_df", "trend_df"]:
            del st.session_state[key]
        st.rerun()

    st.markdown(
        """
        <div class="sg-sidebar-section">
            <b>📊 Quick Snapshot</b><br/>
            Built for Smart India Hackathon<br/>
            Team RESQ
        </div>
        """,
        unsafe_allow_html=True,
    )

zones_df = st.session_state.zones_df
inventory_df = st.session_state.inventory_df
trend_df = st.session_state.trend_df

# ──────────────────────────────────────────────────────────────────────────
# TOP BANNER
# ──────────────────────────────────────────────────────────────────────────
active_critical = (zones_df["Severity"] == "Critical").sum()
total_signals = int(zones_df["Active Distress Signals"].sum())
st.markdown(
    f"""
    <div class="sg-banner">
        <div>
            <p class="sg-title">🛡️ RESQ Command Dashboard</p>
            <p class="sg-subtitle">AI-Powered Disaster Resource Allocation & Evacuation Hub</p>
        </div>
        <div style="text-align:right;">
            <span class="sg-live-pill">● LIVE — {total_signals} active distress signals</span><br/>
            <span class="sg-subtitle">{active_critical} zone(s) at CRITICAL severity</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────
# PAGE 1: COMMAND CENTER & LIVE MAP
# ──────────────────────────────────────────────────────────────────────────
if page == "🗺️ Command Center & Live Map":
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Active Disaster Zones", len(zones_df), delta=f"{active_critical} critical", delta_color="inverse")
    c2.metric("Total Affected Population", f"{zones_df['Affected Population'].sum():,}", delta="+2,340 today", delta_color="inverse")
    c3.metric("People Rescued", f"{zones_df['Rescued'].sum():,}", delta="+512 today")
    c4.metric("Active Distress Signals", total_signals, delta=f"{int(total_signals*0.12)} new", delta_color="inverse")

    st.markdown("### 🗺️ Live Disaster Zone Map")
    map_col, filter_col = st.columns([3, 1])
    with filter_col:
        sev_filter = st.multiselect("Filter by severity", SEVERITIES, default=SEVERITIES)
        show_labels = st.checkbox("Show zone size by population", value=True)
        basemap_choice = st.selectbox("Map style", ["Colorful (streets)", "Colorful (voyager)", "Minimal (light)"], index=0)
    filtered = zones_df[zones_df["Severity"].isin(sev_filter)] if sev_filter else zones_df

    style_lookup = {
        "Colorful (streets)": "open-street-map",
        "Colorful (voyager)": "carto-voyager",
        "Minimal (light)": "carto-positron",
    }
    chosen_style = style_lookup[basemap_choice]

    color_map = {"Critical": "#d9291c", "High": "#c8481a", "Moderate": "#b8720a", "Stable": "#127a3d"}
    with map_col:
        if not filtered.empty:
            map_kwargs = dict(
                lat="Latitude", lon="Longitude",
                color="Severity",
                size="Affected Population" if show_labels else None,
                size_max=42,
                opacity=0.9,
                hover_name="Zone",
                hover_data={"Disaster Type": True, "Affected Population": True, "Active Distress Signals": True, "Latitude": False, "Longitude": False},
                color_discrete_map=color_map,
                category_orders={"Severity": ["Critical", "High", "Moderate", "Stable"]},
                zoom=3.6, height=500,
            )
            # Newer Plotly (>=5.24) renamed scatter_mapbox -> scatter_map and dropped
            # the mapbox_* layout prefix in favor of map_*. Support both so this
            # runs regardless of the installed Plotly version. Both styles work
            # without a Mapbox token (open-street-map / carto-positron / satellite-streets
            # are all token-free tile sources).
            try:
                fig = px.scatter_map(filtered, **map_kwargs)
                fig.update_layout(
                    map_style=chosen_style,
                    map_center=dict(lat=22.5, lon=80),
                    margin=dict(l=0, r=0, t=0, b=0),
                    paper_bgcolor="rgba(0,0,0,0)",
                    legend=dict(bgcolor="rgba(255,255,255,0.92)", bordercolor="#dde2ea", borderwidth=1, font=dict(color="#12161f", size=14)),
                )
            except AttributeError:
                fallback_style = "carto-positron" if chosen_style == "carto-voyager" else chosen_style
                fig = px.scatter_mapbox(filtered, **map_kwargs)
                fig.update_layout(
                    mapbox_style=fallback_style,
                    mapbox_center=dict(lat=22.5, lon=80),
                    margin=dict(l=0, r=0, t=0, b=0),
                    paper_bgcolor="rgba(0,0,0,0)",
                    legend=dict(bgcolor="rgba(255,255,255,0.92)", bordercolor="#dde2ea", borderwidth=1, font=dict(color="#12161f", size=14)),
                )
            fig.update_traces(marker=dict(sizemin=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No zones match the selected filters.")

    st.markdown("### 📋 Zone Status Board")
    for _, row in filtered.iterrows():
        with st.container():
            st.markdown(
                f"""
                <div class="sg-card {sev_card_class(row['Severity'])}">
                    <h4>{row['Zone']}</h4>
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div>
                            <b>{row['Disaster Type']}</b> {sev_badge(row['Severity'])}<br/>
                            <span style="color:var(--text-dim);font-size:13px;">
                                Affected: {row['Affected Population']:,} · Rescued: {row['Rescued']:,} ·
                                Distress Signals: {row['Active Distress Signals']} · Shelters: {row['Shelters Active']}
                            </span>
                        </div>
                        <div style="text-align:right;color:var(--text-dim);font-size:12px;">
                            Updated {row['Last Updated']}
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# ──────────────────────────────────────────────────────────────────────────
# PAGE 2: RESOURCE ALLOCATION & LOGISTICS
# ──────────────────────────────────────────────────────────────────────────
elif page == "📦 Resource Allocation & Logistics":
    st.markdown("### 📦 Resource Inventory Overview")
    inv_cols = st.columns(len(RESOURCE_TYPES))
    for col, (_, r) in zip(inv_cols, inventory_df.iterrows()):
        pct_avail = r["Available"] / r["Total Stock"] * 100
        col.metric(r["Resource"], f"{r['Available']:,}", delta=f"{pct_avail:.0f}% available", delta_color="off")

    fig_inv = px.bar(
        inventory_df, x="Resource", y=["Allocated", "Available"],
        barmode="stack", title="Stock Allocation by Resource Type",
        color_discrete_map={"Allocated": "#c8481a", "Available": "#127a3d"},
    )
    fig_inv.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#12161f", size=14), legend_title_text="",
    )
    st.plotly_chart(fig_inv, use_container_width=True)

    st.markdown("---")
    st.markdown("### 🚚 Smart Dispatch Calculator")
    st.caption("Allocate relief resources to a zone. Recommended quantity auto-scales with severity & affected population.")

    with st.form("dispatch_form"):
        f1, f2, f3 = st.columns(3)
        with f1:
            zone_choice = st.selectbox("Target Zone", zones_df["Zone"].tolist())
            zone_row = zones_df[zones_df["Zone"] == zone_choice].iloc[0]
        with f2:
            resource_choice = st.selectbox("Resource Type", RESOURCE_TYPES)
        with f3:
            priority = st.selectbox("Priority Level", ["Critical – Airlift", "High – Road Convoy", "Standard – Scheduled"])

        sev_multiplier = {"Critical": 3.5, "High": 2.2, "Moderate": 1.4, "Stable": 0.8}
        recommended_qty = int(zone_row["Affected Population"] * 0.02 * sev_multiplier[zone_row["Severity"]])
        recommended_qty = max(50, min(recommended_qty, 5000))

        qty = st.slider(
            f"Quantity to dispatch (AI-recommended: {recommended_qty:,})",
            min_value=10, max_value=6000, value=recommended_qty, step=10,
        )
        note = st.text_area("Dispatch notes (optional)", placeholder="e.g. Route via NH-66, coordinate with local NDRF unit...")
        submitted = st.form_submit_button("🚀 Confirm & Dispatch", use_container_width=True)

    if submitted:
        available_stock = int(inventory_df.loc[inventory_df["Resource"] == resource_choice, "Available"].iloc[0])
        if qty > available_stock:
            st.warning(
                f"⚠️ Requested {qty:,} units of **{resource_choice}** exceeds available stock "
                f"({available_stock:,}). Dispatch capped to available stock and flagged for restock."
            )
            qty = available_stock
        new_entry = pd.DataFrame([{
            "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Zone": zone_choice,
            "Resource": resource_choice,
            "Quantity": qty,
            "Priority": priority,
            "Status": "Dispatched ✅",
        }])
        st.session_state.dispatch_log = pd.concat([new_entry, st.session_state.dispatch_log], ignore_index=True)
        st.session_state.inventory_df.loc[inventory_df["Resource"] == resource_choice, "Available"] -= qty
        st.session_state.inventory_df.loc[inventory_df["Resource"] == resource_choice, "Allocated"] += qty
        st.success(f"✅ Dispatched **{qty:,} units of {resource_choice}** to **{zone_choice}** with priority *{priority}*.")
        st.balloons()

    st.markdown("### 📜 Dispatch Log")
    if st.session_state.dispatch_log.empty:
        st.info("No dispatches recorded yet this session. Submit the form above to log one.")
    else:
        st.dataframe(st.session_state.dispatch_log, use_container_width=True, hide_index=True)

# ──────────────────────────────────────────────────────────────────────────
# PAGE 3: CITIZEN SOS PORTAL
# ──────────────────────────────────────────────────────────────────────────
elif page == "🆘 Citizen SOS Portal":
    st.markdown("### 🆘 Citizen Emergency Reporting")
    st.caption("Simulated public-facing SOS intake. Submissions instantly update the Command Center distress-signal count.")

    left, right = st.columns([1.1, 1])
    with left:
        with st.form("sos_form", clear_on_submit=True):
            name = st.text_input("Your Name (optional)", placeholder="e.g. Anita Sharma")
            phone = st.text_input("Contact Number (optional)", placeholder="e.g. +91 98XXXXXXXX")
            zone_sel = st.selectbox("Nearest Zone / Locality", zones_df["Zone"].tolist())
            emergency_type = st.selectbox("Emergency Type", SOS_TYPES)
            people_count = st.slider("Number of people needing help", 1, 50, 1)
            details = st.text_area("Additional details", placeholder="Describe your situation, landmark, floor number, etc.")
            photo = st.file_uploader(
                "📷 Upload a photo of the situation (optional)",
                type=["png", "jpg", "jpeg"],
                help="A photo helps responders assess severity and plan the right resources before arriving.",
            )
            gps_sim = st.checkbox("📍 Attach simulated GPS coordinates", value=True)
            sos_submit = st.form_submit_button("🆘 SEND SOS ALERT", use_container_width=True, type="primary")

        if sos_submit:
            zone_row = zones_df[zones_df["Zone"] == zone_sel].iloc[0]
            lat = zone_row["Latitude"] + random.uniform(-0.01, 0.01) if gps_sim else None
            lon = zone_row["Longitude"] + random.uniform(-0.01, 0.01) if gps_sim else None
            new_sos = pd.DataFrame([{
                "Time": datetime.now().strftime("%H:%M:%S"),
                "Name": name if name else "Anonymous",
                "Zone": zone_sel,
                "Emergency Type": emergency_type,
                "Details": f"{people_count} people — {details}" if details else f"{people_count} people",
                "Photo Attached": "📷 Yes" if photo else "—",
                "Status": "🔴 Pending Response",
            }])
            st.session_state.sos_log = pd.concat([new_sos, st.session_state.sos_log], ignore_index=True)
            st.session_state.zones_df.loc[st.session_state.zones_df["Zone"] == zone_sel, "Active Distress Signals"] += 1
            st.success(f"✅ SOS Alert sent for **{zone_sel}** — Nearest response team has been notified. Stay safe!")
            if gps_sim:
                st.info(f"📍 GPS attached: {lat:.4f}, {lon:.4f}")
            if photo is not None:
                st.image(photo, caption="Uploaded situation photo", width=320)
            st.toast("Emergency responders alerted!", icon="🚨")

    with right:
        st.markdown("#### 📞 Quick Emergency Contacts")
        st.markdown(
            """
            <div class="sg-contact-card">
            🚑 <b>National Disaster Helpline:</b> 1078<br/>
            👮 <b>Police:</b> 112<br/>
            🚒 <b>Fire:</b> 101<br/>
            🏥 <b>Ambulance:</b> 108<br/>
            🌊 <b>NDRF Control Room:</b> 011-24363260
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("#### 🕒 Recent SOS Reports (this session)")
        if st.session_state.sos_log.empty:
            st.info("No SOS reports submitted yet. Use the form to simulate a citizen report.")
        else:
            st.dataframe(st.session_state.sos_log, use_container_width=True, hide_index=True, height=300)

    st.markdown("---")
    st.markdown("### 🌍 All-Zone Distress Signal Snapshot")
    fig_sos = px.bar(
        zones_df.sort_values("Active Distress Signals", ascending=True),
        x="Active Distress Signals", y="Zone", orientation="h",
        color="Severity", color_discrete_map={"Critical": "#d9291c", "High": "#c8481a", "Moderate": "#b8720a", "Stable": "#127a3d"},
        title="Active Distress Signals by Zone",
    )
    fig_sos.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#12161f", size=14))
    st.plotly_chart(fig_sos, use_container_width=True)

# ──────────────────────────────────────────────────────────────────────────
# PAGE 4: PREDICTIVE RISK & ANALYTICS
# ──────────────────────────────────────────────────────────────────────────
elif page == "📈 Predictive Risk & Analytics":
    st.markdown("### 📈 Predictive Risk & Analytics")
    st.caption("14-day trend simulation of affected population and resource depletion, used to forecast restocking needs.")

    t1, t2 = st.columns([2, 1])
    with t1:
        pop_trend = trend_df.drop_duplicates(subset="Date")[["Date", "Affected Population"]]
        fig_pop = px.area(
            pop_trend, x="Date", y="Affected Population",
            title="Affected Population Trend (14 Days)",
            color_discrete_sequence=["#d9291c"],
        )
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
        fig_dep = px.line(
            dep_data, x="Date", y="Stock Remaining (%)", color="Resource",
            markers=True, title="Projected Stock Remaining Over Time",
        )
        fig_dep.add_hline(y=20, line_dash="dash", line_color="#d9291c", annotation_text="Critical Threshold (20%)")
        fig_dep.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#12161f", size=14))
        st.plotly_chart(fig_dep, use_container_width=True)
    else:
        st.info("Select at least one resource to view the depletion forecast.")

    st.markdown("### 🎯 Zone Risk Matrix")
    risk_fig = px.scatter(
        zones_df, x="Affected Population", y="Active Distress Signals",
        size="Rescued", color="Severity", text="Zone",
        color_discrete_map={"Critical": "#d9291c", "High": "#c8481a", "Moderate": "#b8720a", "Stable": "#127a3d"},
        title="Risk Matrix — Population vs. Active Distress Signals",
    )
    risk_fig.update_traces(textposition="top center", textfont=dict(size=11, color="#5b6473"))
    risk_fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#12161f", size=14), height=480)
    st.plotly_chart(risk_fig, use_container_width=True)

    with st.expander("📊 View Raw Zone & Inventory Data"):
        st.markdown("**Zone Data**")
        st.dataframe(zones_df, use_container_width=True, hide_index=True)
        st.markdown("**Inventory Data**")
        st.dataframe(inventory_df, use_container_width=True, hide_index=True)

# ──────────────────────────────────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <p class="footer-note">
    RESQ · Prototype for Smart India Hackathon (SIH 26206) — Student Innovation in Disaster Management.<br/>
    All data shown is simulated for demonstration purposes.
    </p>
    """,
    unsafe_allow_html=True,
)