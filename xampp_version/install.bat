@echo off
echo Face Recognition Attendance System - XAMPP Installer
echo ===================================================
echo.

IF EXIST "C:\xampp" (
    echo XAMPP installation found at C:\xampp
    echo Installing Face Recognition Attendance System...
    
    mkdir "C:\xampp\htdocs\attendance_system" 2>nul
    
    echo Copying files...
    xcopy /E /I /Y *.* "C:\xampp\htdocs\attendance_system\"
    
    echo.
    echo Installation completed!
    echo.
    echo Next steps:
    echo 1. Start XAMPP services (Apache and MySQL)
    echo 2. Create a database called 'attendance_system' in phpMyAdmin
    echo 3. Import database_setup.sql to set up the tables
    echo 4. Access the application at http://localhost/attendance_system
) ELSE (
    echo XAMPP installation not found at the default location C:\xampp
    echo.
    echo Please install the system manually:
    echo 1. Copy all files to your XAMPP htdocs folder in a directory called 'attendance_system'
    echo 2. Start XAMPP services (Apache and MySQL)
    echo 3. Create a database called 'attendance_system' in phpMyAdmin
    echo 4. Import database_setup.sql to set up the tables
    echo 5. Access the application at http://localhost/attendance_system
)

echo.
pause
