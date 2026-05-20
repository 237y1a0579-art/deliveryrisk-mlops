# Start Here on Windows

Your clean project folder is:

```text
C:\Users\konda\Documents\DeliveryRisk-MLOps
```

Do not type the folder path by itself in PowerShell. A folder path is not a command.

Use one of these instead:

```powershell
cd "C:\Users\konda\Documents\DeliveryRisk-MLOps"
```

or open it directly in VS Code:

```powershell
code "C:\Users\konda\Documents\DeliveryRisk-MLOps"
```

If you use Antigravity, open the same folder:

```text
C:\Users\konda\Documents\DeliveryRisk-MLOps
```

## First-Time Setup

Open VS Code or Antigravity terminal as PowerShell.

Run:

```powershell
cd "C:\Users\konda\Documents\DeliveryRisk-MLOps"
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\scripts\windows\00_setup.ps1
```

## Run the Project Step by Step

Keep each long-running service in its own terminal.

### Optional: Check Environment

```powershell
cd "C:\Users\konda\Documents\DeliveryRisk-MLOps"
.\scripts\windows\00_check_environment.ps1
```

If this command pauses while importing packages, wait. Do not press `Ctrl+C`.

### Terminal 1: MLflow

```powershell
cd "C:\Users\konda\Documents\DeliveryRisk-MLOps"
.\scripts\windows\01_start_mlflow.ps1
```

Open in browser:

```text
http://localhost:5000
```

### Terminal 2: Train the Model

```powershell
cd "C:\Users\konda\Documents\DeliveryRisk-MLOps"
.\scripts\windows\02_run_training_pipeline.ps1
```

This creates:

```text
models/champion.joblib
reports/model_metrics.json
reports/promotion_decision.json
```

### Terminal 3: Backend API

```powershell
cd "C:\Users\konda\Documents\DeliveryRisk-MLOps"
.\scripts\windows\03_start_api.ps1
```

Open in browser:

```text
http://127.0.0.1:8100/docs
```

### Terminal 4: Frontend Dashboard

```powershell
cd "C:\Users\konda\Documents\DeliveryRisk-MLOps"
.\scripts\windows\04_start_frontend.ps1
```

Open in browser:

```text
http://localhost:5173
```

Click **Score** a few times in the dashboard. That creates inference logs for monitoring.

### Terminal 5: Drift Detection

```powershell
cd "C:\Users\konda\Documents\DeliveryRisk-MLOps"
.\scripts\windows\05_start_drift.ps1
```

Open in browser:

```text
http://localhost:8010/drift/run
```

### Terminal 6: Tests

```powershell
cd "C:\Users\konda\Documents\DeliveryRisk-MLOps"
.\scripts\windows\06_run_tests.ps1
```

## Run with Docker Compose

First open Docker Desktop and wait until it is running.

Then:

```powershell
cd "C:\Users\konda\Documents\DeliveryRisk-MLOps"
.\scripts\windows\07_docker_compose_up.ps1
```

## Most Common Mistake

Wrong:

```powershell
C:\Users\konda\Documents\DeliveryRisk-MLOps
```

Correct:

```powershell
cd "C:\Users\konda\Documents\DeliveryRisk-MLOps"
```

or:

```powershell
code "C:\Users\konda\Documents\DeliveryRisk-MLOps"
```
