
@echo off
title THE WHISKIES - Lidkaarten systeem

echo.
echo ==========================================
echo   THE WHISKIES - Lidkaarten systeem
echo ==========================================
echo.

cd /d "%~dp0"

echo Start systeem...
echo.

powershell -NoExit -NoProfile -ExecutionPolicy Bypass -File ".\scripts\START_WHISKIES.ps1"

echo.
echo Systeem afgesloten.
pause