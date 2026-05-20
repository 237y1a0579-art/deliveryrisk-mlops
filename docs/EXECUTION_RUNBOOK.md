# Execution Runbook

This is the practical command-by-command guide. Follow it in order the first time. After you understand the flow, you can use Docker Compose, GitHub Actions, and Argo CD to automate most of it.

## Tool Legend

| Tool | Use it for |
| --- | --- |
| VS Code | Editing code and opening terminals. |
| VS Code Terminal: PowerShell | Python commands, DVC, MLflow, FastAPI, tests, Git, kubectl. |
| Browser | MLflow UI, FastAPI docs, frontend app, Prometheus, Grafana, GitHub Actions, Argo CD UI. |
| Docker Desktop | Running Docker Compose and local Kubernetes. |
| GitHub Website | Creating the repository, checking Actions, viewing packages. |
| Kubernetes CLI: `kubectl` | Applying manifests and checking pods. Run from VS Code terminal. |
| Argo CD | GitOps deployment. Use CLI from terminal or UI in browser. |

## Phase 0: Open the Project in VS Code

Tool: VS Code.

Open this folder:

```text
C:\Users\konda\Documents\Codex\2026-05-20\act-as-a-senior-mlops-architect
```

If the `code` command works, run this in PowerShell:

```powershell
code C:\Users\konda\Documents\Codex\2026-05-20\act-as-a-senior-mlops-architect
```

If it does not work, open VS Code manually, then use:

```text
File > Open Folder
```

## Phase 1: Install Local Prerequisites

Install these on your machine:

- Python 3.11
- Git
- Node.js 22 LTS
- Docker Desktop
- VS Code Python extension
- VS Code Docker extension
- Kubernetes CLI: `kubectl`

Check versions in VS Code Terminal: PowerShell.

```powershell
python --version
git --version
node --version
npm --version
docker --version
kubectl version --client
```

If `python` is not recognized, try:

```powershell
py -3.11 --version
```

If that works, use `py -3.11` instead of `python` only for creating the virtual environment.

## Phase 2: Create Python Environment

Tool: VS Code Terminal: PowerShell.

Run from the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Close and reopen the terminal, then activate again:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Phase 3: Start MLflow

Tool: VS Code Terminal: PowerShell.

Open a second terminal and run:

```powershell
.\.venv\Scripts\Activate.ps1
mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlartifacts
```

Tool: Browser.

Open:

```text
http://localhost:5000
```

Leave this MLflow terminal running.

## Phase 4: Run the ML Pipeline Manually

Tool: VS Code Terminal: PowerShell.

Go back to your first terminal. Make sure the virtual environment is active.

Set MLflow environment variables:

```powershell
$env:MLFLOW_TRACKING_URI="http://127.0.0.1:5000"
$env:MLFLOW_REGISTRY_URI="http://127.0.0.1:5000"
$env:MODEL_NAME="deliveryrisk-late-order"
```

Run each stage:

```powershell
python -m pipelines.ingest
python -m pipelines.validate
python -m pipelines.features
python -m pipelines.train
```

Expected outputs:

```text
data/raw/orders.csv
data/processed/orders_validated.parquet
data/processed/training_features.parquet
data/processed/feature_store.parquet
data/reference/reference_features.parquet
models/champion.joblib
reports/model_metrics.json
```

Tool: Browser.

Refresh MLflow:

```text
http://localhost:5000
```

You should see an experiment named:

```text
deliveryrisk-late-order
```

## Phase 5: Run the Model Promotion Gate

Tool: VS Code Terminal: PowerShell.

Run:

```powershell
python scripts/promote_model.py --set-mlflow-alias
```

What this does:

- Reads `reports/model_metrics.json`.
- Checks thresholds in `params.yaml`.
- Writes `reports/promotion_decision.json`.
- Sets the MLflow registered model alias to `champion` if the model passes.

If this fails, open:

```text
reports/promotion_decision.json
```

The file tells you which metric failed.

## Phase 6: Run the DVC Pipeline

Tool: VS Code Terminal: PowerShell.

Initialize Git and DVC once:

```powershell
git init
dvc init
```

Run the full pipeline through DVC:

```powershell
dvc repro
```

What this proves:

DVC can reproduce ingestion, validation, feature generation, and training from a single command.

## Phase 7: Apply the Feast Feature Store

Tool: VS Code Terminal: PowerShell.

Run:

```powershell
cd feature_repo
feast apply
feast materialize-incremental (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss")
cd ..
```

What this proves:

Feast can read your feature definitions and build the local registry and online store.

## Phase 8: Start the FastAPI Backend

Tool: VS Code Terminal: PowerShell.

Open a third terminal:

```powershell
.\.venv\Scripts\Activate.ps1
$env:MODEL_PATH="models/champion.joblib"
$env:INFERENCE_LOG_PATH="data/production/inference_log.csv"
uvicorn services.api.app.main:app --reload --port 8000
```

Tool: Browser.

Open:

```text
http://localhost:8000/docs
```

Test `POST /predict` from the Swagger page.

## Phase 9: Start the React Frontend

Tool: VS Code Terminal: PowerShell.

Open a fourth terminal:

```powershell
cd services/frontend
npm install
npm run dev
```

Tool: Browser.

Open:

```text
http://localhost:5173
```

Use the dashboard to score a few orders. This will create:

```text
data/production/inference_log.csv
```

## Phase 10: Start Drift Detection

Tool: VS Code Terminal: PowerShell.

Open a fifth terminal:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn services.monitoring.app.main:app --reload --port 8010
```

Tool: Browser.

Open:

```text
http://localhost:8010/drift/run
```

Expected result:

- If you have not scored enough orders yet, status will be `waiting_for_data`.
- After predictions exist, it will return drift statistics.

## Phase 11: Run Promptfoo Prompt Tests

Tool: VS Code Terminal: PowerShell.

Run:

```powershell
cd promptfoo
npx promptfoo@latest eval -c promptfooconfig.yaml
cd ..
```

What this proves:

Your operations-assistant prompt has regression tests. Prompt changes can now fail CI if they become unsafe or unhelpful.

## Phase 12: Run Everything with Docker Compose

Tool: Docker Desktop.

First, open Docker Desktop and wait until Docker is running.

Tool: VS Code Terminal: PowerShell.

Stop local FastAPI, frontend, MLflow, and drift terminals with `Ctrl+C`, then run:

```powershell
docker compose up --build
```

Tool: Browser.

Open:

```text
http://localhost:8000/docs
http://localhost:5173
http://localhost:5000
http://localhost:9090
http://localhost:3000
```

Grafana login:

```text
admin / admin
```

## Phase 13: Push to GitHub

Tool: GitHub Website.

Create a new repository named:

```text
deliveryrisk-mlops
```

Tool: VS Code Terminal: PowerShell.

Commit and push:

```powershell
git add .
git commit -m "Initial end-to-end MLOps project"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/deliveryrisk-mlops.git
git push -u origin main
```

Tool: GitHub Website.

Open:

```text
Your repo > Actions
```

You should see:

- CI
- Build Images
- Continuous Training

## Phase 14: Continuous Integration

Tool: GitHub Actions UI.

Workflow:

```text
.github/workflows/ci.yml
```

It runs:

- Python linting with Ruff.
- Unit and API contract tests.
- DVC pipeline smoke test.
- Promptfoo tests.

When it runs:

- Every pull request.
- Every push to `main`.

## Phase 15: Continuous Deployment

Tool: GitHub Actions UI plus Argo CD.

Workflow:

```text
.github/workflows/cd.yml
```

It runs when app or pipeline code changes. It:

1. Builds API, frontend, and drift Docker images.
2. Pushes images to GitHub Container Registry.
3. Updates `k8s/overlays/dev/kustomization.yaml` with immutable image tags.
4. Commits that GitOps update.
5. Argo CD sees the commit and deploys it.

Important:

If your GitHub package is private, Kubernetes needs an image pull secret. For learning, the simplest path is to make the GHCR packages public from the GitHub package settings.

## Phase 16: Continuous Training

Tool: GitHub Actions UI.

Workflow:

```text
.github/workflows/continuous-training.yml
```

It runs:

- Manually from the GitHub Actions page.
- Weekly on Monday at 02:00 UTC.
- When data, pipeline code, or `params.yaml` changes.

It does this:

1. Runs `dvc repro`.
2. Trains a new model.
3. Checks model quality with `scripts/promote_model.py`.
4. Uploads model and reports as GitHub artifacts.
5. Builds an API Docker image containing the promoted model.
6. Pushes the image to GHCR.
7. Updates the dev Kubernetes overlay with the model image tag.
8. Commits the GitOps change.
9. Argo CD deploys the new model-serving API.

Manual run:

```text
GitHub repo > Actions > Continuous Training > Run workflow
```

Local CT simulation:

```powershell
dvc repro
python scripts/promote_model.py
docker build -f services/api/Dockerfile -t deliveryrisk-api:model-local .
```

## Phase 17: Kubernetes Deployment Without Argo CD

Tool: Docker Desktop.

Enable Kubernetes in Docker Desktop settings, or use minikube/kind.

Tool: VS Code Terminal: PowerShell.

Check cluster access:

```powershell
kubectl get nodes
```

Update image names if needed:

```powershell
python scripts/update_kustomize_image.py --file k8s/overlays/dev/kustomization.yaml --service api --new-name ghcr.io/YOUR_GITHUB_USERNAME/deliveryrisk-mlops/api --new-tag latest
python scripts/update_kustomize_image.py --file k8s/overlays/dev/kustomization.yaml --service drift --new-name ghcr.io/YOUR_GITHUB_USERNAME/deliveryrisk-mlops/drift --new-tag latest
python scripts/update_kustomize_image.py --file k8s/overlays/dev/kustomization.yaml --service frontend --new-name ghcr.io/YOUR_GITHUB_USERNAME/deliveryrisk-mlops/frontend --new-tag latest
```

Deploy:

```powershell
kubectl apply -k k8s/overlays/dev
kubectl get pods -n deliveryrisk
```

Port-forward:

```powershell
kubectl port-forward svc/deliveryrisk-api -n deliveryrisk 8000:8000
kubectl port-forward svc/deliveryrisk-frontend -n deliveryrisk 8080:80
```

Tool: Browser.

Open:

```text
http://localhost:8000/docs
http://localhost:8080
```

## Phase 18: Argo CD Deployment

Tool: VS Code Terminal: PowerShell.

Install Argo CD:

```powershell
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

Update this file with your GitHub repo URL:

```text
k8s/argocd/deliveryrisk-dev-app.yaml
```

Change:

```yaml
repoURL: https://github.com/YOUR_GITHUB_USERNAME/deliveryrisk-mlops.git
```

Apply:

```powershell
kubectl apply -f k8s/argocd/deliveryrisk-dev-app.yaml
kubectl get applications -n argocd
```

Open the Argo CD UI:

```powershell
kubectl port-forward svc/argocd-server -n argocd 8081:443
```

Tool: Browser.

Open:

```text
https://localhost:8081
```

Get initial password:

```powershell
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}"
```

Decode it in PowerShell:

```powershell
[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String("PASTE_BASE64_PASSWORD_HERE"))
```

Login:

```text
username: admin
password: decoded password
```

## Phase 19: Normal Developer Workflow

For code changes:

```powershell
git checkout -b feature/my-change
pytest
ruff check .
git add .
git commit -m "Describe the change"
git push origin feature/my-change
```

Then open a pull request in GitHub. CI should pass before merging.

For model changes:

```powershell
dvc repro
python scripts/promote_model.py
git add dvc.yaml dvc.lock params.yaml reports/model_metrics.json reports/promotion_decision.json
git commit -m "Retrain delivery risk model"
git push
```

For automated model retraining:

```text
GitHub repo > Actions > Continuous Training > Run workflow
```

## Common Errors and Fixes

`python is not recognized`:

Install Python 3.11 and check "Add Python to PATH", or use `py -3.11`.

`Activate.ps1 cannot be loaded`:

Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`.

`docker compose` fails:

Open Docker Desktop and wait until it says Docker is running.

`port already in use`:

Stop the old terminal with `Ctrl+C`, or change the port in the command.

`kubectl cannot connect`:

Start Docker Desktop Kubernetes, minikube, or kind, then run `kubectl get nodes`.

Kubernetes image pull error:

Make the GHCR package public or create an image pull secret.

Argo CD app is out of sync:

Check that `repoURL` and `path: k8s/overlays/dev` are correct.

