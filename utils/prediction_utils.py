"""
prediction_utils.py
--------------------
Phase 1 core: turns satellite / drone imagery signals into a disaster risk
prediction, WITH an explainable breakdown of what fed into the score
(this is what gets shown under each zone card so the number isn't a mystery).

>>> REAL MODEL INTEGRATION POINT <
Replace `_analyze_indicators()` with a call to your trained model. Keep the
same return shape (a dict of factor_name -> 0-100 score) and everything else
downstream (risk level, charts, alerts) keeps working unchanged.
"""

import random
from datetime import datetime

# Each monitored region has a realistic bias toward certain disaster types,
# based on its actual geography - this replaces pure randomness with
# something that resembles how real regional risk modeling works.
REGION_PROFILES = {
    "Kerala Coast": {
        "types": ["Flood", "Cyclone"],
        "factors": ["Rainfall Anomaly", "River Level Rise", "Wind Speed Anomaly", "Storm Surge Risk"],
    },
    "Uttarakhand Himalayas": {
        "types": ["Landslide", "Glacial Lake Outburst", "Flash Flood"],
        "factors": ["Ground Deformation", "Slope Saturation", "Glacial Melt Rate", "Seismic Micro-tremors"],
    },
    "Odisha Coastline": {
        "types": ["Cyclone", "Flood"],
        "factors": ["Wind Speed Anomaly", "Storm Surge Risk", "Rainfall Anomaly", "Sea Surface Temp Anomaly"],
    },
    "Assam Brahmaputra Basin": {
        "types": ["Flood", "Flash Flood"],
        "factors": ["River Level Rise", "Rainfall Anomaly", "Upstream Discharge Rate", "Soil Saturation"],
    },
    "Sikkim Glacial Belt": {
        "types": ["Glacial Lake Outburst", "Landslide"],
        "factors": ["Glacial Melt Rate", "Lake Volume Change", "Ground Deformation", "Thermal Anomaly"],
    },
    "Himachal Hill Districts": {
        "types": ["Landslide", "Earthquake Aftershock Zone", "Flash Flood"],
        "factors": ["Slope Saturation", "Ground Deformation", "Seismic Micro-tremors", "Rainfall Anomaly"],
    },
}

DEFAULT_PROFILE = {
    "types": ["Flood", "Landslide", "Wildfire", "Heatwave"],
    "factors": ["Rainfall Anomaly", "Thermal Anomaly", "Ground Deformation", "Vegetation Stress Index"],
}


def _analyze_indicators(region):
    """
    Placeholder for real CV/ML inference on satellite or drone imagery.
    In production this scores each indicator from actual image analysis
    (e.g. change-detection for water extent, InSAR for ground deformation,
    thermal-band analysis for heat/fire signatures). Here each indicator
    gets an independent random score so the app is fully demoable; swap
    this function's body for your model's real output.
    """
    profile = REGION_PROFILES.get(region, DEFAULT_PROFILE)
    disaster_type = random.choice(profile["types"])

    factors = {}
    for f in profile["factors"]:
        factors[f] = round(random.uniform(5, 98), 1)

    # Overall risk score = weighted average, weighted toward the two
    # strongest indicators (mimics how a real fused model would behave -
    # one or two dominant signals usually drive the alert).
    sorted_scores = sorted(factors.values(), reverse=True)
    if len(sorted_scores) >= 2:
        risk_score = round(sorted_scores[0] * 0.45 + sorted_scores[1] * 0.30
                            + sum(sorted_scores[2:]) / max(len(sorted_scores[2:]), 1) * 0.25, 1)
    else:
        risk_score = round(sum(sorted_scores) / len(sorted_scores), 1)

    return risk_score, disaster_type, factors


def run_disaster_prediction(region="India", lat=20.5937, lon=78.9629, source="satellite"):
    """Main entry point used by the Phase 1 dashboard."""
    risk_score, disaster_type, factors = _analyze_indicators(region)

    if risk_score >= 80:
        risk_level = "CRITICAL"
    elif risk_score >= 55:
        risk_level = "HIGH"
    elif risk_score >= 30:
        risk_level = "MODERATE"
    else:
        risk_level = "LOW"

    confidence = round(random.uniform(70, 98), 1)
    radius = round(random.uniform(2, 60), 1)
    eta = round(random.uniform(1, 48), 1) if risk_level in ("HIGH", "CRITICAL") else None

    top_factor = max(factors, key=factors.get)

    return {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "disaster_type": disaster_type,
        "confidence": confidence,
        "affected_radius_km": radius,
        "eta_hours": eta,
        "source": source,
        "region": region,
        "lat": lat,
        "lon": lon,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "factors": factors,
        "notes": (
            f"{source.title()} imagery over {region} shows {disaster_type.lower()} indicators; "
            f"strongest signal is {top_factor} ({factors[top_factor]}/100)."
        ),
    }


def generate_live_feed(regions):
    """Runs predictions across every monitored region - drives the map + charts."""
    return [run_disaster_prediction(region=r["name"], lat=r["lat"], lon=r["lon"]) for r in regions]
