$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $ProjectRoot

Write-Host "Project root: $ProjectRoot"

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw "Python launcher 'py' was not found. Install Python 3.11 from python.org or winget."
}

py -3.11 --version
if ($LASTEXITCODE -ne 0) {
    throw "Python 3.11 was not found by the Python launcher. Run: winget install -e --id Python.Python.3.11"
}

Write-Host "Creating virtual environment with py -3.11..."
py -3.11 -m venv .venv

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    throw "Virtual environment was not created. Check your Python 3.11 installation."
}

Write-Host "Upgrading pip..."
.\.venv\Scripts\python.exe -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    throw "pip upgrade failed."
}

Write-Host "Installing project dependencies. This can take several minutes..."
.\.venv\Scripts\pip.exe install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    throw "Dependency installation failed. Fix the error above, then run this setup script again."
}

Write-Host ""
Write-Host "Setup complete."
Write-Host "Next: open a new terminal and run .\scripts\windows\01_start_mlflow.ps1"
