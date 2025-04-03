Face Recognition Attendance System - XAMPP Version
=================================================

This package contains the XAMPP version of the Face Recognition Attendance System.
Follow the installation instructions below to set up the system on your local machine.

Installation Instructions:
-------------------------

Windows Users:
1. Extract the downloaded ZIP file
2. Run install.bat to automatically install to XAMPP
   - This will copy all files to your XAMPP htdocs folder
   - Alternatively, manually copy the files to your XAMPP installation
3. Start XAMPP services (Apache and MySQL)
4. Open your web browser and navigate to http://localhost/phpmyadmin
5. Create a new database called 'attendance_system'
6. Import database_setup.sql to set up the tables
7. Access the application at http://localhost/attendance_system

Mac/Linux Users:
1. Extract the downloaded TAR.GZ file
2. Run install.sh to automatically install to XAMPP
   - This will copy all files to your XAMPP htdocs folder
   - You may need to provide execute permissions: chmod +x install.sh
3. Start XAMPP services (Apache and MySQL)
4. Open your web browser and navigate to http://localhost/phpmyadmin
5. Create a new database called 'attendance_system'
6. Import database_setup.sql to set up the tables
7. Access the application at http://localhost/attendance_system

Manual Installation (All Platforms):
1. Extract the downloaded file
2. Copy all the files to your XAMPP htdocs folder in a directory called 'attendance_system'
3. Start XAMPP services (Apache and MySQL)
4. Open your web browser and navigate to http://localhost/phpmyadmin
5. Create a new database called 'attendance_system'
6. Import database_setup.sql to set up the tables
7. Access the application at http://localhost/attendance_system

Data Migration from Streamlit Version:
-------------------------------------
If you want to migrate your data from the Streamlit app:

1. Download your attendance history from the Streamlit app
2. In the XAMPP version, go to "Import Data" page
3. Upload the CSV file to import student information and attendance records
4. Copy student photos from the Streamlit app's data/student_images folder to the uploads folder

System Requirements:
------------------
- XAMPP 7.4 or newer
- Web browser (Chrome, Firefox, Edge, Safari)
- 50MB free disk space
- 512MB RAM minimum

For support or questions, please contact the developer.
