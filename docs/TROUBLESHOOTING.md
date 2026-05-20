# Troubleshooting

## Python dependency installation fails

Check your Python version:

```powershell
python --version
```

Use Python 3.10 or 3.11 for the smoothest path. Some ML packages lag behind the newest Python versions.

## `dvc repro` cannot find files

Run the stages once manually to see the exact failure:

```powershell
python -m pipelines.ingest
python -m pipelines.validate
python -m pipelines.features
python -m pipelines.train
```

If manual execution works, delete stale DVC cache metadata only after you understand what changed. Do not delete source data blindly.

## MLflow model registry fails with local file tracking

Use a server-backed MLflow URI:

```powershell
mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlartifacts
$env:MLFLOW_TRACKING_URI="http://localhost:5000"
$env:MLFLOW_REGISTRY_URI="http://localhost:5000"
python -m pipelines.train
```

The registry is more reliable when the tracking backend is database-backed.

## API starts but says `heuristic-fallback`

That means `models/champion.joblib` is missing. Train the model:

```powershell
python -m pipelines.ingest
python -m pipelines.validate
python -m pipelines.features
python -m pipelines.train
```

Then restart the API.

## Frontend cannot reach the API

Make sure the API is running:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

If you changed the API port, set:

```powershell
$env:VITE_API_BASE_URL="http://localhost:YOUR_PORT"
```

Then restart the frontend dev server.

## Promptfoo fails because `npx` is missing

Install Node.js, then verify:

```powershell
node --version
npx --version
```

Run:

```powershell
cd promptfoo
npx promptfoo@latest eval -c promptfooconfig.yaml
```

## Docker Compose cannot connect services

Rebuild from scratch:

```powershell
docker compose down
docker compose up --build
```

If a port is already used, either stop the conflicting process or change the host port in `docker-compose.yml`.

## Kubernetes images will not pull

Update the placeholder image names in:

```text
k8s/base/api-deployment.yaml
k8s/base/frontend-deployment.yaml
k8s/base/drift-deployment.yaml
k8s/overlays/dev/kustomization.yaml
```

Use your actual GitHub Container Registry path:

```text
ghcr.io/YOUR_GITHUB_USERNAME/YOUR_REPO/api:latest
```

If the repository is private, configure an image pull secret.

## Argo CD app is out of sync

Check the app:

```powershell
kubectl get applications -n argocd
kubectl describe application deliveryrisk-dev -n argocd
```

Common causes:

- Wrong GitHub repo URL.
- Wrong manifest path.
- Kubernetes cluster lacks an ingress controller.
- Image names are still placeholders.

