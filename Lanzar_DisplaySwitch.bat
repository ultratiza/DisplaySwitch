@echo off
if exist "%~dp0MonitorSwitch.exe" (
    start "" "%~dp0MonitorSwitch.exe"
) else (
    start "" pythonw "%~dp0main.py"
)
