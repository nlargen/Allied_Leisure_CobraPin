@echo off
cd /d "%~dp0"
mpf game -b -c config.yaml
if errorlevel 1 pause
