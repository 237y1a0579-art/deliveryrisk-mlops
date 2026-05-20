from datetime import timedelta

from feast import Entity, FeatureView, Field, FileSource
from feast.types import Float32, Int64, String

order = Entity(name="order_id", join_keys=["order_id"])

order_source = FileSource(
    name="order_feature_source",
    path="../data/processed/feature_store.parquet",
    timestamp_field="event_timestamp",
)

order_features = FeatureView(
    name="order_features",
    entities=[order],
    ttl=timedelta(days=2),
    schema=[
        Field(name="customer_id", dtype=Int64),
        Field(name="merchant_id", dtype=Int64),
        Field(name="zone", dtype=String),
        Field(name="weather", dtype=String),
        Field(name="distance_km", dtype=Float32),
        Field(name="basket_value", dtype=Float32),
        Field(name="prep_minutes", dtype=Float32),
        Field(name="driver_supply", dtype=Float32),
        Field(name="traffic_index", dtype=Float32),
        Field(name="promised_minutes", dtype=Float32),
        Field(name="customer_late_rate_30d", dtype=Float32),
        Field(name="merchant_late_rate_30d", dtype=Float32),
        Field(name="zone_late_rate_30d", dtype=Float32),
    ],
    source=order_source,
)

