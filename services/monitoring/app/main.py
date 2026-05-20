from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from scipy.stats import ks_2samp

app = FastAPI(title="DeliveryRisk Drift Service", version="0.1.0")
Instrumentator().instrument(app).expose(app)


NUMERIC_FEATURES = [
    "distance_km",
    "basket_value",
    "prep_minutes",
    "driver_supply",
    "traffic_index",
    "promised_minutes",
    "customer_late_rate_30d",
    "merchant_late_rate_30d",
    "zone_late_rate_30d",
]


def psi(expected: pd.Series, actual: pd.Series, buckets: int = 10) -> float:
    expected = expected.dropna().astype(float)
    actual = actual.dropna().astype(float)
    if expected.empty or actual.empty:
        return 0.0

    quantiles = np.linspace(0, 1, buckets + 1)
    breakpoints = np.unique(np.quantile(expected, quantiles))
    if len(breakpoints) <= 2:
        return 0.0

    expected_counts, _ = np.histogram(expected, bins=breakpoints)
    actual_counts, _ = np.histogram(actual, bins=breakpoints)
    expected_pct = np.maximum(expected_counts / max(expected_counts.sum(), 1), 0.0001)
    actual_pct = np.maximum(actual_counts / max(actual_counts.sum(), 1), 0.0001)
    return float(np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct)))


def load_frame(path: str) -> pd.DataFrame:
    data_path = Path(path)
    if not data_path.exists():
        return pd.DataFrame()
    if data_path.suffix == ".csv":
        return pd.read_csv(data_path)
    return pd.read_parquet(data_path)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/drift/run")
@app.get("/drift/run")
def run_drift() -> dict[str, object]:
    reference_path = os.getenv("REFERENCE_DATA_PATH", "data/reference/reference_features.parquet")
    inference_path = os.getenv("INFERENCE_LOG_PATH", "data/production/inference_log.csv")
    report_path = Path(os.getenv("DRIFT_REPORT_PATH", "reports/drift_report.json"))
    report_path.parent.mkdir(parents=True, exist_ok=True)

    reference = load_frame(reference_path)
    current = load_frame(inference_path)
    if reference.empty or current.empty:
        return {
            "status": "waiting_for_data",
            "reference_rows": int(len(reference)),
            "current_rows": int(len(current)),
        }

    feature_reports = {}
    for feature in NUMERIC_FEATURES:
        if feature not in reference.columns or feature not in current.columns:
            continue
        ks = ks_2samp(reference[feature].dropna(), current[feature].dropna())
        feature_reports[feature] = {
            "psi": round(psi(reference[feature], current[feature]), 4),
            "ks_p_value": round(float(ks.pvalue), 6),
            "drifted": bool(ks.pvalue < 0.05),
        }

    max_psi = max((item["psi"] for item in feature_reports.values()), default=0.0)
    drifted_features = [name for name, item in feature_reports.items() if item["drifted"] or item["psi"] >= 0.25]
    status = "drift_detected" if drifted_features else "ok"
    payload = {
        "status": status,
        "reference_rows": int(len(reference)),
        "current_rows": int(len(current)),
        "max_psi": max_psi,
        "drifted_features": drifted_features,
        "features": feature_reports,
    }
    report_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload
