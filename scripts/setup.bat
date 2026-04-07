@echo off
setlocal enabledelayedexpansion

REM ------------------------------------------------------------
REM setup.bat - Maak/refresh .venv en installeer requirements
REM Plaats dit bestand in de ROOT van je project (waar je .py staat)
REM ------------------------------------------------------------

cd /d "%~dp0"

echo.
echo === Project: %CD% ===
echo.

REM 1) Kies python launcher (py) of python
where py >nul 2>nul
if %errorlevel%==0 (
  set "PY=py -3.11"
) else (
  set "PY=python"
)

echo Gebruik: %PY%
echo.

REM 2) Maak venv als die nog niet bestaat
if not exist ".venv\Scripts\python.exe" (
  echo [1/4] .venv aanmaken...
  %PY% -m venv .venv
  if errorlevel 1 (
    echo FOUT: kon .venv niet aanmaken.
    pause
    exit /b 1
  )
) else (
  echo [1/4] .venv bestaat al.
)

REM 3) Pip updaten
echo [2/4] pip/setuptools/wheel upgraden...
".\.venv\Scripts\python.exe" -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
  echo FOUT: pip upgrade mislukt.
  pause
  exit /b 1
)

REM 4) Installeer dependencies
if exist "requirements.txt" (
  echo [3/4] requirements.txt gevonden - installeren...
  ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
  if errorlevel 1 (
    echo FOUT: install uit requirements.txt mislukt.
    pause
    exit /b 1
  )
) else (
  echo [3/4] Geen requirements.txt - basispackages installeren...
  ".\.venv\Scripts\python.exe" -m pip install flask xlwings openpyxl pandas reportlab pillow qrcode
)

REM 5) Schrijf/refresh requirements.txt met exacte versies
echo [4/4] requirements.txt bijwerken (freeze)...
".\.venv\Scripts\python.exe" -m pip freeze > requirements.txt

echo.
echo Klaar! 
echo - Interpreter: %CD%\.venv\Scripts\python.exe
echo - requirements.txt is aanwezig/geupdate.
echo.
pause
endlocal
