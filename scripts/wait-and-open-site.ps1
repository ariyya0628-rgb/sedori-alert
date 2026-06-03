param(
  [int]$Port = 8000,
  [int]$TimeoutSeconds = 60
)

$ErrorActionPreference = "Stop"

$url = "http://127.0.0.1:$Port/"
$healthUrl = "http://127.0.0.1:$Port/health"
$deadline = (Get-Date).AddSeconds($TimeoutSeconds)

while ((Get-Date) -lt $deadline) {
  try {
    $response = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 2
    if ($response.status -eq "ok") {
      Start-Process $url
      Write-Output "Opened $url"
      exit 0
    }
  } catch {
    Start-Sleep -Milliseconds 500
  }
}

throw "Sedori Alert did not start within $TimeoutSeconds seconds."
