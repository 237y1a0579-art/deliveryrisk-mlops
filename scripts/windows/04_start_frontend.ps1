$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location (Join-Path $ProjectRoot "services\frontend")

if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    throw "npm was not found. Install Node.js 22 LTS."
}

if (-not (Test-Path ".\node_modules")) {
    npm install
}

$env:VITE_API_BASE_URL = "http://127.0.0.1:8100"

Write-Host "Starting frontend at http://localhost:5173"
npm run dev
