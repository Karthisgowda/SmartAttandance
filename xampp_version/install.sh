#!/bin/bash

echo "Face Recognition Attendance System - XAMPP Installer"
echo "==================================================="
echo

# Check for XAMPP installation in typical locations
XAMPP_PATHS=(
    "/opt/lampp"
    "/Applications/XAMPP/xamppfiles"
    "/usr/local/xampp"
)

XAMPP_PATH=""

for path in "${XAMPP_PATHS[@]}"; do
    if [ -d "$path" ]; then
        XAMPP_PATH="$path"
        break
    fi
done

if [ -z "$XAMPP_PATH" ]; then
    echo "XAMPP installation not found in standard locations."
    echo "Please install manually:"
    echo "1. Copy all files to your XAMPP htdocs folder in a directory called 'attendance_system'"
    echo "2. Start XAMPP services (Apache and MySQL)"
    echo "3. Create a database called 'attendance_system' in phpMyAdmin"
    echo "4. Import database_setup.sql to set up the tables"
    echo "5. Access the application at http://localhost/attendance_system"
    exit 1
fi

echo "XAMPP installation found at $XAMPP_PATH"
echo "Installing Face Recognition Attendance System..."

# Create directory if it doesn't exist
mkdir -p "$XAMPP_PATH/htdocs/attendance_system"

# Copy files
cp -r ./* "$XAMPP_PATH/htdocs/attendance_system/"

echo
echo "Installation completed!"
echo
echo "Next steps:"
echo "1. Start XAMPP services (Apache and MySQL)"
echo "2. Create a database called 'attendance_system' in phpMyAdmin"
echo "3. Import database_setup.sql to set up the tables"
echo "4. Access the application at http://localhost/attendance_system"
