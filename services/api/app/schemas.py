from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class OrderFeatures(BaseModel):
    order_id: int = Field(..., ge=1)
    customer_id: int = Field(..., ge=1)
    merchant_id: int = Field(..., ge=1)
    zone: str
    weather: str
    distance_km: float = Field(..., ge=0.1, le=30)
    basket_value: float = Field(..., ge=1, le=500)
    prep_minutes: float = Field(..., ge=1, le=90)
    driver_supply: float = Field(..., ge=0, le=2)
    traffic_index: float = Field(..., ge=0, le=1)
    promised_minutes: float = Field(..., ge=5, le=120)
    customer_late_rate_30d: float = Field(0.2, ge=0, le=1)
    merchant_late_rate_30d: float = Field(0.2, ge=0, le=1)
    zone_late_rate_30d: float = Field(0.2, ge=0, le=1)


class PredictionResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    order_id: int
    late_delivery_probability: float
    risk_band: str
    recommended_action: str
    model_source: str
