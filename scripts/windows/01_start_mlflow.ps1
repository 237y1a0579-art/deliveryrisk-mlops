$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $ProjectRoot

if (-not (Test-Path ".\.venv\Scripts\mlflow.exe")) {
    throw "MLflow is not installed. Run .\scripts\windows\00_setup.ps1 first."
}

Write-Host "Starting MLflow at http://localhost:5000"
.\.venv\Scripts\mlflow.exe server `
    --host 0.0.0.0 `
    --port 5000 `
    --backend-store-uri sqlite:///mlflow.db `
    --default-artifact-root ./mlartifacts

