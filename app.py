"""
RESQ - AI Disaster Prediction & Response Alert System
=======================================================
Run with:  streamlit run app.py

Structure:
  Phase 1 - PREDICT & MONITOR  (main focus): AI reads satellite/drone imagery,
            flags risk, shows it on a live map, fires a siren + notification.
  Phase 2 - GROUND REPORTS: people on-site report what's actually happening.
  Phase 3 - RESOURCE OPS: hospitals / police / shelters, matched to incidents.

Built to stay usable on low/slow connections:
  - "Lite mode" swaps the heavy Leaflet map for a tiny plotly scattergeo plot.
  - Data is loaded once via st.cache_data.
  - No external CDN images; logo + siren are shipped locally in /assets.
"""

import math
import time
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

from utils.prediction_utils import run_disaster_prediction, generate_live_feed
from utils.alert_utils import fire_alert, sos_button_css
from utils.map_utils import build_full_map, build_lite_map

# --------------------------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="RESQ | Disaster Alert System",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(sos_button_css(), unsafe_allow_html=True)
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {padding-top: 1.2rem; padding-bottom: 2rem;}
    body {background-color: #0a0c10;}
    .resq-title {
        font-size: 44px; font-weight: 900; letter-spacing: 2px;
        color: #ffffff; margin-bottom: 0;
    }
    .resq-sub {color:#8b93a7; font-size:15px; margin-top:-6px;}
    .ticker {
        background:#14171f; border-left:4px solid #ff1f1f; padding:8px 14px;
        border-radius:6px; color:#ff9d9d; font-family:monospace; font-size:13px;
    }
    div[data-testid="stMetric"] {
        background:#12151c; border:1px solid #262a35; border-radius:10px; padding:10px;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# MONITORED REGIONS (would come from a live satellite tasking feed)
# --------------------------------------------------------------------------
MONITORED_REGIONS = [
    {"name": "Kerala Coast", "lat": 9.9312, "lon": 76.2673},
    {"name": "Uttarakhand Himalayas", "lat": 30.4038, "lon": 79.3200},
    {"name": "Odisha Coastline", "lat": 19.8135, "lon": 85.8312},
    {"name": "Assam Brahmaputra Basin", "lat": 26.2006, "lon": 92.9376},
    {"name": "Sikkim Glacial Belt", "lat": 27.5330, "lon": 88.5122},
    {"name": "Himachal Hill Districts", "lat": 31.1048, "lon": 77.1734},
]


# --------------------------------------------------------------------------
# CACHED DATA LOADERS
# --------------------------------------------------------------------------
@st.cache_data
def load_history():
    return pd.read_csv("data/historical_disasters.csv")


@st.cache_data
def load_resources():
    return pd.read_csv("data/resources.csv")


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371
    dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1))
         * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    return 2 * r * math.asin(math.sqrt(a))


# --------------------------------------------------------------------------
# SESSION STATE
# --------------------------------------------------------------------------
if "predictions" not in st.session_state:
    st.session_state.predictions = generate_live_feed(MONITORED_REGIONS)
if "ground_reports" not in st.session_state:
    st.session_state.ground_reports = []
if "last_scan" not in st.session_state:
    st.session_state.last_scan = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
if "alert_fired_for" not in st.session_state:
    st.session_state.alert_fired_for = set()

history_df = load_history()
resources_df = load_resources()

# --------------------------------------------------------------------------
# SIDEBAR
# --------------------------------------------------------------------------
with st.sidebar:
    st.image("assets/logo.png", use_container_width=True)
    st.markdown("---")
    lite_mode = st.toggle("Low-bandwidth Lite Mode", value=False,
                           help="Swaps the heavy map for a lightweight chart and trims data. Use this on slow connections.")
    sound_on = st.toggle("Siren + notifications", value=True)
    st.markdown("---")
    page = st.radio(
        "NAVIGATE",
        ["🛰️ Phase 1 · Predict & Monitor", "📢 Phase 2 · Ground Reports",
         "🚑 Phase 3 · Resource Ops", "📜 Past Incidents"],
        index=0,
    )
    st.markdown("---")
    st.caption(f"Last satellite scan: {st.session_state.last_scan}")
    st.markdown(
        '<a href="tel:112" class="sos-btn">🆘 SOS · CALL 112</a>',
        unsafe_allow_html=True,
    )
    st.caption("Emergency helpline (India): 112 · NDRF: 011-24363260")

# --------------------------------------------------------------------------
# HEADER
# --------------------------------------------------------------------------
critical_count = sum(1 for p in st.session_state.predictions if p["risk_level"] == "CRITICAL")
high_count = sum(1 for p in st.session_state.predictions if p["risk_level"] == "HIGH")

h1, h2 = st.columns([3, 1])
with h1:
    st.markdown('<p class="resq-title">RESQ</p>', unsafe_allow_html=True)
    st.markdown('<p class="resq-sub">AI DISASTER PREDICTION &amp; RESPONSE ALERT SYSTEM — LIVE</p>', unsafe_allow_html=True)
with h2:
    st.markdown(f"""
    <div class='ticker'>🔴 LIVE &nbsp;|&nbsp; {critical_count} CRITICAL &nbsp;|&nbsp; {high_count} HIGH &nbsp;|&nbsp; {len(MONITORED_REGIONS)} zones monitored</div>
    """, unsafe_allow_html=True)

st.markdown("")

# ==========================================================================
# PHASE 1 · PREDICT & MONITOR
# ==========================================================================
if page.startswith("🛰️"):
    st.subheader("Phase 1 · AI Prediction from Satellite & Drone Imagery")
    st.caption("This is our core strength: catching a disaster **before** it fully unfolds, "
               "by continuously reading satellite and drone feeds across monitored zones.")

    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        scan_clicked = st.button("🔄 Run New AI Scan", use_container_width=True, type="primary")
    with c2:
        source_choice = st.selectbox("Imagery source", ["satellite", "drone", "fused"], label_visibility="collapsed")
    with c3:
        uploaded_img = st.file_uploader("Or analyze an uploaded satellite/drone image", type=["png", "jpg", "jpeg"], label_visibility="collapsed")

    if scan_clicked:
        with st.spinner("Analyzing latest imagery across all monitored zones..."):
            time.sleep(0.6)
            st.session_state.predictions = generate_live_feed(MONITORED_REGIONS)
            st.session_state.last_scan = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if uploaded_img is not None:
        colimg, colres = st.columns([1, 1])
        with colimg:
            st.image(uploaded_img, caption="Uploaded imagery", use_container_width=True)
        with colres:
            result = run_disaster_prediction(region="Uploaded Image Zone", image_bytes=uploaded_img.read(), source=source_choice)
            st.session_state.predictions.append(result)
            st.markdown(f"**Predicted type:** {result['disaster_type']}")
            st.markdown(f"**Risk score:** {result['risk_score']} / 100")
            st.markdown(f"**Confidence:** {result['confidence']}%")

    predictions = st.session_state.predictions

    # ---- ALERT LOGIC -----------------------------------------------------
    critical_now = [p for p in predictions if p["risk_level"] in ("CRITICAL", "HIGH")]
    new_alerts = [p for p in critical_now if p["region"] not in st.session_state.alert_fired_for]
    if new_alerts and sound_on:
        top = sorted(new_alerts, key=lambda x: x["risk_score"], reverse=True)[0]
        fire_alert(
            title=f"RESQ ALERT: {top['risk_level']} — {top['disaster_type']}",
            message=f"{top['region']}: risk score {top['risk_score']}, confidence {top['confidence']}%.",
            play_sound=True,
        )
        for p in new_alerts:
            st.session_state.alert_fired_for.add(p["region"])

    if critical_now:
        top = sorted(critical_now, key=lambda x: x["risk_score"], reverse=True)[0]
        st.markdown(f"""
        <div class='resq-card' style='border-color:#b30000;'>
        <span class='risk-badge-{top['risk_level'].lower()}'>{top['risk_level']}</span>
        &nbsp;&nbsp;<b>{top['disaster_type']}</b> detected near <b>{top['region']}</b>
        &nbsp;·&nbsp; ETA to impact: <b>{top['eta_hours']} hrs</b>
        &nbsp;·&nbsp; radius <b>{top['affected_radius_km']} km</b>
        <br><small>{top['notes']}</small>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### Live Monitoring Map")
    if lite_mode:
        st.caption("Lite mode active — lightweight plot instead of full map tiles.")
        fig = build_lite_map(predictions)
        st.plotly_chart(fig, use_container_width=True)
    else:
        try:
            from streamlit_folium import st_folium
            fmap = build_full_map(predictions, resources_df)
            st_folium(fmap, use_container_width=True, height=460, returned_objects=[])
        except ModuleNotFoundError:
            st.warning("streamlit-folium not installed — falling back to lite map. Add it to requirements.txt.")
            fig = build_lite_map(predictions)
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Zone-by-Zone Risk")
    grid_cols = st.columns(3)
    for i, p in enumerate(predictions[:len(MONITORED_REGIONS)]):
        with grid_cols[i % 3]:
            st.markdown(f"""
            <div class='resq-card'>
            <b>{p['region']}</b><br>
            <span class='risk-badge-{p['risk_level'].lower()}'>{p['risk_level']}</span><br><br>
            Type: {p['disaster_type']}<br>
            Score: {p['risk_score']}/100 &nbsp;|&nbsp; Confidence: {p['confidence']}%<br>
            Source: {p['source']} &nbsp;|&nbsp; {p['timestamp']}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("### Analytics")
    a1, a2, a3 = st.columns(3)
    with a1:
        df_type = pd.DataFrame(predictions)["disaster_type"].value_counts().reset_index()
        df_type.columns = ["Type", "Count"]
        fig_pie = px.pie(df_type, names="Type", values="Count", title="Predicted Disaster Types", hole=0.45)
        fig_pie.update_layout(margin=dict(t=40, b=0, l=0, r=0), height=300)
        st.plotly_chart(fig_pie, use_container_width=True)
    with a2:
        df_risk = pd.DataFrame(predictions)["risk_level"].value_counts().reset_index()
        df_risk.columns = ["Risk", "Count"]
        color_map = {"CRITICAL": "#b30000", "HIGH": "#ff6a00", "MODERATE": "#ffb800", "LOW": "#1fa855"}
        fig_bar = px.bar(df_risk, x="Risk", y="Count", color="Risk", color_discrete_map=color_map, title="Zones by Risk Level")
        fig_bar.update_layout(margin=dict(t=40, b=0, l=0, r=0), height=300, showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    with a3:
        avg_score = pd.DataFrame(predictions)["risk_score"].mean()
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=avg_score,
            title={"text": "Avg. Regional Risk Score"},
            gauge={"axis": {"range": [0, 100]},
                   "bar": {"color": "#ff1f1f" if avg_score > 55 else "#1fa855"},
                   "steps": [
                       {"range": [0, 30], "color": "#123"},
                       {"range": [30, 55], "color": "#332"},
                       {"range": [55, 80], "color": "#421"},
                       {"range": [80, 100], "color": "#500"}]}))
        fig_gauge.update_layout(margin=dict(t=40, b=0, l=20, r=20), height=300)
        st.plotly_chart(fig_gauge, use_container_width=True)

    st.markdown("### Notify Authorities")
    notify_zone = st.selectbox("Select a zone to alert", [p["region"] for p in predictions])
    if st.button("📡 Dispatch alert to authorities + nearby resources"):
        chosen = next(p for p in predictions if p["region"] == notify_zone)
        resources_df["dist_km"] = resources_df.apply(
            lambda r: haversine_km(chosen["lat"], chosen["lon"], r["lat"], r["lon"]), axis=1)
        nearest = resources_df.sort_values("dist_km").head(3)
        st.success(f"Alert dispatched for {notify_zone} ({chosen['risk_level']} · {chosen['disaster_type']}).")
        st.dataframe(nearest[["name", "type", "region", "contact", "dist_km"]]
                     .rename(columns={"dist_km": "distance_km"})
                     .round({"distance_km": 1}), use_container_width=True, hide_index=True)

# ==========================================================================
# PHASE 2 · GROUND REPORTS
# ==========================================================================
elif page.startswith("📢"):
    st.subheader("Phase 2 · Ground Reports from Affected Areas")
    st.caption("Once a zone is flagged, people on the ground can add real detail: what's actually happening, how many are affected, and what help is needed.")

    with st.form("ground_report_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            r_type = st.selectbox("Type of disaster", ["Flood", "Earthquake", "Landslide", "Cyclone", "Fire", "Other"])
            r_location = st.text_input("Location / landmark")
            r_lat = st.number_input("Latitude", value=20.5937, format="%.4f")
            r_lon = st.number_input("Longitude", value=78.9629, format="%.4f")
        with col2:
            r_people = st.number_input("Approx. number of people affected", min_value=0, step=1)
            r_help = st.multiselect("Help needed", ["Medical", "Food/Water", "Shelter", "Evacuation", "Rescue Team", "Power/Electricity"])
            r_severity = st.select_slider("Perceived severity", ["Low", "Moderate", "High", "Critical"], value="Moderate")
        r_desc = st.text_area("Describe the situation")
        r_photo = st.file_uploader("Attach a photo (optional)", type=["png", "jpg", "jpeg"])
        submitted = st.form_submit_button("Submit Report", type="primary", use_container_width=True)

        if submitted:
            st.session_state.ground_reports.append({
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": r_type, "location": r_location, "lat": r_lat, "lon": r_lon,
                "people_affected": r_people, "help_needed": ", ".join(r_help),
                "severity": r_severity, "description": r_desc,
                "has_photo": r_photo is not None,
            })
            st.success("Report submitted — thank you. This has been added to the live feed below.")

    st.markdown("### Live Ground Reports")
    if st.session_state.ground_reports:
        rep_df = pd.DataFrame(st.session_state.ground_reports)
        st.dataframe(rep_df, use_container_width=True, hide_index=True)

        b1, b2 = st.columns(2)
        with b1:
            fig = px.pie(rep_df, names="type", title="Reports by Disaster Type", hole=0.45)
            st.plotly_chart(fig, use_container_width=True)
        with b2:
            fig2 = px.bar(rep_df, x="location", y="people_affected", color="severity",
                          color_discrete_map={"Low": "#1fa855", "Moderate": "#ffb800", "High": "#ff6a00", "Critical": "#b30000"},
                          title="People Affected by Location")
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No ground reports submitted yet.")

# ==========================================================================
# PHASE 3 · RESOURCE OPS
# ==========================================================================
elif page.startswith("🚑"):
    st.subheader("Phase 3 · Resource Management & Analysis")
    st.caption("Hospitals, police, shelters and rescue teams — tracked, filtered, and matched to active incidents.")

    f1, f2 = st.columns(2)
    with f1:
        type_filter = st.multiselect("Filter by type", resources_df["type"].unique().tolist(),
                                      default=resources_df["type"].unique().tolist())
    with f2:
        region_filter = st.multiselect("Filter by region", resources_df["region"].unique().tolist(),
                                        default=resources_df["region"].unique().tolist())

    filtered = resources_df[resources_df["type"].isin(type_filter) & resources_df["region"].isin(region_filter)]
    st.dataframe(filtered, use_container_width=True, hide_index=True)

    r1, r2 = st.columns(2)
    with r1:
        fig = px.pie(filtered, names="type", title="Resource Mix", hole=0.45)
        st.plotly_chart(fig, use_container_width=True)
    with r2:
        fig2 = px.bar(filtered, x="region", y="capacity", color="type", title="Capacity by Region")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### Match Resources to Active Predicted Risk Zones")
    active = [p for p in st.session_state.predictions if p["risk_level"] in ("HIGH", "CRITICAL")]
    if active:
        for p in active:
            filtered = filtered.copy()
            filtered["dist_km"] = filtered.apply(lambda r: haversine_km(p["lat"], p["lon"], r["lat"], r["lon"]), axis=1)
            nearest = filtered.sort_values("dist_km").head(3)
            st.markdown(f"**{p['region']}** — {p['risk_level']} {p['disaster_type']}")
            st.dataframe(nearest[["name", "type", "contact", "dist_km"]].rename(columns={"dist_km": "distance_km"}).round({"distance_km": 1}),
                         use_container_width=True, hide_index=True)
    else:
        st.info("No HIGH/CRITICAL zones right now — resource matching will appear here automatically when one is detected.")

# ==========================================================================
# PAST INCIDENTS
# ==========================================================================
else:
    st.subheader("Past Incidents — Historical Disaster Data")
    st.caption("Includes major past events such as the 2015 Nepal earthquake, used to calibrate and validate the prediction model.")

    country_filter = st.multiselect("Country", history_df["country"].unique().tolist(),
                                     default=history_df["country"].unique().tolist())
    type_filter2 = st.multiselect("Type", history_df["type"].unique().tolist(),
                                   default=history_df["type"].unique().tolist())
    hist_filtered = history_df[history_df["country"].isin(country_filter) & history_df["type"].isin(type_filter2)]

    st.dataframe(hist_filtered.sort_values("date", ascending=False), use_container_width=True, hide_index=True)

    if not lite_mode:
        try:
            import folium
            from streamlit_folium import st_folium
            hm = folium.Map(location=(20.5, 78.9), zoom_start=4, tiles="CartoDB dark_matter")
            sev_color = {"Critical": "#b30000", "High": "#ff6a00", "Medium": "#ffb800", "Low": "#1fa855"}
            for _, row in hist_filtered.iterrows():
                folium.CircleMarker(
                    location=(row["lat"], row["lon"]),
                    radius=6 + (row["deaths"] ** 0.25),
                    color=sev_color.get(row["severity"], "#888"),
                    fill=True, fill_opacity=0.7,
                    popup=f"<b>{row['name']}</b><br>{row['date']}<br>Deaths: {row['deaths']}<br>{row['summary']}",
                    tooltip=row["name"],
                ).add_to(hm)
            st_folium(hm, use_container_width=True, height=420, returned_objects=[])
        except ModuleNotFoundError:
            st.info("Install streamlit-folium for the interactive historical map.")

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(hist_filtered.sort_values("deaths", ascending=False), x="name", y="deaths",
                     color="type", title="Deaths by Incident")
        fig.update_layout(xaxis_tickangle=-35)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig2 = px.pie(hist_filtered, names="type", title="Incidents by Type", hole=0.45)
        st.plotly_chart(fig2, use_container_width=True)
