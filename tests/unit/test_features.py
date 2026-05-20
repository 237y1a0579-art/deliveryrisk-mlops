import pandas as pd

from pipelines.features import build_training_table


def test_build_training_table_adds_historical_features():
    frame = pd.DataFrame(
        {
            "order_id": [1, 2, 3],
            "event_timestamp": pd.to_datetime(
                ["2026-01-01T00:00:00Z", "2026-01-01T01:00:00Z", "2026-01-01T02:00:00Z"]
            ),
            "customer_id": [101, 101, 102],
            "merchant_id": [10, 10, 11],
            "zone": ["central", "central", "north"],
            "weather": ["clear", "rain", "clear"],
            "distance_km": [1.2, 3.4, 2.2],
            "basket_value": [22.0, 40.0, 18.0],
            "prep_minutes": [12.0, 24.0, 18.0],
            "driver_supply": [0.8, 0.5, 0.7],
            "traffic_index": [0.2, 0.8, 0.4],
            "promised_minutes": [28.0, 42.0, 35.0],
            "actual_delivery_minutes": [25.0, 65.0, 36.0],
            "late_delivery": [0, 1, 0],
        }
    )

    result = build_training_table(frame)

    assert "customer_late_rate_30d" in result.columns
    assert "merchant_late_rate_30d" in result.columns
    assert "weather_rain" in result.columns
    assert len(result) == 3

