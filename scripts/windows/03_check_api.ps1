$ErrorActionPreference = "Stop"

Write-Host "Checking API identity..."

$ApiBaseUrl = "http://127.0.0.1:8100"

$Root = Invoke-RestMethod "$ApiBaseUrl/"
$Health = Invoke-RestMethod "$ApiBaseUrl/health"
$OpenApi = Invoke-RestMethod "$ApiBaseUrl/openapi.json"

Write-Host ""
Write-Host "Root:"
$Root

Write-Host ""
Write-Host "Health:"
$Health

Write-Host ""
Write-Host "OpenAPI title:"
$OpenApi.info.title
