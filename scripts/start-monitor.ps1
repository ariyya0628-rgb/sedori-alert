param(
  [int]$UserId = 1,
  [int]$EverySeconds = 60
)

$ErrorActionPreference = "Stop"

$runner = Join-Path $PSScriptRoot "run-scheduler-once.ps1"

while ($true) {
  $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
  Write-Output "[$timestamp] scheduler check"
  powershell -NoProfile -ExecutionPolicy Bypass -File $runner -UserId $UserId
  Start-Sleep -Seconds ([Math]::Max(10, $EverySeconds))
}
