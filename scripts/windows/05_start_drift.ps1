$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $ProjectRoot

if (-not (Test-Path ".\.venv\Scripts\uvicorn.exe")) {
    throw "Uvicorn is not installed. Run .\scripts\windows\00_setup.ps1 first."
}

$env:REFERENCE_DATA_PATH = "data/reference/reference_features.parquet"
$env:INFERENCE_LOG_PATH = "data/production/inference_log.csv"
$env:DRIFT_REPORT_PATH = "reports/drift_report.json"
$env:PYTHONPATH = "$ProjectRoot"

Write-Host "Starting drift service at http://localhost:8010/drift/run"
.\.venv\Scripts\python.exe -m uvicorn services.monitoring.app.main:app --reload --app-dir "$ProjectRoot" --port 8010
