"""
map_utils.py
------------
Builds the live monitoring map. Two modes:
  - "full": real Leaflet/OpenStreetMap map via folium (richer, heavier).
  - "lite": plotly scatter-geo map, much lighter payload for low-connectivity
    users (no external tile requests after the base render).
"""

import folium
import plotly.graph_objects as go

RISK_COLORS = {
    "CRITICAL": "#b30000",
    "HIGH": "#ff6a00",
    "MODERATE": "#ffb800",
    "LOW": "#1fa855",
}


def build_full_map(predictions, resources=None, center=(22.9734, 78.6569), zoom=5):
    m = folium.Map(location=center, zoom_start=zoom, tiles="CartoDB dark_matter", control_scale=True)

    # Satellite/drone monitored regions with risk prediction
    for p in predictions:
        color = RISK_COLORS.get(p["risk_level"], "#888")
        popup_html = (
            f"<b>{p['region']}</b><br>"
            f"Type: {p['disaster_type']}<br>"
            f"Risk: {p['risk_level']} ({p['risk_score']})<br>"
            f"Confidence: {p['confidence']}%<br>"
            f"Radius: {p['affected_radius_km']} km<br>"
            f"Source: {p['source']}<br>"
            f"Detected: {p['timestamp']}"
        )
        folium.Circle(
            location=(p["lat"], p["lon"]),
            radius=p["affected_radius_km"] * 1000,
            color=color,
            fill=True,
            fill_opacity=0.25,
            weight=2,
        ).add_to(m)
        folium.Marker(
            location=(p["lat"], p["lon"]),
            popup=folium.Popup(popup_html, max_width=260),
            tooltip=f"{p['region']} - {p['risk_level']}",
            icon=folium.Icon(color="red" if p["risk_level"] in ("CRITICAL", "HIGH") else "orange", icon="warning-sign"),
        ).add_to(m)

    # Nearby resources - hospitals, police, shelters
    if resources is not None:
        icon_map = {
            "Hospital": ("plus-sign", "blue"),
            "Police Station": ("info-sign", "darkblue"),
            "Shelter": ("home", "green"),
            "Response Team": ("flag", "cadetblue"),
            "Fire/Rescue": ("fire", "red"),
        }
        for _, row in resources.iterrows():
            icon_name, icon_color = icon_map.get(row["type"], ("info-sign", "gray"))
            folium.Marker(
                location=(row["lat"], row["lon"]),
                popup=f"{row['name']} ({row['type']})<br>Capacity: {row['capacity']}<br>Contact: {row['contact']}",
                tooltip=row["name"],
                icon=folium.Icon(color=icon_color, icon=icon_name),
            ).add_to(m)

    return m


def build_lite_map(predictions):
    """Low-bandwidth fallback: a single lightweight plotly scattergeo figure."""
    lats = [p["lat"] for p in predictions]
    lons = [p["lon"] for p in predictions]
    colors = [RISK_COLORS.get(p["risk_level"], "#888") for p in predictions]
    text = [f"{p['region']}: {p['risk_level']} - {p['disaster_type']}" for p in predictions]
    sizes = [max(10, p["risk_score"] / 3) for p in predictions]

    fig = go.Figure(go.Scattergeo(
        lat=lats, lon=lons, text=text,
        mode="markers",
        marker=dict(size=sizes, color=colors, line=dict(width=1, color="white")),
    ))
    fig.update_geos(
        scope="asia",
        showcountries=True, countrycolor="#444",
        showland=True, landcolor="#1a1a1a",
        showocean=True, oceancolor="#0b0f14",
        bgcolor="rgba(0,0,0,0)",
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        height=420,
    )
    return fig
