<<<<<<< HEAD

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
=======

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
>>>>>>> 14b142486c61fce67c54e7dc87a5c29fdb29e6d5
pause