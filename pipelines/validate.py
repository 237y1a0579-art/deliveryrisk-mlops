from __future__ import annotations

import pandas as pd

from pipelines.common import ensure_parent, load_params, project_path, write_json

REQUIRED_COLUMNS = {
    "order_id",
    "event_timestamp",
    "customer_id",
    "merchant_id",
    "zone",
    "weather",
    "distance_km",
    "basket_value",
    "prep_minutes",
    "driver_supply",
    "traffic_index",
    "promised_minutes",
    "actual_delivery_minutes",
    "late_delivery",
}

ALLOWED_WEATHER = {"clear", "rain", "storm", "heat"}
ALLOWED_ZONES = {"central", "north", "south", "east", "west"}


def validate_orders(df: pd.DataFrame, min_rows: int) -> dict[str, object]:
    failures: list[str] = []

    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        failures.append(f"Missing columns: {sorted(missing)}")

    if len(df) < min_rows:
        failures.append(f"Expected at least {min_rows} rows, found {len(df)}")

    if df["order_id"].duplicated().any():
        failures.append("order_id must be unique")

    if df[["order_id", "customer_id", "merchant_id", "event_timestamp"]].isna().any().any():
        failures.append("Core identity and timestamp columns cannot be null")

    numeric_ranges = {
        "distance_km": (0.1, 30),
        "basket_value": (1, 500),
        "prep_minutes": (1, 90),
        "driver_supply": (0, 2),
        "traffic_index": (0, 1),
        "promised_minutes": (5, 120),
        "actual_delivery_minutes": (5, 180),
    }
    for column, (low, high) in numeric_ranges.items():
        invalid_count = (~df[column].between(low, high)).sum()
        if invalid_count:
            failures.append(f"{column} has {invalid_count} values outside [{low}, {high}]")

    if not set(df["weather"]).issubset(ALLOWED_WEATHER):
        failures.append("weather contains unexpected values")

    if not set(df["zone"]).issubset(ALLOWED_ZONES):
        failures.append("zone contains unexpected values")

    if not set(df["late_delivery"]).issubset({0, 1}):
        failures.append("late_delivery must be binary")

    return {
        "passed": not failures,
        "row_count": int(len(df)),
        "late_delivery_rate": float(df["late_delivery"].mean()),
        "null_counts": {col: int(value) for col, value in df.isna().sum().items()},
        "failures": failures,
    }


def main() -> None:
    params = load_params()
    raw_path = project_path("data", "raw", "orders.csv")
    output_path = project_path("data", "processed", "orders_validated.parquet")
    report_path = project_path("reports", "data_validation.json")

    df = pd.read_csv(raw_path, parse_dates=["event_timestamp"])
    report = validate_orders(df, min_rows=int(params["data"]["validation_min_rows"]))
    write_json(report_path, report)

    if not report["passed"]:
        raise ValueError(f"Data validation failed: {report['failures']}")

    ensure_parent(output_path)
    df.to_parquet(output_path, index=False)
    print(f"Validated data written to {output_path}")


if __name__ == "__main__":
    main()

