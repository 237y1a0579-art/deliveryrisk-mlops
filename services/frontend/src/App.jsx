import { Activity, AlertTriangle, Gauge, RefreshCw, Route, Send } from "lucide-react";
import { useMemo, useState } from "react";

const isLocalBrowser = ["localhost", "127.0.0.1"].includes(window.location.hostname);
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || (isLocalBrowser ? "http://localhost:8000" : "/api");
const DRIFT_RUN_URL = import.meta.env.VITE_DRIFT_RUN_URL || (isLocalBrowser ? "http://localhost:8010/drift/run" : "/drift/run");

const initialOrder = {
  order_id: 90001,
  customer_id: 1442,
  merchant_id: 34,
  zone: "central",
  weather: "rain",
  distance_km: 6.2,
  basket_value: 38.5,
  prep_minutes: 23,
  driver_supply: 0.42,
  traffic_index: 0.78,
  promised_minutes: 45,
  customer_late_rate_30d: 0.24,
  merchant_late_rate_30d: 0.34,
  zone_late_rate_30d: 0.28,
};

function NumberField({ label, name, value, onChange, min, max, step = "0.01" }) {
  return (
    <label className="field">
      <span>{label}</span>
      <input
        type="number"
        name={name}
        value={value}
        min={min}
        max={max}
        step={step}
        onChange={onChange}
      />
    </label>
  );
}

function App() {
  const [order, setOrder] = useState(initialOrder);
  const [prediction, setPrediction] = useState(null);
  const [drift, setDrift] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const riskWidth = useMemo(() => {
    const probability = prediction?.late_delivery_probability ?? 0;
    return `${Math.round(probability * 100)}%`;
  }, [prediction]);

  function updateOrder(event) {
    const { name, value, type } = event.target;
    setOrder((current) => ({
      ...current,
      [name]: type === "number" ? Number(value) : value,
    }));
  }

  async function scoreOrder() {
    setLoading(true);
    setMessage("");
    try {
      const response = await fetch(`${API_BASE_URL}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(order),
      });
      if (!response.ok) throw new Error(`API returned ${response.status}`);
      setPrediction(await response.json());
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function runDrift() {
    setMessage("");
    try {
      const response = await fetch(DRIFT_RUN_URL, { method: "POST" });
      if (!response.ok) throw new Error(`Drift service returned ${response.status}`);
      setDrift(await response.json());
    } catch (error) {
      setMessage(error.message);
    }
  }

  return (
    <main className="shell">
      <aside className="sidebar">
        <div className="brand">
          <Route aria-hidden="true" />
          <div>
            <strong>DeliveryRisk</strong>
            <span>Operations Console</span>
          </div>
        </div>
        <nav>
          <a className="active" href="#score">
            <Gauge aria-hidden="true" /> Score
          </a>
          <a href="#monitoring">
            <Activity aria-hidden="true" /> Monitoring
          </a>
          <a href="#alerts">
            <AlertTriangle aria-hidden="true" /> Alerts
          </a>
        </nav>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <h1>Late Delivery Risk</h1>
            <p>Score live orders, inspect operational drivers, and trigger drift checks.</p>
          </div>
          <button className="secondary" type="button" onClick={runDrift}>
            <RefreshCw aria-hidden="true" /> Drift Check
          </button>
        </header>

        <div className="grid">
          <section className="panel" id="score">
            <div className="panel-heading">
              <h2>Order Inputs</h2>
              <button type="button" onClick={scoreOrder} disabled={loading}>
                <Send aria-hidden="true" /> {loading ? "Scoring" : "Score"}
              </button>
            </div>

            <div className="form-grid">
              <NumberField label="Order ID" name="order_id" value={order.order_id} onChange={updateOrder} min="1" step="1" />
              <NumberField label="Customer ID" name="customer_id" value={order.customer_id} onChange={updateOrder} min="1" step="1" />
              <NumberField label="Merchant ID" name="merchant_id" value={order.merchant_id} onChange={updateOrder} min="1" step="1" />
              <label className="field">
                <span>Zone</span>
                <select name="zone" value={order.zone} onChange={updateOrder}>
                  <option value="central">central</option>
                  <option value="north">north</option>
                  <option value="south">south</option>
                  <option value="east">east</option>
                  <option value="west">west</option>
                </select>
              </label>
              <label className="field">
                <span>Weather</span>
                <select name="weather" value={order.weather} onChange={updateOrder}>
                  <option value="clear">clear</option>
                  <option value="rain">rain</option>
                  <option value="storm">storm</option>
                  <option value="heat">heat</option>
                </select>
              </label>
              <NumberField label="Distance km" name="distance_km" value={order.distance_km} onChange={updateOrder} min="0.1" max="30" />
              <NumberField label="Basket value" name="basket_value" value={order.basket_value} onChange={updateOrder} min="1" max="500" />
              <NumberField label="Prep minutes" name="prep_minutes" value={order.prep_minutes} onChange={updateOrder} min="1" max="90" />
              <NumberField label="Driver supply" name="driver_supply" value={order.driver_supply} onChange={updateOrder} min="0" max="2" />
              <NumberField label="Traffic index" name="traffic_index" value={order.traffic_index} onChange={updateOrder} min="0" max="1" />
              <NumberField label="Promised minutes" name="promised_minutes" value={order.promised_minutes} onChange={updateOrder} min="5" max="120" />
              <NumberField label="Customer late rate" name="customer_late_rate_30d" value={order.customer_late_rate_30d} onChange={updateOrder} min="0" max="1" />
              <NumberField label="Merchant late rate" name="merchant_late_rate_30d" value={order.merchant_late_rate_30d} onChange={updateOrder} min="0" max="1" />
              <NumberField label="Zone late rate" name="zone_late_rate_30d" value={order.zone_late_rate_30d} onChange={updateOrder} min="0" max="1" />
            </div>
          </section>

          <section className="panel outcome">
            <div className="panel-heading">
              <h2>Prediction</h2>
              <span className={`badge ${prediction?.risk_band || "idle"}`}>
                {prediction?.risk_band || "waiting"}
              </span>
            </div>
            <div className="meter">
              <div style={{ width: riskWidth }} />
            </div>
            <strong className="probability">
              {prediction ? `${Math.round(prediction.late_delivery_probability * 100)}%` : "--"}
            </strong>
            <p>{prediction?.recommended_action || "Submit an order to see the recommended operations action."}</p>
            <dl>
              <div>
                <dt>Model</dt>
                <dd>{prediction?.model_source || "not scored"}</dd>
              </div>
              <div>
                <dt>Order</dt>
                <dd>{prediction?.order_id || order.order_id}</dd>
              </div>
            </dl>
          </section>
        </div>

        <section className="panel" id="monitoring">
          <div className="panel-heading">
            <h2>Drift Snapshot</h2>
            <span className={`badge ${drift?.status === "ok" ? "low" : "medium"}`}>
              {drift?.status || "not run"}
            </span>
          </div>
          <div className="drift-grid">
            <div>
              <span>Reference rows</span>
              <strong>{drift?.reference_rows ?? "--"}</strong>
            </div>
            <div>
              <span>Current rows</span>
              <strong>{drift?.current_rows ?? "--"}</strong>
            </div>
            <div>
              <span>Max PSI</span>
              <strong>{drift?.max_psi ?? "--"}</strong>
            </div>
            <div>
              <span>Features flagged</span>
              <strong>{drift?.drifted_features?.length ?? "--"}</strong>
            </div>
          </div>
        </section>

        {message && <div className="toast">{message}</div>}
      </section>
    </main>
  );
}

export default App;
