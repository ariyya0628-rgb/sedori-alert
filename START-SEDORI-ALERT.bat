@echo off
title Sedori Alert Server
cd /d "%~dp0"

if not exist logs mkdir logs
echo %date% %time% > logs\launcher-started.txt

echo Starting Sedori Alert...
echo.
echo Keep this window open while using the site.
echo If this window closes or shows an error, send the message shown here.
echo.

set POWERSHELL_EXE=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe

start "Sedori Alert Browser" "%POWERSHELL_EXE%" -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\wait-and-open-site.ps1" -TimeoutSeconds 120
"%POWERSHELL_EXE%" -NoProfile -ExecutionPolicy Bypass -NoExit -File "%~dp0scripts\start-site.ps1"

echo.
echo Startup command ended.
pause
