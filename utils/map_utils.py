"""
map_utils.py
------------
Builds the live monitoring map using REAL satellite imagery tiles
(Esri World Imagery - free, no API key) so it actually looks like a
satellite view rather than a generic basemap.
"""

import folium

RISK_COLORS = {
    "CRITICAL": "#ff1f1f",
    "HIGH": "#ff6a00",
    "MODERATE": "#ffcc00",
    "LOW": "#2ecc71",
}

ESRI_SATELLITE_URL = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
ESRI_ATTR = "Tiles &copy; Esri &mdash; Source: Esri, Maxar, Earthstar Geographics"


def build_full_map(predictions, resources=None, center=(22.9734, 78.6569), zoom=5):
    m = folium.Map(location=center, zoom_start=zoom, tiles=None, control_scale=True)
    folium.TileLayer(tiles=ESRI_SATELLITE_URL, attr=ESRI_ATTR, name="Satellite", overlay=False).add_to(m)
    # Light label layer on top so region/city names stay readable over imagery.
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
        attr=ESRI_ATTR, name="Labels", overlay=True, control=False,
    ).add_to(m)

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
            color=color, fill=True, fill_opacity=0.25, weight=2,
        ).add_to(m)
        folium.Marker(
            location=(p["lat"], p["lon"]),
            popup=folium.Popup(popup_html, max_width=260),
            tooltip=f"{p['region']} - {p['risk_level']}",
            icon=folium.Icon(color="red" if p["risk_level"] in ("CRITICAL", "HIGH") else "orange", icon="warning-sign"),
        ).add_to(m)

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


def build_history_map(history_df):
    m = folium.Map(location=(20.5, 78.9), zoom_start=3, tiles=None)
    folium.TileLayer(tiles=ESRI_SATELLITE_URL, attr=ESRI_ATTR, name="Satellite", overlay=False).add_to(m)
    sev_color = {"Critical": "#b30000", "High": "#ff6a00", "Medium": "#ffb800", "Low": "#1fa855"}
    for _, row in history_df.iterrows():
        folium.CircleMarker(
            location=(row["lat"], row["lon"]),
            radius=6 + (row["deaths"] ** 0.25),
            color=sev_color.get(row["severity"], "#888"),
            fill=True, fill_opacity=0.75,
            popup=f"<b>{row['name']}</b><br>{row['date']}<br>Deaths: {row['deaths']}<br>{row['summary']}",
            tooltip=row["name"],
        ).add_to(m)
    return m
