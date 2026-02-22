from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np
from pathlib import Path

app = FastAPI()

# ✅ Allow POST from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

DATA_PATH = Path("q-vercel-latency.json")

def load_data():
    with open(DATA_PATH) as f:
        return json.load(f)

@app.post("/")
async def telemetry(payload: dict):
    regions = payload["regions"]
    threshold = payload["threshold_ms"]

    data = load_data()
    result = {}

    for region in regions:
        rows = [r for r in data if r["region"] == region]

        lat = np.array([r["latency_ms"] for r in rows])
        up = np.array([r["uptime_pct"] for r in rows])

        result[region] = {
            "avg_latency": float(lat.mean()),
            "p95_latency": float(np.percentile(lat, 95)),
            "avg_uptime": float(up.mean()),
            "breaches": int((lat > threshold).sum())
        }

    return result