# Step-by-Step Implementation Guide

This guide teaches the project as if you are building it from scratch. The commands assume PowerShell on Windows, but the same Python and Docker concepts apply on macOS or Linux.

## 1. Understand the Business Problem

The application predicts `late_delivery`, a binary label:

- `0`: order arrived within the acceptable promise window.
- `1`: order arrived late.

The model uses features such as distance, traffic, weather, merchant prep time, courier supply, and historical late rates. In production, this type of model helps operations teams intervene before a customer has a bad experience.

## 2. Create the Project Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Concept:

A virtual environment isolates this project from the rest of your machine. That prevents one project from breaking another project by upgrading shared packages.

## 3. Inspect the Folder Structure

```text
deliveryrisk-mlops/
  .github/workflows/        GitHub Actions CI and image build workflows
  configs/                  Future app and environment configs
  data/                     Raw, processed, reference, and production data
  docs/                     Architecture, guide, troubleshooting, resume notes
  feature_repo/             Feast feature store definitions
  k8s/                      Kubernetes and Argo CD manifests
  monitoring/               Prometheus and Grafana configuration
  pipelines/                Data, feature, and training code
  promptfoo/                Prompt regression tests
  services/api/             FastAPI prediction service
  services/frontend/        React dashboard
  services/monitoring/      Drift detection service
  tests/                    Unit and integration tests
```

Concept:

Production ML is not one notebook. A real ML system needs reproducible data pipelines, serving code, infrastructure, monitoring, tests, and documentation.

## 4. Run Data Ingestion

```powershell
python -m pipelines.ingest
```

Output:

```text
data/raw/orders.csv
```

Concept:

Ingestion is the boundary where external data enters your ML system. This project generates synthetic order data, but in a real company this stage might read from Kafka, S3, a database, or a vendor API.

Best practice:

Keep ingestion simple. Do not train models directly from raw ingestion code. Land the raw data first so you can audit and replay it.

## 5. Run Data Validation

```powershell
python -m pipelines.validate
```

Outputs:

```text
data/processed/orders_validated.parquet
reports/data_validation.json
```

Concept:

Data validation checks whether the input data is usable before it reaches feature engineering or model training. Examples:

- Required columns exist.
- IDs are not null.
- Distances and delivery times are inside reasonable ranges.
- Labels are binary.
- Categorical values are expected.

Why this matters:

Most production ML failures are data failures wearing a model costume. Validation catches broken upstream feeds early.

## 6. Run Feature Engineering

```powershell
python -m pipelines.features
```

Outputs:

```text
data/processed/training_features.parquet
data/processed/feature_store.parquet
data/reference/reference_features.parquet
```

Concept:

Feature engineering converts raw columns into model-ready signals. This project creates historical late-rate features:

- `customer_late_rate_30d`
- `merchant_late_rate_30d`
- `zone_late_rate_30d`

The pipeline writes two important outputs:

- A training table for model training.
- A feature-store source table for Feast.

Best practice:

Avoid training-serving skew. If a feature is important during training, design how it will be available during serving.

## 7. Reproduce Everything with DVC

Initialize DVC once:

```powershell
git init
dvc init
```

Then run:

```powershell
dvc repro
```

Concept:

DVC turns the ML workflow into a dependency graph. If raw data or code changes, DVC knows which stages must rerun.

Typical DVC lifecycle:

```powershell
dvc repro
git add dvc.yaml dvc.lock params.yaml
git commit -m "Reproduce ML pipeline"
```

Production note:

For a team project, configure a remote store:

```powershell
dvc remote add -d storage s3://your-bucket/deliveryrisk
dvc push
```

## 8. Apply the Feast Feature Store

```powershell
cd feature_repo
feast apply
feast materialize-incremental (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss")
cd ..
```

Concept:

A feature store keeps feature definitions consistent between training and inference. Feast supports offline retrieval for training and online serving for low-latency predictions.

In this starter project, Feast is configured with local file and SQLite stores. In production, you would usually use a warehouse or lakehouse for offline data and Redis or DynamoDB for online data.

## 9. Train and Track the Model

Start MLflow locally:

```powershell
mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlartifacts
```

In another terminal:

```powershell
$env:MLFLOW_TRACKING_URI="http://localhost:5000"
$env:MLFLOW_REGISTRY_URI="http://localhost:5000"
python -m pipelines.train
```

Outputs:

```text
models/champion.joblib
reports/model_metrics.json
```

Open:

```text
http://localhost:5000
```

Concept:

MLflow Tracking records parameters, metrics, and artifacts for each training run. The Model Registry gives you a lifecycle location for model versions.

Best practice:

Never choose a model by memory or screenshot. Log every experiment and promote models through clear acceptance criteria.

## 10. Serve the Model with FastAPI

```powershell
uvicorn services.api.app.main:app --reload --port 8000
```

Open:

```text
http://localhost:8000/docs
```

Try a prediction:

```powershell
$body = @{
  order_id = 1
  customer_id = 101
  merchant_id = 10
  zone = "central"
  weather = "rain"
  distance_km = 5.4
  basket_value = 31.2
  prep_minutes = 24
  driver_supply = 0.42
  traffic_index = 0.82
  promised_minutes = 42
  customer_late_rate_30d = 0.24
  merchant_late_rate_30d = 0.31
  zone_late_rate_30d = 0.28
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri http://localhost:8000/predict -Body $body -ContentType "application/json"
```

Concept:

The API is the production boundary for inference. Pydantic schemas validate incoming requests before they hit model code.

## 11. Run the Frontend

```powershell
cd services/frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

Concept:

A dashboard makes the project feel like a product. Hiring managers and teammates understand systems faster when they can interact with them.

## 12. Run Drift Detection

Make several predictions first so the API writes inference logs.

Then:

```powershell
uvicorn services.monitoring.app.main:app --reload --port 8010
Invoke-RestMethod -Method Post -Uri http://localhost:8010/drift/run
```

Concept:

Drift detection compares current production inputs against reference training data. This project calculates PSI and KS-style checks for numeric features.

Interpretation:

- PSI below `0.10`: usually small change.
- PSI around `0.10` to `0.25`: investigate.
- PSI above `0.25`: likely meaningful drift.

Drift does not automatically mean the model is wrong. It means production data no longer looks like training data, so you need investigation.

## 13. Run Tests

```powershell
pytest
ruff check .
```

Concept:

MLOps projects need software tests and ML checks. Unit tests catch feature bugs. API contract tests catch serving regressions. Metric thresholds catch bad model runs.

## 14. Run Promptfoo

```powershell
cd promptfoo
npx promptfoo@latest eval -c promptfooconfig.yaml
```

Concept:

Promptfoo regression-tests prompt behavior. This project tests the operations-assistant prompt so changes do not start making unsafe promises or over-escalating low-risk cases.

Production note:

The included provider is a mock provider so CI can run without API keys. To test a real LLM, add a provider that points to your model gateway and store API keys as GitHub Actions secrets.

## 15. Run the Whole Stack with Docker Compose

```powershell
docker compose up --build
```

This starts:

- MLflow on `http://localhost:5000`
- API on `http://localhost:8000`
- Frontend on `http://localhost:5173`
- Drift service on `http://localhost:8010`
- Prometheus on `http://localhost:9090`
- Grafana on `http://localhost:3000`

Grafana login:

```text
admin / admin
```

Concept:

Docker Compose is your local integration environment. It is not the same as production, but it helps you test service boundaries early.

## 16. Deploy to Kubernetes

For local Kubernetes, use Docker Desktop Kubernetes, minikube, kind, or k3d.

First update the placeholder images:

```text
ghcr.io/OWNER/REPO/api
ghcr.io/OWNER/REPO/frontend
ghcr.io/OWNER/REPO/drift
```

Then:

```powershell
kubectl apply -k k8s/overlays/dev
kubectl get pods -n deliveryrisk
kubectl port-forward svc/deliveryrisk-api -n deliveryrisk 8000:8000
kubectl port-forward svc/deliveryrisk-frontend -n deliveryrisk 8080:80
```

Concept:

Kubernetes runs containers as declarative resources. Deployments manage replicas. Services provide stable networking. Probes tell Kubernetes when a container is healthy.

## 17. Deploy with Argo CD

Install Argo CD into your cluster, then update:

```text
k8s/argocd/deliveryrisk-dev-app.yaml
```

Set your actual GitHub repo URL:

```yaml
repoURL: https://github.com/YOUR_GITHUB_USERNAME/deliveryrisk-mlops.git
```

Apply:

```powershell
kubectl apply -f k8s/argocd/deliveryrisk-dev-app.yaml
```

Concept:

Argo CD watches Git and reconciles Kubernetes to match the manifests. This is GitOps: Git becomes the source of truth for deployment state.

## 18. CI/CD Flow

The CI workflow does three things:

- Runs lint and tests.
- Runs `dvc repro` as a pipeline smoke test.
- Runs Promptfoo prompt tests.

The CD workflow builds and pushes Docker images to GitHub Container Registry, then updates the dev Kubernetes overlay with immutable image tags. Argo CD deploys the updated GitOps state.

## 19. Continuous Training Flow

Continuous Training means the model is retrained automatically when the training trigger fires. In this project, CT is handled by:

```text
.github/workflows/continuous-training.yml
```

It can run manually, weekly, or when data/pipeline configuration changes.

The CT workflow:

- Runs `dvc repro`.
- Trains a new model.
- Checks quality gates with `scripts/promote_model.py`.
- Uploads model and report artifacts.
- Builds an API Docker image containing the promoted model.
- Updates `k8s/overlays/dev/kustomization.yaml`.
- Lets Argo CD deploy the new model-serving API.

Production improvement:

Add a deployment promotion workflow that updates `k8s/overlays/prod/kustomization.yaml` with a pinned image SHA after model and app checks pass.

## 20. What to Build Next

Good follow-up improvements:

- Add a real dataset ingestion connector.
- Add Redis as the Feast online store.
- Add Evidently or WhyLabs for richer drift reports.
- Add model explainability with SHAP.
- Add canary deployments and rollback.
- Add authentication to the dashboard and API.
- Add a scheduled retraining workflow.
