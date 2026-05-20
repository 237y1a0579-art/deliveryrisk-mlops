from fastapi.testclient import TestClient

from services.api.app.main import app


def test_predict_contract():
    client = TestClient(app)
    response = client.post(
        "/predict",
        json={
            "order_id": 1,
            "customer_id": 101,
            "merchant_id": 10,
            "zone": "central",
            "weather": "rain",
            "distance_km": 5.4,
            "basket_value": 31.2,
            "prep_minutes": 24.0,
            "driver_supply": 0.42,
            "traffic_index": 0.82,
            "promised_minutes": 42.0,
            "customer_late_rate_30d": 0.24,
            "merchant_late_rate_30d": 0.31,
            "zone_late_rate_30d": 0.28,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert 0 <= payload["late_delivery_probability"] <= 1
    assert payload["risk_band"] in {"low", "medium", "high"}

