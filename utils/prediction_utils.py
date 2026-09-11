"""
prediction_utils.py
--------------------
Phase 1 core: takes satellite / drone imagery (or, for now, simulated sensor
readings standing in for imagery) and returns a disaster risk prediction.

>>> REAL MODEL INTEGRATION POINT <<<
Replace `run_disaster_prediction()` internals with a call to your trained
model (e.g. a CNN/segmentation model for satellite imagery, a time-series
model for sensor fusion, or a hosted inference endpoint). Keep the same
return schema so the rest of the app keeps working unchanged.

Expected return schema:
{
    "risk_level": "LOW" | "MODERATE" | "HIGH" | "CRITICAL",
    "risk_score": float 0-100,
    "disaster_type": str,
    "confidence": float 0-100,
    "affected_radius_km": float,
    "eta_hours": float or None,   # estimated time to impact, if predictable
    "source": "satellite" | "drone" | "fused",
    "notes": str
}
"""

import random
import time
from datetime import datetime

DISASTER_TYPES = [
    "Flood", "Landslide", "Cyclone", "Wildfire",
    "Earthquake Aftershock Zone", "Glacial Lake Outburst", "Heatwave"
]


def _simulate_image_analysis(image_bytes=None, region="India"):
    """
    Placeholder for actual CV/ML inference on satellite or drone imagery.
    In production this function would:
      1. Preprocess the image (tiling, normalization, cloud masking).
      2. Run it through a trained segmentation/classification model
         (e.g. U-Net for flood extent, change-detection CNN for landslides).
      3. Return anomaly scores per region/grid-cell.
    Here we simulate a plausible output so the UI/alerting pipeline can be
    fully built and demoed end-to-end before the real model is plugged in.
    """
    random.seed(int(time.time() * 1000) % 100000)
    anomaly_score = random.uniform(0, 100)
    disaster_type = random.choice(DISASTER_TYPES)
    return anomaly_score, disaster_type


def run_disaster_prediction(region="India", lat=20.5937, lon=78.9629,
                             image_bytes=None, source="satellite"):
    """Main entry point used by the Phase 1 dashboard."""
    anomaly_score, disaster_type = _simulate_image_analysis(image_bytes, region)

    if anomaly_score >= 80:
        risk_level = "CRITICAL"
    elif anomaly_score >= 55:
        risk_level = "HIGH"
    elif anomaly_score >= 30:
        risk_level = "MODERATE"
    else:
        risk_level = "LOW"

    confidence = round(random.uniform(70, 98), 1)
    radius = round(random.uniform(2, 60), 1)
    eta = round(random.uniform(1, 48), 1) if risk_level in ("HIGH", "CRITICAL") else None

    return {
        "risk_level": risk_level,
        "risk_score": round(anomaly_score, 1),
        "disaster_type": disaster_type,
        "confidence": confidence,
        "affected_radius_km": radius,
        "eta_hours": eta,
        "source": source,
        "region": region,
        "lat": lat,
        "lon": lon,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "notes": (
            f"{source.title()} imagery analysis over {region} flagged anomalies "
            f"consistent with early-stage {disaster_type.lower()} indicators."
        ),
    }


def generate_live_feed(regions):
    """Runs predictions across multiple monitored regions - used for the map."""
    results = []
    for r in regions:
        pred = run_disaster_prediction(region=r["name"], lat=r["lat"], lon=r["lon"])
        results.append(pred)
    return results
