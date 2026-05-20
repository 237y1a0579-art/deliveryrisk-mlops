from __future__ import annotations

import csv
import os
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from services.api.app.model_loader import load_model
from services.api.app.prompts import choose_action, risk_band
from services.api.app.schemas import OrderFeatures, PredictionResponse

app = FastAPI(title="DeliveryRisk Prediction API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Instrumentator().instrument(app).expose(app)

MODEL, FEATURE_COLUMNS, MODEL_SOURCE = load_model()


def to_model_frame(payload: OrderFeatures) -> pd.DataFrame:
    raw = payload.model_dump()
    frame = pd.DataFrame([raw])
    frame = pd.get_dummies(frame, columns=["zone", "weather"], dtype=int)

    for column in FEATURE_COLUMNS:
        if column not in frame.columns:
            frame[column] = 0

    return frame[FEATURE_COLUMNS]


def append_inference_log(payload: OrderFeatures, probability: float, band: str) -> None:
    path = Path(os.getenv("INFERENCE_LOG_PATH", "data/production/inference_log.csv"))
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists()

    row = payload.model_dump()
    row.update(
        {
            "event_timestamp": datetime.now(timezone.utc).isoformat(),
            "late_delivery_probability": probability,
            "risk_band": band,
        }
    )

    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if write_header:
            writer.writeheader()
        writer.writerow(row)


@app.get("/health")
@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "model_source": MODEL_SOURCE}


@app.get("/")
def root() -> dict[str, str]:
    return {
        "project": "DeliveryRisk MLOps",
        "service": "Prediction API",
        "docs": "/docs",
        "health": "/health",
    }


@app.post("/predict", response_model=PredictionResponse)
@app.post("/api/predict", response_model=PredictionResponse)
def predict(payload: OrderFeatures) -> PredictionResponse:
    frame = to_model_frame(payload)
    probability = float(MODEL.predict_proba(frame)[0, 1])
    band = risk_band(probability)
    append_inference_log(payload, probability, band)
    return PredictionResponse(
        order_id=payload.order_id,
        late_delivery_probability=round(probability, 4),
        risk_band=band,
        recommended_action=choose_action(probability, payload.weather, payload.driver_supply),
        model_source=MODEL_SOURCE,
    )
