def choose_action(probability: float, weather: str, driver_supply: float) -> str:
    if probability >= 0.7:
        if weather in {"rain", "storm"}:
            return "Proactively notify the customer, add a weather delay note, and prioritize courier reassignment."
        if driver_supply < 0.45:
            return "Escalate courier supply, notify the customer, and offer a support credit if the SLA is missed."
        return "Route to operations queue and send a transparent delay warning."
    if probability >= 0.4:
        return "Watch closely and refresh ETA after merchant pickup confirmation."
    return "No escalation needed; continue normal tracking."


def risk_band(probability: float) -> str:
    if probability >= 0.7:
        return "high"
    if probability >= 0.4:
        return "medium"
    return "low"

