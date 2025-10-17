@echo off
setlocal enableextensions enabledelayedexpansion

REM Build Windows exe with PyInstaller
REM Requires: pip install pyinstaller

set SCRIPT=image_generator.py
set EXENAME=image_generator.exe
set ICON=

REM Add data files: template.jpg placed next to exe
set ADDDATA=template.jpg;.

py -3 -m pip install --upgrade pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
  echo Failed to ensure pyinstaller is installed. Trying with python...
  python -m pip install --upgrade pyinstaller || goto :error
)

REM Clean previous build
if exist build rd /s /q build
if exist dist rd /s /q dist
if exist %EXENAME% del /q %EXENAME%

REM Build
py -3 -m PyInstaller --noconsole --name image_generator --onefile --add-data "%ADDDATA%" %SCRIPT%
if %errorlevel% neq 0 (
  echo PyInstaller via py failed, trying python...
  python -m PyInstaller --noconsole --name image_generator --onefile --add-data "%ADDDATA%" %SCRIPT% || goto :error
)

REM Move result
if exist dist\image_generator\image_generator.exe (
  move /y dist\image_generator\image_generator.exe %EXENAME% >nul
) else if exist dist\image_generator.exe (
  move /y dist\image_generator.exe %EXENAME% >nul
)

echo Built %EXENAME%
exit /b 0

:error
echo Build failed.
exit /b 1




