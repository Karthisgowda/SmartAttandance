@echo off
echo Face Recognition Attendance System - XAMPP Installation Script
echo -------------------------------------------------------------
echo.

REM Check if XAMPP is installed
if exist "C:\xampp" (
    set XAMPP_PATH=C:\xampp
) else if exist "D:\xampp" (
    set XAMPP_PATH=D:\xampp
) else (
    echo XAMPP installation not found in C:\xampp or D:\xampp
    echo Please enter your XAMPP installation path:
    set /p XAMPP_PATH=
)

if not exist "%XAMPP_PATH%\htdocs" (
    echo Error: Invalid XAMPP path or htdocs folder not found.
    echo Installation failed.
    pause
    exit /b
)

echo.
echo Found XAMPP at: %XAMPP_PATH%
echo.

REM Create attendance_system folder in htdocs
set TARGET_DIR=%XAMPP_PATH%\htdocs\attendance_system
echo Creating directory: %TARGET_DIR%

if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

REM Copy files
echo Copying files to %TARGET_DIR%...
xcopy /E /I /Y ".\*.*" "%TARGET_DIR%"

REM Create uploads directory
if not exist "%TARGET_DIR%\uploads" mkdir "%TARGET_DIR%\uploads"

echo.
echo Installation complete!
echo.
echo Next steps:
echo 1. Start XAMPP Control Panel and ensure Apache and MySQL are running
echo 2. Open your browser and go to http://localhost/phpmyadmin
echo 3. Create a new database named 'attendance_system'
echo 4. Import the database_setup.sql file
echo 5. Access the application at http://localhost/attendance_system
echo.

pause
