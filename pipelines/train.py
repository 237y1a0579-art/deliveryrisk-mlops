from __future__ import annotations

import os

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from pipelines.common import ensure_parent, load_params, project_path, write_json

TARGET = "late_delivery"
DROP_COLUMNS = {"actual_delivery_minutes", "event_timestamp", TARGET, "order_id", "customer_id", "merchant_id"}


def split_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    candidate_columns = [col for col in df.columns if col not in DROP_COLUMNS]
    x = df[candidate_columns]
    y = df[TARGET].astype(int)
    return x, y


def build_model(n_estimators: int, max_depth: int, random_seed: int) -> Pipeline:
    numeric_features = []
    categorical_features = []
    for column in [
        "distance_km",
        "basket_value",
        "prep_minutes",
        "driver_supply",
        "traffic_index",
        "promised_minutes",
        "customer_late_rate_30d",
        "merchant_late_rate_30d",
        "zone_late_rate_30d",
    ]:
        numeric_features.append(column)

    categorical_features = [
        column
        for column in [
            "zone_central",
            "zone_north",
            "zone_south",
            "zone_east",
            "zone_west",
            "weather_clear",
            "weather_rain",
            "weather_storm",
            "weather_heat",
        ]
        if column
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("imputer", SimpleImputer()), ("scaler", StandardScaler())]), numeric_features),
            ("cat", "passthrough", categorical_features),
        ],
        remainder="drop",
    )
    classifier = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_leaf=8,
        class_weight="balanced",
        random_state=random_seed,
        n_jobs=-1,
    )
    return Pipeline([("preprocessor", preprocessor), ("classifier", classifier)])


def main() -> None:
    params = load_params()
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "file:./mlruns")
    registry_uri = os.getenv("MLFLOW_REGISTRY_URI", tracking_uri)
    model_name = os.getenv("MODEL_NAME", "deliveryrisk-late-order")

    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_registry_uri(registry_uri)
    mlflow.set_experiment("deliveryrisk-late-order")

    df = pd.read_parquet(project_path("data", "processed", "training_features.parquet"))
    x, y = split_features(df)
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=float(params["training"]["test_size"]),
        random_state=int(params["training"]["random_seed"]),
        stratify=y,
    )

    model = build_model(
        n_estimators=int(params["training"]["n_estimators"]),
        max_depth=int(params["training"]["max_depth"]),
        random_seed=int(params["training"]["random_seed"]),
    )

    with mlflow.start_run(run_name="random-forest-baseline"):
        model.fit(x_train, y_train)
        y_pred = model.predict(x_test)
        y_score = model.predict_proba(x_test)[:, 1]

        metrics = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred)),
            "recall": float(recall_score(y_test, y_pred)),
            "f1": float(f1_score(y_test, y_pred)),
            "roc_auc": float(roc_auc_score(y_test, y_score)),
        }
        mlflow.log_params(params["training"])
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            registered_model_name=model_name,
            input_example=x_test.head(3),
        )

        model_path = project_path("models", "champion.joblib")
        ensure_parent(model_path)
        joblib.dump({"model": model, "feature_columns": list(x.columns)}, model_path)
        write_json(project_path("reports", "model_metrics.json"), metrics)

    min_auc = float(params["training"]["min_auc"])
    if metrics["roc_auc"] < min_auc:
        raise RuntimeError(f"Model AUC {metrics['roc_auc']:.3f} is below required threshold {min_auc:.3f}")

    print(f"Saved champion model to {model_path}")
    print(metrics)


if __name__ == "__main__":
    main()
