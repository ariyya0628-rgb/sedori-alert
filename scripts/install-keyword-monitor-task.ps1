param(
  [int]$UserId = 1,
  [int]$Limit = 20,
  [int]$EverySeconds = 60,
  [string]$TaskName = "SedoriAlertKeywordMonitor"
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$monitor = Join-Path $PSScriptRoot "start-keyword-monitor.ps1"
$logFile = Join-Path $root "logs\keyword-monitor.log"

if (!(Test-Path $monitor)) {
  throw "Keyword monitor script was not found: $monitor"
}

$argument = @(
  "-NoProfile",
  "-ExecutionPolicy", "Bypass",
  "-File", "`"$monitor`"",
  "-UserId", $UserId,
  "-Limit", $Limit,
  "-EverySeconds", $EverySeconds,
  "-LogFile", "`"$logFile`""
) -join " "

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $argument -WorkingDirectory $root
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet `
  -AllowStartIfOnBatteries `
  -DontStopIfGoingOnBatteries `
  -ExecutionTimeLimit (New-TimeSpan -Days 30) `
  -RestartCount 3 `
  -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask `
  -TaskName $TaskName `
  -Action $action `
  -Trigger $trigger `
  -Settings $settings `
  -Description "Runs Sedori Alert registered keyword monitoring while the user is logged in." `
  -Force | Out-Null

Write-Output "Installed scheduled task: $TaskName"
Write-Output "Log file: $logFile"
