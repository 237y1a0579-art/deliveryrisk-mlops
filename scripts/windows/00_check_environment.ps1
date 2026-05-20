$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $ProjectRoot

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    throw "Virtual environment not found. Run .\scripts\windows\00_setup.ps1 first."
}

Write-Host "Checking Python..."
.\.venv\Scripts\python.exe --version

Write-Host "Checking core Python packages..."
.\.venv\Scripts\python.exe -c "import pandas as pd; import numpy as np; import pyarrow as pa; import sklearn; import mlflow; print('pandas', pd.__version__); print('numpy', np.__version__); print('pyarrow', pa.__version__); print('sklearn', sklearn.__version__); print('mlflow', mlflow.__version__)"

Write-Host ""
Write-Host "Environment check passed."
