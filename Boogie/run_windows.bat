@echo off
cd /d "%~dp0"
mpf game -c config.yaml
if errorlevel 1 pause
