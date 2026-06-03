param(
  [string]$TaskName = "SedoriAlertKeywordMonitor"
)

$ErrorActionPreference = "Stop"

$task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if (!$task) {
  Write-Output "Scheduled task was not found: $TaskName"
  exit 0
}

Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
Write-Output "Uninstalled scheduled task: $TaskName"
