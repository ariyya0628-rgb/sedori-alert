param(
  [string]$TaskName = "SedoriAlertKeywordMonitor"
)

$ErrorActionPreference = "Stop"

$task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if (!$task) {
  Write-Output "Scheduled task was not found: $TaskName"
  exit 0
}

$info = Get-ScheduledTaskInfo -TaskName $TaskName
[pscustomobject]@{
  TaskName = $TaskName
  State = $task.State
  LastRunTime = $info.LastRunTime
  LastTaskResult = $info.LastTaskResult
  NextRunTime = $info.NextRunTime
}
