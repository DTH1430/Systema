@echo off
REM SystemScanner Build Script
REM This script rebuilds the executable with anti-virus mitigation features

echo ========================================================================
echo SystemScanner - Build Script
echo ========================================================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Clean previous build
echo [1/4] Cleaning previous build artifacts...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo    Done.
echo.

REM Check if virtual environment exists
if exist scanner_env\Scripts\activate.bat (
    echo [2/4] Activating virtual environment...
    call scanner_env\Scripts\activate.bat
    echo    Done.
    echo.
) else (
    echo WARNING: Virtual environment not found at scanner_env\
    echo Using system Python instead...
    echo.
)

REM Check if PyInstaller is installed
echo [3/4] Checking PyInstaller...
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: PyInstaller not found!
    echo Install with: pip install pyinstaller
    pause
    exit /b 1
)
echo    PyInstaller found.
echo.

REM Build the executable
echo [4/4] Building executable with enhanced configuration...
echo    - Adding version information
echo    - Adding UAC manifest
echo    - Including PDF reporter
echo    - Enabling console for transparency
echo.
pyinstaller SystemScanner.spec --clean

REM Check if build was successful
echo.
echo ========================================================================
if exist dist\SystemScanner.exe (
    echo BUILD SUCCESSFUL!
    echo ========================================================================
    echo.
    echo Executable location: dist\SystemScanner.exe
    echo.

    REM Show file information
    for %%I in (dist\SystemScanner.exe) do (
        echo File size: %%~zI bytes ^(%%~zI / 1024 / 1024 MB^)
        echo Created: %%~tI
    )

    echo.
    echo ========================================================================
    echo NEXT STEPS:
    echo ========================================================================
    echo.
    echo 1. Verify version information:
    echo    Right-click dist\SystemScanner.exe ^> Properties ^> Details
    echo.
    echo 2. Test the executable:
    echo    cd dist
    echo    SystemScanner.exe
    echo.
    echo 3. If Windows Security flags it:
    echo    Read WHITELIST_INSTRUCTIONS.md for solutions
    echo.
    echo 4. Check VirusTotal scan:
    echo    Upload to https://www.virustotal.com
    echo.
    echo ========================================================================
    echo ANTI-VIRUS MITIGATION FEATURES:
    echo ========================================================================
    echo.
    echo - Version information added
    echo - UAC manifest included
    echo - Console window enabled ^(transparency^)
    echo - Proper file description
    echo - Company and copyright info
    echo.
    echo To further reduce false positives, consider:
    echo - Code signing certificate ^($200-400/year^)
    echo - Submitting to Microsoft as false positive
    echo.

) else (
    echo BUILD FAILED!
    echo ========================================================================
    echo.
    echo Check the error messages above for details.
    echo.
    echo Common issues:
    echo - PyInstaller not installed: pip install pyinstaller
    echo - Missing dependencies: pip install -r requirements.txt
    echo - Python not in PATH
    echo.
)

echo.
pause
