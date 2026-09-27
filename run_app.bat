@echo off
title AegisFinance Web App Launcher
echo =====================================================================
echo Launching AegisFinance AI Personal Finance ^& Financial Risk Agent...
echo =====================================================================

REM Open standalone web app in default browser
start "" "%~dp0index.html"

echo.
echo Standalone Web App opened in your default browser!
echo Location: %~dp0index.html
echo.
pause
