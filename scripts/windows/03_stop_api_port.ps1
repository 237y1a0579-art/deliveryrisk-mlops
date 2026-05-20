$ErrorActionPreference = "Stop"

$Port = 8000
Write-Host "Finding processes listening on port $Port..."

$Lines = netstat -ano | Select-String ":$Port\s+.*LISTENING"
$ProcessIds = @()

foreach ($Line in $Lines) {
    $Parts = ($Line.ToString() -split "\s+") | Where-Object { $_ -ne "" }
    $ProcessIds += $Parts[-1]
}

$ProcessIds = $ProcessIds | Sort-Object -Unique

if (-not $ProcessIds -or $ProcessIds.Count -eq 0) {
    Write-Host "No process is listening on port $Port."
    exit 0
}

Write-Host "Stopping processes on port ${Port}: $($ProcessIds -join ', ')"

foreach ($ProcessId in $ProcessIds) {
    Stop-Process -Id ([int]$ProcessId) -Force
}

Write-Host "Port $Port is now clean."
