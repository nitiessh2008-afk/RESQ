"""
ResQ Live: Comprehensive Disaster Management Platform
=====================================================
A unified system encompassing all three critical disaster phases:
1. BEFORE DISASTER: Prediction, satellite/drone monitoring, and proactive mitigation (MAJOR PRIORITY)
2. DURING DISASTER: Automated help triggers and low-bandwidth Emergency SOS beacon
3. AFTER DISASTER: Post-disaster damage reporting, relief distribution, and recovery tracking

Author: ResQ Live Engineering Team
Repository: https://github.com/your-org/resqlive
License: MIT
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
from PIL import Image, ImageDraw

# ==============================================================================
# 0. PAGE CONFIGURATION & SETUP
# ==============================================================================
st.set_page_config(
    page_title="ResQ Live | Comprehensive Disaster Management",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Note: In accordance with guidelines, no custom CSS font-size alterations are used.
# Native Streamlit typography and layout components are preserved.

# ==============================================================================
# 1. SESSION STATE INITIALIZATION (PERSISTENT DATA STORE)
# ==============================================================================
def init_session_state():
    """Initializes in-memory session data for dispatches, SOS alerts, and reports."""
    if "initialized" not in st.session_state:
        st.session_state.initialized = True

        # Phase 1: Default Risk Indicators
        st.session_state.current_hazard_status = "MODERATE"
        st.session_state.active_early_warnings = [
            {
                "id": "EW-2026-081",
                "hazard": "Riverine Flood",
                "region": "Basin Sector 4 (Upper Reach)",
                "predicted_severity": "High (Level 3)",
                "est_impact_window": "Next 12-24 Hours",
                "action": "Initiate Stage 1 Floodgate Discharge; Evacuate Low-lying Settlements",
                "timestamp": (datetime.now() - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M"),
            }
        ]

        # Phase 2: Automated First Responder Dispatches
        st.session_state.automated_dispatches = [
            {
                "dispatch_id": "DISP-8901",
                "hazard_trigger": "River Water Level > 8.5m (Basin Sector 4)",
                "unit": "NDRF Battalion 7 (Water Rescue)",
                "destination": "Riverbank Zone B",
                "status": "En Route",
                "time_triggered": (datetime.now() - timedelta(minutes=45)).strftime("%H:%M:%S"),
            },
            {
                "dispatch_id": "DISP-8902",
                "hazard_trigger": "Wildfire Thermal Anomaly Detected (North Forest)",
                "unit": "Aerial Firefighting Squadron 2",
                "destination": "North Ridge Sector 1",
                "status": "On Scene",
                "time_triggered": (datetime.now() - timedelta(hours=1, minutes=15)).strftime("%H:%M:%S"),
            },
            {
                "dispatch_id": "DISP-8903",
                "hazard_trigger": "Cyclone Wind Gust Alert (>110 km/h)",
                "unit": "State Power Grid Restoration Team",
                "destination": "Coastal Grid Substation 3",
                "status": "Staged",
                "time_triggered": (datetime.now() - timedelta(minutes=10)).strftime("%H:%M:%S"),
            }
        ]

        # Phase 2: Active SOS Signals
        st.session_state.sos_signals = [
            {
                "sos_id": "SOS-1042",
                "latitude": 19.0760,
                "longitude": 72.8777,
                "triage": "Critical Medical Need",
                "people_count": 4,
                "details": "Diabetic patient with high fever, trapped on second floor due to water level.",
                "status": "Assigned (Unit 7)",
                "timestamp": (datetime.now() - timedelta(minutes=25)).strftime("%H:%M:%S"),
            },
            {
                "sos_id": "SOS-1043",
                "latitude": 19.0880,
                "longitude": 72.8680,
                "triage": "Trapped / Rising Water",
                "people_count": 2,
                "details": "Water reached 4 feet. Need evacuation boat.",
                "status": "En Route",
                "timestamp": (datetime.now() - timedelta(minutes=14)).strftime("%H:%M:%S"),
            }
        ]

        # Phase 3: Post-Disaster Reports
        st.session_state.damage_reports = [
            {
                "report_id": "REP-501",
                "location": "Green Valley Block C",
                "damage_type": "Road Blockage & Mudslide",
                "severity": "Severe",
                "casualties": 0,
                "supplies_needed": "Heavy Earthmovers, Drinking Water (200L)",
                "status": "Under Assessment",
                "timestamp": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"),
            },
            {
                "report_id": "REP-502",
                "location": "Old Town Commercial Complex",
                "damage_type": "Electrical Grid & Transformer Down",
                "severity": "Moderate",
                "casualties": 0,
                "supplies_needed": "Emergency Generator, Diesel Rations",
                "status": "Relief Dispatched",
                "timestamp": (datetime.now() - timedelta(hours=18)).strftime("%Y-%m-%d %H:%M"),
            }
        ]

        # Phase 3: Relief Supplies Inventory
        st.session_state.relief_inventory = {
            "Clean Water Kits (10L)": {"requested": 1200, "dispatched": 950},
            "Emergency Food Rations": {"requested": 2500, "dispatched": 2100},
            "Medical First Aid Kits": {"requested": 400, "dispatched": 380},
            "Emergency Shelters / Tarps": {"requested": 850, "dispatched": 620},
            "Portable Power Generators": {"requested": 60, "dispatched": 42},
        }

init_session_state()

# ==============================================================================
# 2. PLACEHOLDER API CONNECTORS (NASA, GOOGLE EARTH ENGINE, OPENWEATHER)
# ==============================================================================
def fetch_nasa_firms_wildfire_feed(api_key: str = None, country_code: str = "IND"):
    """
    Placeholder for NASA FIRMS (Fire Information for Resource Management System) API.
    Fetches real-time MODIS / VIIRS active fire hotspots.
    API Docs: https://firms.modaps.eosdis.nasa.gov/api/
    """
    if not api_key:
        # Returns simulated high-confidence hotspot data points
        return pd.DataFrame({
            "latitude": [19.120, 19.145, 19.180, 19.135],
            "longitude": [72.920, 72.950, 72.990, 72.940],
            "brightness_kelvin": [342.5, 365.1, 388.9, 350.2],
            "confidence": ["Nominal", "High", "Critical", "High"],
            "satellite": ["VIIRS-SNPP", "MODIS-Aqua", "VIIRS-SNPP", "MODIS-Terra"],
            "acquisition_time": [datetime.now().strftime("%Y-%m-%d %H:%M") for _ in range(4)]
        })
    # Real API integration snippet:
    # url = f"https://firms.modaps.eosdis.nasa.gov/api/country/csv/{api_key}/VIIRS_SNPP_NRT/{country_code}/1"
    # return pd.read_csv(url)


def fetch_openweather_forecast(api_key: str = None, lat: float = 19.0760, lon: float = 72.8777):
    """
    Placeholder for OpenWeatherMap One Call / Forecast API.
    Fetches temperature, precipitation probability, wind speed, and severe weather alerts.
    API Docs: https://openweathermap.org/api
    """
    if not api_key:
        # Synthetic weather payload
        return {
            "city": "Coastal Monitoring Station Delta",
            "temperature_c": 31.5,
            "humidity_pct": 89,
            "precipitation_mm": 115.4,
            "wind_speed_kmh": 78.2,
            "pressure_hpa": 988.0,
            "cyclone_threat": "Elevated (Category 2 Potential)",
            "river_gauge_m": 8.42,
            "danger_threshold_m": 8.00
        }
    # Real API integration snippet:
    # response = requests.get(f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric")
    # return response.json()


def query_google_earth_engine_ndwi(geojson_boundary=None):
    """
    Placeholder for Google Earth Engine (GEE) Sentinel-2 Normalized Difference Water Index (NDWI)
    and Normalized Difference Vegetation Index (NDVI) for pre-disaster environmental assessment.
    GEE Python API: https://developers.google.com/earth-engine/guides/python_install
    """
    # Placeholder returning calculated indices
    return {
        "status": "GEE Connector Ready (Mock Mode)",
        "mean_ndvi": 0.42,  # Low NDVI indicates dryness or urban deforestation
        "mean_ndwi": 0.78,  # High NDWI indicates excessive water accumulation / flood risk
        "soil_saturation_index": "88% (Near Saturation Capacity)",
        "satellite_source": "Copernicus Sentinel-2 MSI L2A"
    }


def generate_synthetic_imagery(view_type: str = "Weather Radar") -> Image.Image:
    """Generates synthetic high-resolution environmental monitoring imagery."""
    width, height = 700, 420
    img = Image.new("RGB", (width, height), color=(18, 25, 35))
    draw = ImageDraw.Draw(img)

    if view_type == "Weather Radar & Cyclone Tracking":
        # Draw simulated storm/cyclone spiral and precipitation bands
        for radius in range(50, 320, 25):
            color = (30 + radius // 2, 80 + radius // 4, 180 + radius // 5)
            draw.arc([(width // 2 - radius, height // 2 - radius),
                      (width // 2 + radius, height // 2 + radius)],
                     start=30, end=280, fill=color, width=6)
        # Eye of storm marker
        draw.ellipse([(width // 2 - 15, height // 2 - 15), (width // 2 + 15, height // 2 + 15)],
                     fill=(255, 60, 60), outline=(255, 255, 255))
        draw.text((width // 2 - 60, height // 2 + 25), "CYCLONE EYE: 988 hPa", fill=(255, 255, 255))

    elif view_type == "Hydrological Flood Inundation (NDWI)":
        # Draw river basin with flood risk inundation zones
        points = [(40, 200), (180, 230), (320, 180), (460, 260), (620, 220), (680, 240)]
        for i in range(len(points) - 1):
            draw.line([points[i], points[i+1]], fill=(40, 150, 255), width=28)
            # Inundation overflow markers
            draw.ellipse([points[i][0]-20, points[i][1]-20, points[i][0]+20, points[i][1]+20],
                         fill=(230, 70, 70, 120), outline=(255, 200, 0))
        draw.text((50, 40), "SATELLITE NDWI: CRITICAL WATER OVERFLOW DETECTED", fill=(255, 100, 100))
        draw.text((50, 70), "Basin Sector 4: 1.4m Above Safe Embankment Level", fill=(200, 230, 255))

    elif view_type == "Thermal IR Wildfire Detection":
        # Draw thermal heatmap hotspots
        for x, y, r, intensity in [(180, 150, 40, "370K"), (230, 190, 60, "388K"), (450, 280, 35, "355K")]:
            draw.ellipse([(x - r, y - r), (x + r, y + r)], fill=(255, 90, 0), outline=(255, 255, 0))
            draw.ellipse([(x - r // 2, y - r // 2), (x + r // 2, y + r // 2)], fill=(255, 240, 0))
            draw.text((x - 20, y - 10), intensity, fill=(0, 0, 0))
        draw.text((50, 40), "THERMAL IR (MODIS/VIIRS): 3 ACTIVE CANOPY HOTSPOTS", fill=(255, 150, 50))

    else:  # Drone Reconnaissance Survey
        # Drone grid layout with bounding boxes
        draw.rectangle([(80, 60), (620, 360)], outline=(0, 255, 150), width=2)
        draw.line([(width//2, 50), (width//2, 370)], fill=(0, 255, 150, 100), width=1)
        draw.line([(70, height//2), (630, height//2)], fill=(0, 255, 150, 100), width=1)
        # Target bounding boxes
        draw.rectangle([(200, 120), (320, 230)], outline=(255, 50, 50), width=3)
        draw.text((205, 125), "ANOMALY: Rising Water Cutoff", fill=(255, 255, 255))
        draw.rectangle([(420, 180), (530, 270)], outline=(255, 200, 0), width=2)
        draw.text((425, 185), "CHECK: Stranded Vehicle", fill=(255, 255, 255))
        draw.text((90, 70), "UAV DRONE STREAM: SECTOR 4 OVERFLIGHT (ALT: 120m)", fill=(0, 255, 150))

    return img


# ==============================================================================
# 3. SIDEBAR NAVIGATION & SYSTEM MONITOR
# ==============================================================================
st.sidebar.title("🛡️ ResQ Live")
st.sidebar.caption("Comprehensive Disaster Resilience Platform")

# System operational status
overall_threat = st.session_state.current_hazard_status
if overall_threat == "CRITICAL":
    st.sidebar.error(f"SYSTEM STATUS: {overall_threat} ALERT")
elif overall_threat == "HIGH":
    st.sidebar.warning(f"SYSTEM STATUS: {overall_threat} ADVISORY")
else:
    st.sidebar.info(f"SYSTEM STATUS: {overall_threat} MONITORING")

app_phase = st.sidebar.radio(
    "Select Disaster Management Phase:",
    [
        "1. BEFORE Disaster (Prediction & Mitigation)",
        "2. DURING Disaster (Active Response & SOS)",
        "3. AFTER Disaster (Reporting & Recovery)",
        "4. System Settings & API Connectors"
    ],
    index=0  # Defaults to BEFORE DISASTER as requested
)

st.sidebar.markdown("---")
st.sidebar.subheader("Quick Response Actions")
if st.sidebar.button("🚨 Broadcast System Emergency Warning", use_container_width=True):
    new_alert = {
        "id": f"EW-{datetime.now().strftime('%Y-%H%M%S')}",
        "hazard": "Severe Meteorological Event",
        "region": "All Coastal & Low-Lying Sectors",
        "predicted_severity": "Emergency Category",
        "est_impact_window": "Immediate (0-6 Hours)",
        "action": "Immediate evacuation to designated relief shelters; activate emergency sirens.",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    st.session_state.active_early_warnings.insert(0, new_alert)
    st.session_state.current_hazard_status = "CRITICAL"
    st.sidebar.success("Emergency Warning Broadcasted!")

st.sidebar.caption("ResQ Live Core Engine v2.4 | GitHub Ready")


# ==============================================================================
# 4. MODULE 1: BEFORE DISASTER (PREDICTION & PROACTIVE MITIGATION) - MAJOR PRIORITY
# ==============================================================================
if app_phase == "1. BEFORE Disaster (Prediction & Mitigation)":
    st.title("🛡️ Phase 1: BEFORE DISASTER (Prediction & Mitigation)")
    st.markdown(
        "**Core Focus**: Early detection, predictive risk intelligence, satellite/drone monitoring, "
        "and proactive community preparedness before catastrophic impact."
    )

    # Top Level Early Warning Banner if active
    if st.session_state.active_early_warnings:
        latest = st.session_state.active_early_warnings[0]
        st.warning(
            f"⚠️ **ACTIVE EARLY WARNING ({latest['id']})**: {latest['hazard']} in **{latest['region']}** "
            f"| Severity: **{latest['predicted_severity']}** | Expected Window: **{latest['est_impact_window']}**"
        )

    # Sub-tabs for Phase 1
    tab_imagery, tab_predictive, tab_preparedness = st.tabs([
        "🛰️ Satellite & Drone Imagery Integration",
        "🤖 Predictive AI Risk Analytics",
        "📋 Preparedness & Evacuation Hub"
    ])

    # --------------------------------------------------------------------------
    # SUB-TAB 1.1: SATELLITE & DRONE IMAGERY INTEGRATION
    # --------------------------------------------------------------------------
    with tab_imagery:
        st.subheader("Environmental Earth Observation & Drone Feeds")
        st.markdown(
            "Access real-time multispectral feeds and high-resolution UAV reconnaissance "
            "to detect environmental risk indicators such as river water levels, storm spirals, and heat signatures."
        )

        col_img_ctrl, col_img_view = st.columns([1, 2])

        with col_img_ctrl:
            feed_type = st.selectbox(
                "Select Active Imagery Feed:",
                [
                    "Hydrological Flood Inundation (NDWI)",
                    "Weather Radar & Cyclone Tracking",
                    "Thermal IR Wildfire Detection",
                    "Drone Reconnaissance Survey"
                ]
            )

            st.markdown("**Feed Metadata & Source Specs:**")
            if "Flood" in feed_type:
                st.info(
                    "**Sensor**: Sentinel-2 MSI Multi-Spectral\n\n"
                    "**Bands**: Band 3 (Green) & Band 8 (NIR) for NDWI\n\n"
                    "**Resolution**: 10m Ground Sample Distance\n\n"
                    "**Target Metric**: River Basin Crest & Surface Inundation"
                )
            elif "Weather" in feed_type:
                st.info(
                    "**Sensor**: INSAT-3D / NOAA GOES-16 Geostationary\n\n"
                    "**Product**: Cloud Top Brightness Temperature\n\n"
                    "**Refresh Rate**: Every 15 Minutes\n\n"
                    "**Target Metric**: Cyclone Vorticity & Deep Convection"
                )
            elif "Wildfire" in feed_type:
                st.info(
                    "**Sensor**: NASA MODIS (Aqua/Terra) & VIIRS (Suomi NPP)\n\n"
                    "**Product**: 375m Active Fire & Thermal Anomalies\n\n"
                    "**Threshold**: > 340 Kelvin Canopy Hotspot\n\n"
                    "**Target Metric**: Forest Fire Spread & Dry Fuel Index"
                )
            else:
                st.info(
                    "**Platform**: Autonomous Surveillance UAV Drone (Hexacopter)\n\n"
                    "**Payload**: 4K RGB + FLIR Lepton Thermal Sensor\n\n"
                    "**Flight Altitude**: 120m AGL\n\n"
                    "**Target Metric**: Blocked Drainage & Embankment Cracks"
                )

            st.markdown("---")
            st.markdown("**Upload Field Drone / Satellite Tile:**")
            uploaded_file = st.file_uploader(
                "Upload GeoTIFF, PNG, or JPG survey image for computer vision analysis:",
                type=["png", "jpg", "jpeg", "tif"]
            )
            if uploaded_file:
                st.success(f"Uploaded: {uploaded_file.name} (Ready for inference)")

        with col_img_view:
            if uploaded_file:
                st.markdown("**Uploaded Field Observation Tile:**")
                st.image(uploaded_file, caption=f"Field Upload: {uploaded_file.name}", use_container_width=True)
            else:
                st.markdown(f"**Live Feed Stream: {feed_type}**")
                synthetic_img = generate_synthetic_imagery(feed_type)
                st.image(synthetic_img, caption=f"Real-time Feed: {feed_type} (Satellite/UAV Composite)", use_container_width=True)

        # Satellite Anomaly Log
        st.markdown("#### Detected Geospatial Anomalies")
        anomaly_df = pd.DataFrame([
            {"Timestamp": "10 Mins Ago", "Region": "River Basin Sector 4", "Hazard Type": "River Gauge Breach", "Telemetry / Index": "Water Level: 8.42m (Alert: 8.00m)", "Risk Tier": "HIGH"},
            {"Timestamp": "25 Mins Ago", "Region": "North Forest Zone 2", "Hazard Type": "Thermal Hotspot", "Telemetry / Index": "Temp: 388 Kelvin (High Flame Prob.)", "Risk Tier": "CRITICAL"},
            {"Timestamp": "1 Hour Ago", "Region": "Coastal Harbor Reach", "Hazard Type": "Wind Sheer Spike", "Telemetry / Index": "Gusts: 104 km/h (Surge Risk)", "Risk Tier": "MODERATE"},
            {"Timestamp": "2 Hours Ago", "Region": "Highland Ridge Block B", "Hazard Type": "Soil Saturation", "Telemetry / Index": "Moisture: 92% (Mudslide Danger)", "Risk Tier": "HIGH"},
        ])
        st.dataframe(anomaly_df, use_container_width=True)

    # --------------------------------------------------------------------------
    # SUB-TAB 1.2: PREDICTIVE AI RISK MODEL & EARLY WARNING
    # --------------------------------------------------------------------------
    with tab_predictive:
        st.subheader("Predictive AI Risk Analytics & Simulation Engine")
        st.markdown(
            "The AI predictive engine continuously evaluates meteorological, hydrological, "
            "and satellite sensor feeds to forecast disaster probability before impact occurs."
        )

        col_sim, col_metrics = st.columns([1, 1])

        with col_sim:
            st.markdown("#### Interactive Risk Simulator")
            st.caption("Adjust forecast variables to simulate prospective hazard impact and observe automated alerts.")

            sim_rainfall = st.slider("Forecasted Rainfall (mm in 24 Hours)", min_value=0, max_value=400, value=145, step=5)
            sim_wind = st.slider("Sustained Wind Speed / Gusts (km/h)", min_value=10, max_value=220, value=85, step=5)
            sim_river_gauge = st.slider("River Gauge Height Above Normal (Meters)", min_value=0.0, max_value=12.0, value=7.8, step=0.1)
            sim_temp = st.slider("Ambient Temperature (°C)", min_value=10, max_value=50, value=38, step=1)
            sim_soil_moisture = st.slider("Soil Moisture Saturation (%)", min_value=10, max_value=100, value=82, step=2)

            # Predictive Calculation Formulas (Simulation Model)
            # 1. Flood Risk %
            flood_score = min(100, int((sim_rainfall * 0.35) + (sim_river_gauge * 6.5) + (sim_soil_moisture * 0.25)))
            # 2. Wildfire Risk %
            wildfire_score = min(100, max(0, int((sim_temp * 1.6) + (sim_wind * 0.3) - (sim_soil_moisture * 0.5) - (sim_rainfall * 0.4))))
            # 3. Cyclone Impact Score %
            cyclone_score = min(100, int((sim_wind * 0.45) + (sim_rainfall * 0.25)))

        with col_metrics:
            st.markdown("#### AI Risk Probability Forecast")

            col_f, col_w, col_c = st.columns(3)
            with col_f:
                st.metric("Flood Risk", f"{flood_score}%", delta=f"{'+' if flood_score > 60 else ''}{flood_score - 50}%")
            with col_w:
                st.metric("Wildfire Risk", f"{wildfire_score}%", delta=f"{'+' if wildfire_score > 50 else ''}{wildfire_score - 40}%")
            with col_c:
                st.metric("Cyclone Risk", f"{cyclone_score}%", delta=f"{'+' if cyclone_score > 55 else ''}{cyclone_score - 45}%")

            # Determine dominant threat and auto-trigger early warnings
            highest_risk = max(flood_score, wildfire_score, cyclone_score)

            if highest_risk >= 75:
                threat_name = "FLOOD" if highest_risk == flood_score else ("WILDFIRE" if highest_risk == wildfire_score else "CYCLONE")
                st.error(
                    f"🚨 **CRITICAL PRE-DISASTER ALERT TRIGGERED!**\n\n"
                    f"Automated risk threshold exceeded: **{threat_name} RISK AT {highest_risk}%**.\n\n"
                    "Automated early-warning sirens and responder pre-dispatch staging have been initiated."
                )
                if st.button("Transmit Early Warning Alert to Emergency Dispatch Console"):
                    new_disp = {
                        "dispatch_id": f"AUTO-{datetime.now().strftime('%H%M%S')}",
                        "hazard_trigger": f"Predictive AI Trigger: {threat_name} Risk {highest_risk}%",
                        "unit": "Emergency Pre-Disaster Staging Unit",
                        "destination": "High Risk Sector Alpha",
                        "status": "Staged",
                        "time_triggered": datetime.now().strftime("%H:%M:%S"),
                    }
                    st.session_state.automated_dispatches.insert(0, new_disp)
                    st.success("Automated Pre-Disaster Staging Dispatched!")
            elif highest_risk >= 50:
                st.warning(
                    f"⚠️ **ELEVATED HAZARD WATCH**: Risk models predict significant likelihood ({highest_risk}%). "
                    "Recommend clearing drainage channels and issuing advisory notifications to citizens."
                )
            else:
                st.success("✅ **STABLE ENVIRONMENTAL CONDITIONS**: All simulated hazard indices are within safe baseline tolerances.")

            # Gauge Visualization
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=highest_risk,
                title={'text': "Composite Hazard Index (Max Threat Level)"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#ff4b4b" if highest_risk >= 75 else ("#ffa500" if highest_risk >= 50 else "#00c0f2")},
                    'steps': [
                        {'range': [0, 50], 'color': "#e8f4f8"},
                        {'range': [50, 75], 'color': "#fff2cc"},
                        {'range': [75, 100], 'color': "#fce8e6"},
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 75
                    }
                }
            ))
            fig_gauge.update_layout(height=260, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_gauge, use_container_width=True)

        # 48-Hour Historical & Forecast Trend Chart
        st.markdown("#### 48-Hour Multi-Hazard Prediction Timeline")
        hours_timeline = [f"T-{48 - i*4}h" for i in range(12)] + ["Current"] + [f"T+{i*4}h" for i in range(1, 6)]
        trend_data = pd.DataFrame({
            "Timeline": hours_timeline,
            "Flood Risk Probability (%)": [20, 22, 25, 28, 35, 42, 48, 55, 62, 70, 78, 85, flood_score,
                                           min(100, flood_score + 6), min(100, flood_score + 10),
                                           max(0, flood_score + 4), max(0, flood_score - 5), max(0, flood_score - 15)],
            "Wildfire Spread Index (%)": [40, 42, 45, 48, 52, 50, 48, 45, 40, 38, 35, 30, wildfire_score,
                                          max(0, wildfire_score - 4), max(0, wildfire_score - 8),
                                          max(0, wildfire_score - 15), max(0, wildfire_score - 20), max(0, wildfire_score - 25)],
            "Cyclone Intensity Index (%)": [15, 15, 18, 20, 22, 25, 30, 40, 52, 65, 72, 80, cyclone_score,
                                            min(100, cyclone_score + 8), min(100, cyclone_score + 12),
                                            min(100, cyclone_score + 5), max(0, cyclone_score - 10), max(0, cyclone_score - 25)],
        })
        fig_trend = px.line(
            trend_data,
            x="Timeline",
            y=["Flood Risk Probability (%)", "Wildfire Spread Index (%)", "Cyclone Intensity Index (%)"],
            markers=True,
            title="Hazard Probability Evolution (Past 48h to Next 24h Forecast)"
        )
        fig_trend.update_layout(height=340, legend_title_text="Hazard Category")
        st.plotly_chart(fig_trend, use_container_width=True)

    # --------------------------------------------------------------------------
    # SUB-TAB 1.3: PREPAREDNESS GUIDELINES & EVACUATION HUB
    # --------------------------------------------------------------------------
    with tab_preparedness:
        st.subheader("Community Preparedness & Evacuation Route Planning")
        st.markdown(
            "Empowering citizens and authorities with actionable early-mitigation checklists, "
            "safe shelter locations, and pre-planned evacuation corridors before disaster strikes."
        )

        col_chk, col_map = st.columns([1, 1])

        with col_chk:
            hazard_guide = st.selectbox(
                "Select Pre-Disaster Hazard Checklist:",
                ["🌊 Riverine & Flash Floods", "🌪️ Cyclones & High-Wind Storms", "🔥 Wildfires & Forest Conflagrations", "🏚️ Earthquakes & Structural Tremors"]
            )

            if "Flood" in hazard_guide:
                st.markdown("**Essential Pre-Flood Mitigation Checklist:**")
                st.checkbox("Identify nearest elevated evacuation shelter (> 15m elevation)")
                st.checkbox("Store 72 hours of sealed drinking water (4 liters per person per day)")
                st.checkbox("Elevate electrical appliances and circuit breakers above projected flood line")
                st.checkbox("Clear local street drainage culverts and stormwater drains of debris")
                st.checkbox("Prepare a buoyant dry-bag with national IDs, prescriptions, and power banks")
                st.checkbox("Install one-way backflow valves on home sewage pipelines")
            elif "Cyclone" in hazard_guide:
                st.markdown("**Essential Pre-Cyclone Mitigation Checklist:**")
                st.checkbox("Board up or tape large glass windows and reinforce external doors")
                st.checkbox("Trim weak tree branches within 10 meters of overhead utility lines")
                st.checkbox("Secure rooftop solar panels, tin sheds, and outdoor water tanks")
                st.checkbox("Charge all radio transceivers, flashlights, and mobile devices")
                st.checkbox("Anchor small fishing vessels or move them inland past high-tide mark")
            elif "Wildfire" in hazard_guide:
                st.markdown("**Essential Pre-Wildfire Mitigation Checklist:**")
                st.checkbox("Create a 30-meter defensible space by clearing dry brush and pine needles")
                st.checkbox("Clean dry leaves from rooftop gutters and under wooden deck structures")
                st.checkbox("Shut off residential LP gas cylinders and main fuel lines")
                st.checkbox("Prepare N95 smoke-respirator masks and goggles for all family members")
                st.checkbox("Keep garden water hoses connected to external spigots with reliable pressure")
            else:
                st.markdown("**Essential Pre-Earthquake Mitigation Checklist:**")
                st.checkbox("Bolt heavy bookcases, water heaters, and tall storage cabinets to wall studs")
                st.checkbox("Identify safe 'Drop, Cover, and Hold On' locations in every room")
                st.checkbox("Locate and practice manual shutoff for household gas and water mains")
                st.checkbox("Avoid placing heavy mirrors or framed artwork directly above sleeping areas")

        with col_map:
            st.markdown("#### Nearest Designated Safe Evacuation Shelters")
            st.caption("Pre-surveyed relief camps equipped with food rations, backup power, and medical posts.")

            shelters_data = pd.DataFrame([
                {"name": "Central High-Ground Stadium Shelter", "lat": 19.0760 + 0.02, "lon": 72.8777 + 0.015, "Capacity": "2,500 Beds", "Status": "Open & Stocked"},
                {"name": "District Polytechnic Relief Camp", "lat": 19.0760 - 0.015, "lon": 72.8777 - 0.02, "Capacity": "1,200 Beds", "Status": "Open & Stocked"},
                {"name": "North Hill Community Evacuation Center", "lat": 19.0760 + 0.035, "lon": 72.8777 - 0.01, "Capacity": "800 Beds", "Status": "Standby"},
                {"name": "St. Jude Naval Base Shelter", "lat": 19.0760 - 0.025, "lon": 72.8777 + 0.03, "Capacity": "3,000 Beds", "Status": "Open & Stocked"},
            ])
            st.map(shelters_data, latitude="lat", longitude="lon", zoom=11)
            st.dataframe(shelters_data[["name", "Capacity", "Status"]], use_container_width=True)


# ==============================================================================
# 5. MODULE 2: DURING DISASTER (AUTOMATED RESPONSE & LOW-BANDWIDTH SOS)
# ==============================================================================
elif app_phase == "2. DURING Disaster (Active Response & SOS)":
    st.title("⚡ Phase 2: DURING DISASTER (Active Response & Relief Initiation)")
    st.markdown(
        "**Core Focus**: When disaster strikes, manual victim reporting is severely hindered. "
        "This module delivers **Automated First Responder Help Initiation** triggered by sensor risk breaches, "
        "paired with an **ultra-lightweight, low-bandwidth 1-click Emergency SOS beacon**."
    )

    col_auto, col_sos = st.columns([1, 1])

    # --------------------------------------------------------------------------
    # SUB-MODULE 2.1: AUTOMATED HELP INITIATION & DISPATCH
    # --------------------------------------------------------------------------
    with col_auto:
        st.subheader("🤖 Automated Help Initiation & Dispatch")
        st.markdown(
            "Rather than waiting for manual reports from victims in distress, the system "
            "automatically deploys emergency rescue resources to high-risk coordinates identified in Phase 1."
        )

        st.markdown("#### Trigger New Automated Response")
        with st.form("auto_dispatch_form"):
            trigger_reason = st.selectbox(
                "Triggering Sensor / Threat Event:",
                [
                    "Hydrological River Gauge Breach (> 8.5m)",
                    "Satellite Thermal Wildfire Cluster (> 380K)",
                    "Cyclone Gust Velocity (> 110 km/h)",
                    "UAV Drone Detected Rising Water Cutoff",
                    "Flash Flood Barrier Overflow Warning"
                ]
            )
            unit_to_deploy = st.selectbox(
                "Deploy Automated First Responder Unit:",
                [
                    "National Disaster Response Force (NDRF Flood Boat Squad)",
                    "Aerial Water-Dropper Squadron",
                    "Medical Rapid Triage Team",
                    "Civil Defense Amphibious Evacuation Squad",
                    "Heavy Clearance & Earthmover Unit"
                ]
            )
            target_sector = st.text_input("Target Geographical Sector:", value="Basin Sector 4 (Inundation Zone B)")

            submitted_auto = st.form_submit_button("🚨 Confirm Automated Dispatch Trigger", use_container_width=True)
            if submitted_auto:
                new_entry = {
                    "dispatch_id": f"DISP-{datetime.now().strftime('%M%S')}",
                    "hazard_trigger": trigger_reason,
                    "unit": unit_to_deploy,
                    "destination": target_sector,
                    "status": "Dispatched",
                    "time_triggered": datetime.now().strftime("%H:%M:%S"),
                }
                st.session_state.automated_dispatches.insert(0, new_entry)
                st.success(f"Dispatched {unit_to_deploy} to {target_sector}!")

        st.markdown("#### Live Emergency Dispatch Queue")
        disp_df = pd.DataFrame(st.session_state.automated_dispatches)
        st.dataframe(disp_df, use_container_width=True)

    # --------------------------------------------------------------------------
    # SUB-MODULE 2.2: LOW-BANDWIDTH EMERGENCY SOS BEACON
    # --------------------------------------------------------------------------
    with col_sos:
        st.subheader("🆘 Emergency SOS / Low-Bandwidth Beacon")
        st.markdown(
            "Designed for victims trapped in an active crisis with unstable connectivity. "
            "Transmits only essential telemetry with minimal data payload."
        )

        st.info("📶 Low-Bandwidth Mode Active. Minimal data footprint (< 2KB payload).")

        with st.form("emergency_sos_form"):
            st.markdown("**1-Click GPS Coordinate Ping**")
            col_lat, col_lon = st.columns(2)
            with col_lat:
                sos_lat = st.number_input("Latitude:", value=19.0760, format="%.5f")
            with col_lon:
                sos_lon = st.number_input("Longitude:", value=72.8777, format="%.5f")

            sos_triage = st.selectbox(
                "Primary Critical Condition (Triage Tag):",
                [
                    "Trapped by Rising Water / Flood",
                    "Critical Medical Need / Severe Injury",
                    "Trapped in Collapsed Building / Rubble",
                    "Elderly / Infant Without Food & Water",
                    "Surrounded by Active Wildfire Smoke"
                ]
            )

            sos_people = st.slider("Number of People Trapped:", min_value=1, max_value=25, value=3)
            sos_details = st.text_area(
                "Short Message (Landmark, Floor, Battery %):",
                placeholder="e.g., 2nd floor, blue roof house near old church. Battery 8% left.",
                max_chars=120
            )

            sos_submitted = st.form_submit_button("🔴 SEND EMERGENCY SOS DISTRESS BEACON", use_container_width=True)
            if sos_submitted:
                new_sos = {
                    "sos_id": f"SOS-{datetime.now().strftime('%M%S')}",
                    "latitude": sos_lat,
                    "longitude": sos_lon,
                    "triage": sos_triage,
                    "people_count": sos_people,
                    "details": sos_details if sos_details else "No additional notes.",
                    "status": "Transmitted - Rescue Queue #1",
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                }
                st.session_state.sos_signals.insert(0, new_sos)
                st.error(
                    f"🚨 **SOS BEACON TRANSMITTED SUCCESSFULLY!**\n\n"
                    f"Rescue Beacon Token: **{new_sos['sos_id']}**\n\n"
                    f"Coordinates: **({sos_lat:.4f}, {sos_lon:.4f})**\n\n"
                    "Stay calm. Keep your mobile device dry and preserve your battery. Emergency personnel have been pinged."
                )

        st.markdown("#### Active SOS Distress Signals")
        sos_df = pd.DataFrame(st.session_state.sos_signals)
        st.dataframe(sos_df[["sos_id", "triage", "people_count", "status", "timestamp"]], use_container_width=True)

        if not sos_df.empty:
            st.markdown("#### Geospatial SOS Beacon Cluster Map")
            st.map(sos_df, latitude="latitude", longitude="longitude", zoom=11)


# ==============================================================================
# 6. MODULE 3: AFTER DISASTER (REPORTING & RECOVERY) - EXISTING FEATURE REFINED
# ==============================================================================
elif app_phase == "3. AFTER Disaster (Reporting & Recovery)":
    st.title("🤝 Phase 3: AFTER DISASTER (Reporting & Recovery)")
    st.markdown(
        "**Core Focus**: Once the acute danger passes, communities transition to recovery. "
        "Log structural damages, request rebuilding supplies, and track relief distribution transparency."
    )

    tab_post_report, tab_recovery_track = st.tabs([
        "📝 Post-Disaster Damage & Needs Reporting",
        "📊 Resource & Relief Tracking Dashboard"
    ])

    # --------------------------------------------------------------------------
    # SUB-TAB 3.1: POST-DISASTER DAMAGE & SUPPLY REQUEST FORM
    # --------------------------------------------------------------------------
    with tab_post_report:
        st.subheader("Submit Post-Disaster Incident & Damage Report")
        st.markdown(
            "Citizens, community volunteers, and municipal officials can record infrastructure damage, "
            "utility failures, and specific relief aid requirements."
        )

        with st.form("post_disaster_report_form"):
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                rep_location = st.text_input("Exact Location / Neighborhood / Ward:", placeholder="e.g., Riverside Sector 2, Ward 14")
                rep_type = st.selectbox(
                    "Primary Type of Damage:",
                    [
                        "Residential Structural Collapse",
                        "Bridge / Road Washout",
                        "Drinking Water Pipeline Rupture",
                        "Power Grid / Electrical Transformer Outage",
                        "Agricultural Crop Flooding",
                        "Hospital / Clinic Flooding"
                    ]
                )
                rep_severity = st.selectbox("Assessed Severity:", ["Minor", "Moderate", "Severe", "Catastrophic"])

            with col_r2:
                rep_casualties = st.number_input("Known Injuries / Casualties:", min_value=0, max_value=500, value=0)
                rep_supplies = st.text_input(
                    "Specific Urgent Supplies Needed:",
                    placeholder="e.g., 500L Drinking Water, 50 Tarps, Chlorine Tablets"
                )
                rep_contact = st.text_input("Reporting Person / Official Contact:", placeholder="e.g., Ward Officer Sharma (+91-9876543210)")

            rep_notes = st.text_area("Detailed Damage Description & Access Route Status:")

            submitted_report = st.form_submit_button("Submit Post-Disaster Report", use_container_width=True)
            if submitted_report:
                if not rep_location:
                    st.error("Please specify the location of the incident.")
                else:
                    new_rep = {
                        "report_id": f"REP-{datetime.now().strftime('%M%S')}",
                        "location": rep_location,
                        "damage_type": rep_type,
                        "severity": rep_severity,
                        "casualties": rep_casualties,
                        "supplies_needed": rep_supplies if rep_supplies else "General Relief",
                        "status": "Logged & Awaiting Resource Assignment",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    }
                    st.session_state.damage_reports.insert(0, new_rep)
                    st.success(f"Damage Report **{new_rep['report_id']}** logged successfully! Municipal relief teams alerted.")

        st.markdown("#### Recently Logged Post-Disaster Incident Reports")
        st.dataframe(pd.DataFrame(st.session_state.damage_reports), use_container_width=True)

    # --------------------------------------------------------------------------
    # SUB-TAB 3.2: RELIEF & RECOVERY TRACKER DASHBOARD
    # --------------------------------------------------------------------------
    with tab_recovery_track:
        st.subheader("Resource & Relief Distribution Tracking")
        st.markdown(
            "Live transparent tracking of requested relief materials, dispatched humanitarian aid, "
            "and municipal infrastructure restoration progress."
        )

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric("Total Incident Reports", len(st.session_state.damage_reports), delta="+2 Today")
        with col_m2:
            st.metric("Displaced Citizens Sheltered", "4,380", delta="+350 Re-housed")
        with col_m3:
            st.metric("Water Rations Distributed", "14,500 L", delta="88% Target Met")
        with col_m4:
            st.metric("Power Grid Restoration", "76%", delta="+12% Restored")

        # Supply Fulfillment Progress
        st.markdown("#### Relief Supply Pipeline (Requested vs. Dispatched)")
        supply_records = []
        for item, vals in st.session_state.relief_inventory.items():
            pct = int((vals["dispatched"] / vals["requested"]) * 100) if vals["requested"] > 0 else 0
            supply_records.append({
                "Supply Category": item,
                "Requested Units": vals["requested"],
                "Dispatched Units": vals["dispatched"],
                "Fulfillment (%)": pct
            })
        supply_df = pd.DataFrame(supply_records)

        fig_supplies = px.bar(
            supply_df,
            x="Supply Category",
            y=["Requested Units", "Dispatched Units"],
            barmode="group",
            title="Relief Supplies Inventory Tracker",
            color_discrete_map={"Requested Units": "#ffa500", "Dispatched Units": "#00c0f2"}
        )
        fig_supplies.update_layout(height=340)
        st.plotly_chart(fig_supplies, use_container_width=True)

        st.dataframe(supply_df, use_container_width=True)

        # Rebuilding & Recovery Milestone Timeline
        st.markdown("#### Infrastructure Recovery Milestones")
        recovery_milestones = pd.DataFrame([
            {"Sector": "Road Network", "Progress": "92%", "Status": "All Main Highways Cleared of Mudslides", "Target Date": "Completed"},
            {"Sector": "Drinking Water", "Progress": "78%", "Status": "Chlorination Active in 14 of 18 Wards", "Target Date": "Next 48h"},
            {"Sector": "Electrical Grid", "Progress": "76%", "Status": "Main Substation Restored; Feeders Staged", "Target Date": "Next 24h"},
            {"Sector": "Cellular Networks", "Progress": "85%", "Status": "Portable COWs (Cell on Wheels) Deployed", "Target Date": "Active"},
        ])
        st.table(recovery_milestones)


# ==============================================================================
# 7. MODULE 4: API CONFIGURATION & ARCHITECTURE DOCUMENTATION
# ==============================================================================
elif app_phase == "4. System Settings & API Connectors":
    st.title("⚙️ System Settings & External API Connectors")
    st.markdown(
        "Configure live credentials for Earth observation satellites, real-time weather stations, "
        "and Google Earth Engine connectors for scalable production deployment."
    )

    col_api_conf, col_docs = st.columns([1, 1])

    with col_api_conf:
        st.subheader("API Keys & Environment Variables")
        with st.form("api_keys_form"):
            nasa_key = st.text_input("NASA Earthdata / FIRMS API Key:", type="password", placeholder="Paste NASA Earthdata Bearer Token")
            gee_project = st.text_input("Google Earth Engine Cloud Project ID:", placeholder="e.g., ee-disaster-resilience")
            openweather_key = st.text_input("OpenWeatherMap API Key:", type="password", placeholder="e.g., 32-character hexadecimal key")
            mapbox_token = st.text_input("Mapbox Public Token (Optional for 3D Topography):", type="password", placeholder="pk.eyJ...")

            saved = st.form_submit_button("Save & Test API Connectors", use_container_width=True)
            if saved:
                st.success("API configuration stored in session. Using mock fallback if keys are omitted.")

        st.markdown("#### Active Data Sources Status")
        st.markdown(
            "- **NASA FIRMS**: Simulated (Ready for live key)\n"
            "- **Copernicus Sentinel-2 (NDWI/NDVI)**: Simulated\n"
            "- **OpenWeather One Call**: Simulated\n"
            "- **State Disaster Response Dispatch Hub**: In-Memory Active"
        )

    with col_docs:
        st.subheader("System Architecture & Data Flow")
        st.markdown(
            """
            ```
            [NASA Earthdata / FIRMS / GEE]
                          │
                          ▼
            [1. BEFORE DISASTER ENGINE]
              ├── Satellite & Drone Imagery Analytics
              ├── AI Predictive Risk Simulation (Rain, Wind, Gauge)
              └── Automated Early Warning Triggers
                          │
                          ▼ (When Threat Score >= 75%)
            [2. DURING DISASTER CONSOLE]
              ├── Automated First Responder Dispatch
              └── Low-Bandwidth 1-Click SOS Beacons
                          │
                          ▼ (Post-Event Transition)
            [3. AFTER DISASTER RECOVERY]
              ├── Structural Damage Reports
              └── Transparent Relief Tracking
            ```
            """
        )
        st.info(
            "💡 **GitHub Deployment Tip**: Push this repository directly to GitHub and connect to "
            "[Streamlit Community Cloud](https://streamlit.io/cloud). All mock components work out-of-the-box."
        )

# ==============================================================================
# FOOTER
# ==============================================================================
st.markdown("---")
col_f1, col_f2 = st.columns([2, 1])
with col_f1:
    st.caption("ResQ Live Platform | Comprehensive Disaster Management System (Before, During, After)")
with col_f2:
    st.caption("Status: Operational | Streamlit Native Typography")

