from __future__ import annotations

import pandas as pd

from pipelines.common import ensure_parent, project_path

CATEGORICAL_COLUMNS = ["zone", "weather"]
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


def add_historical_rates(df: pd.DataFrame) -> pd.DataFrame:
    ordered = df.sort_values("event_timestamp").copy()
    global_rate = ordered["late_delivery"].expanding().mean().shift(1).fillna(ordered["late_delivery"].mean())

    ordered["customer_late_rate_30d"] = (
        ordered.groupby("customer_id")["late_delivery"]
        .transform(lambda s: s.expanding().mean().shift(1))
        .fillna(global_rate)
    )
    ordered["merchant_late_rate_30d"] = (
        ordered.groupby("merchant_id")["late_delivery"]
        .transform(lambda s: s.expanding().mean().shift(1))
        .fillna(global_rate)
    )
    ordered["zone_late_rate_30d"] = (
        ordered.groupby("zone")["late_delivery"]
        .transform(lambda s: s.expanding().mean().shift(1))
        .fillna(global_rate)
    )
    return ordered


def build_training_table(df: pd.DataFrame) -> pd.DataFrame:
    featured = add_historical_rates(df)
    encoded = pd.get_dummies(featured, columns=CATEGORICAL_COLUMNS, drop_first=False, dtype=int)
    return encoded


def build_feature_store_table(df: pd.DataFrame) -> pd.DataFrame:
    featured = add_historical_rates(df)
    return featured[
        [
            "order_id",
            "event_timestamp",
            "customer_id",
            "merchant_id",
            "zone",
            "weather",
            *NUMERIC_FEATURES,
        ]
    ].copy()


def main() -> None:
    input_path = project_path("data", "processed", "orders_validated.parquet")
    training_path = project_path("data", "processed", "training_features.parquet")
    feature_store_path = project_path("data", "processed", "feature_store.parquet")
    reference_path = project_path("data", "reference", "reference_features.parquet")

    df = pd.read_parquet(input_path)
    training = build_training_table(df)
    feature_store = build_feature_store_table(df)

    ensure_parent(training_path)
    training.to_parquet(training_path, index=False)
    feature_store.to_parquet(feature_store_path, index=False)

    reference_columns = [*NUMERIC_FEATURES, "late_delivery"]
    training[reference_columns].sample(frac=0.35, random_state=42).to_parquet(reference_path, index=False)
    print(f"Training features written to {training_path}")
    print(f"Feature store source written to {feature_store_path}")


if __name__ == "__main__":
    main()

