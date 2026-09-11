# RESQ — AI Disaster Prediction & Response Alert System

RESQ is built as an **alert system**, not a dashboard/brochure: it opens straight
into live risk status, a big SOS button, a siren, and push notifications —
not a marketing page.

## 3 Phases

| Phase | Focus | What it does |
|---|---|---|
| **1 · Predict & Monitor** (core focus) | AI + satellite/drone imagery | Continuously "scans" monitored zones, scores risk, plots it on a live map, fires a siren + browser notification the moment risk crosses HIGH/CRITICAL, and shows type/risk breakdowns via pie/bar/gauge charts. |
| **2 · Ground Reports** | Human input | People near a flagged zone report disaster type, people affected, and what help (medical, food, shelter, rescue...) is needed. |
| **3 · Resource Ops** | Response | Live hospital/police/shelter/rescue-team registry, filterable, and auto-matched (nearest-first) to any HIGH/CRITICAL zone. |

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Push this whole folder to a GitHub repo.
2. On https://share.streamlit.io, "New app" → point it at `app.py`.
3. Done — `requirements.txt` is picked up automatically.

## Low-connectivity design

- **Lite Mode** toggle in the sidebar swaps the full Leaflet map for a
  tiny Plotly `scattergeo` plot (a few KB vs. many map tiles).
- All data is loaded once via `st.cache_data` — no repeated re-fetching.
- The logo and siren sound ship locally in `/assets` — nothing pulled from
  an external CDN at runtime.
- No large frontend JS framework — Streamlit's server-rendered components
  keep payload small per interaction.

## Plugging in a real AI model

All prediction logic lives in `utils/prediction_utils.py`, behind
`run_disaster_prediction()`. Right now it **simulates** an anomaly score so
the whole pipeline (map, alerts, charts, resource matching) is fully wired
and demoable. Swap the body of `_simulate_image_analysis()` for your actual
model call (e.g. a segmentation/classification CNN run on satellite tiles,
or a hosted inference endpoint) — keep the same return schema and nothing
else in the app needs to change.

## File structure

```
RESQ/
├── app.py                     # main Streamlit app (all 3 phases)
├── requirements.txt
├── assets/
│   ├── logo.png
│   └── alert_siren.wav        # generated, unique 2-tone + sweep siren
├── data/
│   ├── historical_disasters.csv   # Nepal 2015, Kerala 2018, Turkey-Syria 2023, etc.
│   └── resources.csv              # sample hospitals / police / shelters / rescue teams
└── utils/
    ├── prediction_utils.py    # AI prediction — swap in your real model here
    ├── alert_utils.py         # siren + browser notification + SOS button CSS
    └── map_utils.py           # full (folium) and lite (plotly) map builders
```

## Notes

- The Web Notification API requires the browser tab to grant permission —
  most browsers will prompt on first alert.
- Autoplay audio can be blocked by some browsers until the user has
  interacted with the page once (a browser security rule, not a bug).
- `resources.csv` and `historical_disasters.csv` are sample data — swap
  in your real, verified data before going to production, especially the
  historical incident summaries.
