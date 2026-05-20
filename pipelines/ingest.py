from __future__ import annotations

from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

from pipelines.common import ensure_parent, load_params, project_path

ZONES = ["central", "north", "south", "east", "west"]
WEATHER = ["clear", "rain", "storm", "heat"]


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-x))


def generate_orders(n_orders: int, random_seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(random_seed)
    start = datetime.now(timezone.utc) - timedelta(days=90)

    customer_ids = rng.integers(1000, 1800, size=n_orders)
    merchant_ids = rng.integers(10, 90, size=n_orders)
    zone = rng.choice(ZONES, size=n_orders, p=[0.28, 0.18, 0.18, 0.18, 0.18])
    weather = rng.choice(WEATHER, size=n_orders, p=[0.64, 0.22, 0.06, 0.08])
    event_timestamp = [start + timedelta(minutes=int(i * 11)) for i in range(n_orders)]

    distance_km = rng.gamma(shape=2.2, scale=1.8, size=n_orders).clip(0.4, 18)
    basket_value = rng.lognormal(mean=3.4, sigma=0.45, size=n_orders).clip(8, 180)
    prep_minutes = rng.normal(loc=18, scale=6, size=n_orders).clip(4, 55)
    driver_supply = rng.normal(loc=0.74, scale=0.18, size=n_orders).clip(0.15, 1.25)
    traffic_index = rng.beta(a=2.2, b=2.0, size=n_orders)
    promised_minutes = 28 + distance_km * 3.2 + rng.normal(0, 5, n_orders)

    weather_risk = pd.Series(weather).map({"clear": 0.0, "rain": 0.55, "storm": 1.1, "heat": 0.2}).to_numpy()
    zone_risk = pd.Series(zone).map({"central": 0.25, "north": 0.1, "south": 0.05, "east": 0.18, "west": 0.12}).to_numpy()

    latent = (
        -3.1
        + 0.18 * distance_km
        + 0.055 * prep_minutes
        + 1.55 * traffic_index
        - 1.45 * driver_supply
        + weather_risk
        + zone_risk
        + rng.normal(0, 0.35, n_orders)
    )
    late_probability = sigmoid(latent)
    late_delivery = rng.binomial(1, late_probability)
    actual_delivery_minutes = promised_minutes + rng.normal(4, 7, n_orders) + late_delivery * rng.normal(18, 6, n_orders)

    return pd.DataFrame(
        {
            "order_id": np.arange(1, n_orders + 1),
            "event_timestamp": event_timestamp,
            "customer_id": customer_ids,
            "merchant_id": merchant_ids,
            "zone": zone,
            "weather": weather,
            "distance_km": distance_km.round(2),
            "basket_value": basket_value.round(2),
            "prep_minutes": prep_minutes.round(1),
            "driver_supply": driver_supply.round(3),
            "traffic_index": traffic_index.round(3),
            "promised_minutes": promised_minutes.round(1),
            "actual_delivery_minutes": actual_delivery_minutes.round(1),
            "late_delivery": late_delivery,
        }
    )


def main() -> None:
    params = load_params()
    output_path = project_path("data", "raw", "orders.csv")
    ensure_parent(output_path)
    df = generate_orders(
        n_orders=int(params["data"]["n_orders"]),
        random_seed=int(params["data"]["random_seed"]),
    )
    df.to_csv(output_path, index=False)
    print(f"Wrote {len(df):,} raw orders to {output_path}")


if __name__ == "__main__":
    main()

