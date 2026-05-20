$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $ProjectRoot

if (-not (Test-Path ".\.venv\Scripts\uvicorn.exe")) {
    throw "Uvicorn is not installed. Run .\scripts\windows\00_setup.ps1 first."
}

$ApiPort = 8100
$env:MODEL_PATH = "models/champion.joblib"
$env:INFERENCE_LOG_PATH = "data/production/inference_log.csv"
$env:PYTHONPATH = "$ProjectRoot"

Write-Host "Import check:"
.\.venv\Scripts\python.exe -c "import services.api.app.main as m; print(m.__file__)"

Write-Host "Starting API at http://127.0.0.1:${ApiPort}/docs"
.\.venv\Scripts\python.exe -m uvicorn services.api.app.main:app --app-dir "$ProjectRoot" --host 127.0.0.1 --port $ApiPort
