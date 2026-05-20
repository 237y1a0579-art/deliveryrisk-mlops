$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $ProjectRoot

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    throw "Virtual environment not found. Run .\scripts\windows\00_setup.ps1 first."
}

Write-Host "Running Ruff..."
.\.venv\Scripts\python.exe -m ruff check .
if ($LASTEXITCODE -ne 0) {
    throw "Ruff failed."
}

Write-Host "Running Pytest..."
.\.venv\Scripts\python.exe -m pytest
if ($LASTEXITCODE -ne 0) {
    throw "Pytest failed."
}
