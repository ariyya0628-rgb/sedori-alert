param(
  [int]$UserId = 1,
  [int]$Limit = 20,
  [int]$EverySeconds = 60,
  [string]$LogFile = ""
)

$ErrorActionPreference = "Stop"

$runner = Join-Path $PSScriptRoot "watch-keywords-once.ps1"

function Write-MonitorLine {
  param([string]$Message)

  Write-Output $Message
  if ($LogFile) {
    $logDir = Split-Path -Parent $LogFile
    if ($logDir) {
      New-Item -ItemType Directory -Force -Path $logDir | Out-Null
    }
    Add-Content -LiteralPath $LogFile -Value $Message -Encoding UTF8
  }
}

while ($true) {
  $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
  Write-MonitorLine "[$timestamp] registered keyword watch"
  $result = powershell -NoProfile -ExecutionPolicy Bypass -File $runner -UserId $UserId -Limit $Limit 2>&1
  foreach ($line in $result) {
    Write-MonitorLine ([string]$line)
  }
  Start-Sleep -Seconds ([Math]::Max(10, $EverySeconds))
}
