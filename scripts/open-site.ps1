param(
  [int]$Port = 8000,
  [int]$TimeoutSeconds = 90
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$url = "http://127.0.0.1:$Port/"
$healthUrl = "http://127.0.0.1:$Port/health"
$logs = Join-Path $root "logs"
$serverLog = Join-Path $logs "site-server.log"
$serverErrorLog = Join-Path $logs "site-server-error.log"
$serverScript = Join-Path $PSScriptRoot "start-site.ps1"

function Test-SiteHealth {
  try {
    $response = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 2
    return $response.status -eq "ok"
  } catch {
    return $false
  }
}

function Show-LastLogLines {
  param([string]$Path)

  if (Test-Path $Path) {
    Write-Host ""
    Write-Host "----- $Path -----"
    Get-Content -Path $Path -Tail 40
  }
}

function Stop-ServerProcess {
  param([System.Diagnostics.Process]$Process)

  if ($Process -and !$Process.HasExited) {
    cmd.exe /c "taskkill /PID $($Process.Id) /T /F >NUL 2>NUL"
  }
}

New-Item -ItemType Directory -Force -Path $logs | Out-Null

Write-Host ""
Write-Host "Starting Sedori Alert..."
Write-Host "Keep this window open while using the site."
Write-Host ""

if (!(Test-SiteHealth)) {
  $existing = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
  if ($existing) {
    Write-Host "Port 8000 is already in use, but Sedori Alert did not respond."
    Write-Host "Close the other startup window, then open this file again."
    Read-Host "Press Enter to close"
    exit 1
  }

  Remove-Item -Path $serverLog, $serverErrorLog -ErrorAction SilentlyContinue

  $serverProcess = Start-Process `
    -FilePath powershell.exe `
    -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $serverScript, "-Port", $Port) `
    -WorkingDirectory $root `
    -RedirectStandardOutput $serverLog `
    -RedirectStandardError $serverErrorLog `
    -PassThru `
    -WindowStyle Hidden

  Write-Host "Starting server. Please wait..."
} else {
  $serverProcess = $null
}

$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
while ((Get-Date) -lt $deadline) {
  if (Test-SiteHealth) {
    Write-Host ""
    Write-Host "Opening site: $url"
    Start-Process $url
    Write-Host ""
    Write-Host "Started. Do not close this window while using the site."
    Write-Host "When you want to stop, press Enter in this window."
    Read-Host

    Stop-ServerProcess -Process $serverProcess
    exit 0
  }

  if ($serverProcess -and $serverProcess.HasExited) {
    Write-Host ""
    Write-Host "The server stopped before the site opened."
    Show-LastLogLines -Path $serverErrorLog
    Show-LastLogLines -Path $serverLog
    Read-Host "Press Enter to close"
    exit 1
  }

  Start-Sleep -Milliseconds 500
}

Write-Host ""
Write-Host "The site did not start in time."
Show-LastLogLines -Path $serverErrorLog
Show-LastLogLines -Path $serverLog
Read-Host "Press Enter to close"
exit 1
