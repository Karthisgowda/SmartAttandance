# Face Recognition Attendance System - XAMPP Version

## Setup Instructions

### Prerequisites
- XAMPP installed (with Apache and MySQL)
- A web browser

### Step 1: Database Setup
1. Start XAMPP Control Panel and ensure Apache and MySQL services are running
2. Access phpMyAdmin at http://localhost/phpmyadmin
3. Create a new database named `attendance_system`
4. Execute the following SQL to create the required tables:

```sql
-- Create students table
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    photo_path VARCHAR(255)
);

-- Create attendance table
CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(id)
);
```

### Step 2: Application Setup
1. Copy all files from this folder to your XAMPP htdocs directory:
   - Windows: C:\xampp\htdocs\attendance_system\
   - Mac: /Applications/XAMPP/htdocs/attendance_system/
   - Linux: /opt/lampp/htdocs/attendance_system/

2. Make sure the uploads folder has write permissions:
   - Windows: Right-click folder → Properties → Security → Edit → Allow write permissions
   - Mac/Linux: From terminal, run `chmod 777 uploads`

### Step 3: Accessing the Application
1. Open your browser and go to http://localhost/attendance_system
2. The application should be ready to use with the following features:
   - Register new students with photos
   - Mark attendance for registered students
   - View attendance by date
   - Export attendance records as CSV

### Step 4: Migrating Data from Streamlit Version
1. Export your attendance records from the Streamlit app using the "Download Attendance History" button
2. Copy student photos from data/faces/ to the uploads/ folder
3. You'll need to manually import the student data into the MySQL database

### Optional: Customization
- You can customize the appearance by editing css/style.css
- Add more features by modifying the PHP files

### Troubleshooting
- If you encounter file upload errors, check the permissions of the uploads folder
- For database connection issues, verify your MySQL username and password in db_connection.php
