param(
  [int]$UserId = 1,
  [int]$Limit = 20,
  [int]$EverySeconds = 60
)

$ErrorActionPreference = "Stop"

$runner = Join-Path $PSScriptRoot "watch-keywords-once.ps1"

while ($true) {
  $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
  Write-Output "[$timestamp] registered keyword watch"
  powershell -NoProfile -ExecutionPolicy Bypass -File $runner -UserId $UserId -Limit $Limit
  Start-Sleep -Seconds ([Math]::Max(10, $EverySeconds))
}
