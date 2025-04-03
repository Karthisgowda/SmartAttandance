#!/bin/bash

echo "Face Recognition Attendance System - XAMPP Installation Script"
echo "-------------------------------------------------------------"
echo ""

# Detect OS and set default XAMPP paths
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    DEFAULT_XAMPP_PATH="/Applications/XAMPP"
else
    # Linux
    DEFAULT_XAMPP_PATH="/opt/lampp"
fi

# Check if XAMPP exists at default location
if [ -d "$DEFAULT_XAMPP_PATH" ]; then
    XAMPP_PATH=$DEFAULT_XAMPP_PATH
else
    echo "XAMPP installation not found at $DEFAULT_XAMPP_PATH"
    echo "Please enter your XAMPP installation path:"
    read XAMPP_PATH
fi

if [ ! -d "$XAMPP_PATH/htdocs" ]; then
    echo "Error: Invalid XAMPP path or htdocs folder not found."
    echo "Installation failed."
    exit 1
fi

echo ""
echo "Found XAMPP at: $XAMPP_PATH"
echo ""

# Create attendance_system folder in htdocs
TARGET_DIR="$XAMPP_PATH/htdocs/attendance_system"
echo "Creating directory: $TARGET_DIR"

mkdir -p "$TARGET_DIR"

# Copy files
echo "Copying files to $TARGET_DIR..."
cp -R ./* "$TARGET_DIR/"

# Create uploads directory
mkdir -p "$TARGET_DIR/uploads"
chmod 777 "$TARGET_DIR/uploads"

echo ""
echo "Installation complete!"
echo ""
echo "Next steps:"
echo "1. Start XAMPP and ensure Apache and MySQL are running"
echo "2. Open your browser and go to http://localhost/phpmyadmin"
echo "3. Create a new database named 'attendance_system'"
echo "4. Import the database_setup.sql file"
echo "5. Access the application at http://localhost/attendance_system"
echo ""

read -p "Press Enter to continue..." key
