$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $ProjectRoot

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    throw "Virtual environment not found. Run .\scripts\windows\00_setup.ps1 first."
}

$env:MLFLOW_TRACKING_URI = "http://127.0.0.1:5000"
$env:MLFLOW_REGISTRY_URI = "http://127.0.0.1:5000"
$env:MODEL_NAME = "deliveryrisk-late-order"
$env:PYTHONPATH = "$ProjectRoot"

function Invoke-PythonStep {
    param(
        [string]$Title,
        [string[]]$Arguments
    )

    Write-Host $Title
    & .\.venv\Scripts\python.exe @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Step failed: $Title"
    }
}

Invoke-PythonStep "Running data ingestion..." @("-m", "pipelines.ingest")

Invoke-PythonStep "Running data validation..." @("-m", "pipelines.validate")

Invoke-PythonStep "Running feature engineering..." @("-m", "pipelines.features")

Invoke-PythonStep "Training model and logging to MLflow..." @("-m", "pipelines.train")

Invoke-PythonStep "Running model promotion quality gate..." @("scripts\promote_model.py", "--set-mlflow-alias")

Write-Host ""
Write-Host "Training complete."
Write-Host "Model: models\champion.joblib"
Write-Host "Metrics: reports\model_metrics.json"
Write-Host "Promotion decision: reports\promotion_decision.json"
