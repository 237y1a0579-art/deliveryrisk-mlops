from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipelines.common import load_params, project_path, write_json  # noqa: E402


def load_metrics(path: Path) -> dict[str, float]:
    import json

    if not path.exists():
        raise FileNotFoundError(f"Metrics file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    return {key: float(value) for key, value in raw.items()}


def latest_model_version(model_name: str) -> str | None:
    from mlflow.tracking import MlflowClient

    client = MlflowClient()
    versions = client.search_model_versions(f"name = '{model_name}'")
    if not versions:
        return None
    return str(max(int(version.version) for version in versions))


def set_model_alias(model_name: str, alias: str, version: str) -> None:
    from mlflow.tracking import MlflowClient

    client = MlflowClient()
    client.set_registered_model_alias(model_name, alias, version)


def build_decision(metrics: dict[str, float], min_auc: float, min_f1: float) -> dict[str, Any]:
    passed = metrics.get("roc_auc", 0.0) >= min_auc and metrics.get("f1", 0.0) >= min_f1
    reasons = []
    if metrics.get("roc_auc", 0.0) < min_auc:
        reasons.append(f"roc_auc below threshold: {metrics.get('roc_auc', 0.0):.4f} < {min_auc:.4f}")
    if metrics.get("f1", 0.0) < min_f1:
        reasons.append(f"f1 below threshold: {metrics.get('f1', 0.0):.4f} < {min_f1:.4f}")
    return {
        "passed": passed,
        "decision": "promote" if passed else "reject",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "thresholds": {"roc_auc": min_auc, "f1": min_f1},
        "metrics": metrics,
        "reasons": reasons,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Gate and optionally promote a trained DeliveryRisk model.")
    parser.add_argument("--metrics-path", default="reports/model_metrics.json")
    parser.add_argument("--decision-path", default="reports/promotion_decision.json")
    parser.add_argument("--model-name", default=os.getenv("MODEL_NAME", "deliveryrisk-late-order"))
    parser.add_argument("--alias", default="champion")
    parser.add_argument("--min-f1", type=float, default=None)
    parser.add_argument("--set-mlflow-alias", action="store_true")
    args = parser.parse_args()

    params = load_params()
    min_auc = float(params["training"]["min_auc"])
    min_f1 = float(args.min_f1 if args.min_f1 is not None else params["training"]["min_f1"])
    metrics = load_metrics(project_path(args.metrics_path))
    decision = build_decision(metrics=metrics, min_auc=min_auc, min_f1=min_f1)

    promoted_version = None
    if decision["passed"] and args.set_mlflow_alias:
        version = latest_model_version(args.model_name)
        if version is None:
            raise RuntimeError(f"No registered MLflow model versions found for {args.model_name}")
        set_model_alias(args.model_name, args.alias, version)
        promoted_version = version

    decision["model_name"] = args.model_name
    decision["mlflow_alias"] = args.alias if args.set_mlflow_alias else None
    decision["promoted_version"] = promoted_version
    write_json(project_path(args.decision_path), decision)

    print(f"Promotion decision: {decision['decision']}")
    if decision["reasons"]:
        for reason in decision["reasons"]:
            print(f"- {reason}")

    if not decision["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
