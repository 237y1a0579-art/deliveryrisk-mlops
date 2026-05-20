from __future__ import annotations

import os
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


class HeuristicModel:
    feature_columns = [
        "order_id",
        "customer_id",
        "merchant_id",
        "distance_km",
        "basket_value",
        "prep_minutes",
        "driver_supply",
        "traffic_index",
        "promised_minutes",
        "customer_late_rate_30d",
        "merchant_late_rate_30d",
        "zone_late_rate_30d",
        "zone_central",
        "zone_north",
        "zone_south",
        "zone_east",
        "zone_west",
        "weather_clear",
        "weather_rain",
        "weather_storm",
        "weather_heat",
    ]

    def predict_proba(self, frame: pd.DataFrame) -> np.ndarray:
        score = (
            -2.9
            + 0.18 * frame["distance_km"].to_numpy()
            + 0.05 * frame["prep_minutes"].to_numpy()
            + 1.4 * frame["traffic_index"].to_numpy()
            - 1.2 * frame["driver_supply"].to_numpy()
            + 1.0 * frame["weather_storm"].to_numpy()
            + 0.45 * frame["weather_rain"].to_numpy()
            + 0.9 * frame["merchant_late_rate_30d"].to_numpy()
        )
        probability = 1 / (1 + np.exp(-score))
        return np.vstack([1 - probability, probability]).T


def load_model() -> tuple[object, list[str], str]:
    path = Path(os.getenv("MODEL_PATH", "models/champion.joblib"))
    if path.exists():
        artifact = joblib.load(path)
        return artifact["model"], artifact["feature_columns"], str(path)
    fallback = HeuristicModel()
    return fallback, fallback.feature_columns, "heuristic-fallback"

