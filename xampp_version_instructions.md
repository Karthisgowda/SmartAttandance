# Face Recognition Attendance System - XAMPP Version

## How to Run on XAMPP

### Prerequisites
1. XAMPP installed (with Apache and MySQL)
2. Basic knowledge of PHP and MySQL
3. Your current attendance data (if you want to migrate existing records)

### Step 1: Database Setup
1. Start XAMPP Control Panel and ensure Apache and MySQL services are running
2. Access phpMyAdmin at `http://localhost/phpmyadmin`
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

### Step 2: Copy Application Files
1. Create a folder named `attendance_system` in your XAMPP htdocs directory:
   - Windows: `C:\xampp\htdocs\attendance_system\`
   - Mac: `/Applications/XAMPP/htdocs/attendance_system/`
   - Linux: `/opt/lampp/htdocs/attendance_system/`

2. Create the following files in this folder:

#### db_connection.php
```php
<?php
// Database connection settings
$servername = "localhost";
$username = "root";     // Default XAMPP username
$password = "";         // Default XAMPP password is empty
$dbname = "attendance_system";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}
?>
```

#### index.php
```php
<?php include 'header.php'; ?>

<div class="container mt-5">
    <div class="jumbotron bg-dark text-light">
        <h1 class="display-4">Face Recognition Attendance System</h1>
        <p class="lead">Welcome to the attendance management system</p>
        <hr class="my-4 bg-light">
        <div class="row">
            <div class="col-md-4">
                <div class="card bg-dark text-light mb-4">
                    <div class="card-body">
                        <h5 class="card-title">Register New Student</h5>
                        <p class="card-text">Add a new student to the system with photo.</p>
                        <a href="register.php" class="btn btn-primary">Register</a>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card bg-dark text-light mb-4">
                    <div class="card-body">
                        <h5 class="card-title">Mark Attendance</h5>
                        <p class="card-text">Mark attendance for registered students.</p>
                        <a href="attendance.php" class="btn btn-primary">Attendance</a>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card bg-dark text-light mb-4">
                    <div class="card-body">
                        <h5 class="card-title">View Attendance</h5>
                        <p class="card-text">View and export attendance records.</p>
                        <a href="view.php" class="btn btn-primary">View Records</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<?php include 'footer.php'; ?>
```

#### header.php
```php
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Attendance System</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="css/style.css">
</head>
<body class="bg-dark text-light">
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="index.php">Attendance System</a>
            <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ml-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="index.php">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="register.php">Register</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="attendance.php">Attendance</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="view.php">View Records</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
```

#### footer.php
```php
    <footer class="mt-5 py-3 text-center">
        <div class="container">
            <p>&copy; <?php echo date('Y'); ?> Face Recognition Attendance System</p>
        </div>
    </footer>

    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="js/script.js"></script>
</body>
</html>
```

#### register.php
```php
<?php
include 'header.php';
include 'db_connection.php';

$message = '';

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $name = $_POST['name'];
    
    // Check if file was uploaded without errors
    if (isset($_FILES["photo"]) && $_FILES["photo"]["error"] == 0) {
        $allowed = ["jpg" => "image/jpg", "jpeg" => "image/jpeg", "png" => "image/png"];
        $filename = $_FILES["photo"]["name"];
        $filetype = $_FILES["photo"]["type"];
        $filesize = $_FILES["photo"]["size"];
    
        // Verify file extension
        $ext = pathinfo($filename, PATHINFO_EXTENSION);
        if (!array_key_exists($ext, $allowed)) {
            $message = "Error: Please select a valid file format.";
        }
    
        // Verify file size - 5MB maximum
        $maxsize = 5 * 1024 * 1024;
        if ($filesize > $maxsize) {
            $message = "Error: File size is larger than the allowed limit.";
        }
    
        // Verify MIME type of the file
        if (in_array($filetype, $allowed)) {
            // Check if file exists before uploading
            $newFilename = uniqid() . "." . $ext;
            $targetFilePath = "uploads/" . $newFilename;
            
            // Upload file
            if (move_uploaded_file($_FILES["photo"]["tmp_name"], $targetFilePath)) {
                // Insert student record
                $sql = "INSERT INTO students (name, photo_path) VALUES ('$name', '$targetFilePath')";
                
                if ($conn->query($sql) === TRUE) {
                    $message = "Student registered successfully.";
                } else {
                    $message = "Error: " . $sql . "<br>" . $conn->error;
                }
            } else {
                $message = "Error: There was an error uploading your file.";
            }
        } else {
            $message = "Error: There was a problem with the file upload. Please try again.";
        }
    } else {
        $message = "Error: " . $_FILES["photo"]["error"];
    }
}
?>

<div class="container mt-5">
    <div class="card bg-dark text-light">
        <div class="card-header">
            <h2>Register New Student</h2>
        </div>
        <div class="card-body">
            <?php if($message): ?>
                <div class="alert alert-info"><?php echo $message; ?></div>
            <?php endif; ?>
            
            <form method="post" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="name">Student Name</label>
                    <input type="text" class="form-control" id="name" name="name" required>
                </div>
                <div class="form-group">
                    <label for="photo">Upload Photo</label>
                    <input type="file" class="form-control-file" id="photo" name="photo" required>
                </div>
                <button type="submit" class="btn btn-primary">Register</button>
            </form>
        </div>
    </div>
</div>

<?php include 'footer.php'; ?>
```

#### attendance.php
```php
<?php
include 'header.php';
include 'db_connection.php';

$message = '';
$today = date('Y-m-d');

// Get all students
$sql = "SELECT * FROM students";
$result = $conn->query($sql);
$students = [];

if ($result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
        $students[] = $row;
    }
}

// Mark attendance
if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['student_id'])) {
    $student_id = $_POST['student_id'];
    $current_time = date('H:i:s');
    
    // Check if attendance already marked for today
    $check_sql = "SELECT * FROM attendance WHERE student_id = $student_id AND date = '$today'";
    $check_result = $conn->query($check_sql);
    
    if ($check_result->num_rows > 0) {
        $message = "Attendance already marked for this student today.";
    } else {
        // Insert attendance record
        $sql = "INSERT INTO attendance (student_id, date, time) VALUES ($student_id, '$today', '$current_time')";
        
        if ($conn->query($sql) === TRUE) {
            $message = "Attendance marked successfully.";
        } else {
            $message = "Error: " . $sql . "<br>" . $conn->error;
        }
    }
}

// Get today's attendance records
$today_sql = "SELECT a.*, s.name FROM attendance a JOIN students s ON a.student_id = s.id WHERE a.date = '$today'";
$today_result = $conn->query($today_sql);
$today_attendance = [];

if ($today_result->num_rows > 0) {
    while($row = $today_result->fetch_assoc()) {
        $today_attendance[] = $row;
    }
}
?>

<div class="container mt-5">
    <div class="row">
        <div class="col-md-6">
            <div class="card bg-dark text-light">
                <div class="card-header">
                    <h2>Mark Attendance</h2>
                </div>
                <div class="card-body">
                    <?php if($message): ?>
                        <div class="alert alert-info"><?php echo $message; ?></div>
                    <?php endif; ?>
                    
                    <?php if(count($students) > 0): ?>
                        <form method="post">
                            <div class="form-group">
                                <label for="student_id">Select Student</label>
                                <select class="form-control" id="student_id" name="student_id" required>
                                    <option value="">-- Select Student --</option>
                                    <?php foreach($students as $student): ?>
                                        <option value="<?php echo $student['id']; ?>"><?php echo $student['name']; ?></option>
                                    <?php endforeach; ?>
                                </select>
                            </div>
                            <button type="submit" class="btn btn-primary">Mark Present</button>
                        </form>
                    <?php else: ?>
                        <div class="alert alert-warning">No students registered yet. Please register students first.</div>
                    <?php endif; ?>
                </div>
            </div>
        </div>
        
        <div class="col-md-6">
            <div class="card bg-dark text-light">
                <div class="card-header">
                    <h2>Today's Attendance</h2>
                </div>
                <div class="card-body">
                    <?php if(count($today_attendance) > 0): ?>
                        <ul class="list-group">
                            <?php foreach($today_attendance as $record): ?>
                                <li class="list-group-item bg-dark text-light border-light">
                                    ✅ <?php echo $record['name']; ?> - <?php echo $record['time']; ?>
                                </li>
                            <?php endforeach; ?>
                        </ul>
                    <?php else: ?>
                        <div class="alert alert-info">No attendance marked yet for today</div>
                    <?php endif; ?>
                </div>
            </div>
        </div>
    </div>
</div>

<?php include 'footer.php'; ?>
```

#### view.php
```php
<?php
include 'header.php';
include 'db_connection.php';

// Get all students
$sql = "SELECT * FROM students";
$result = $conn->query($sql);
$students = [];

if ($result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
        $students[$row['id']] = $row['name'];
    }
}

// Date filter
$selected_date = isset($_GET['date']) ? $_GET['date'] : date('Y-m-d');

// Get attendance for selected date
$date_sql = "SELECT a.*, s.name FROM attendance a JOIN students s ON a.student_id = s.id WHERE a.date = '$selected_date'";
$date_result = $conn->query($date_sql);
$date_attendance = [];

if ($date_result->num_rows > 0) {
    while($row = $date_result->fetch_assoc()) {
        $date_attendance[] = $row;
    }
}

// Get all dates with attendance records
$dates_sql = "SELECT DISTINCT date FROM attendance ORDER BY date DESC";
$dates_result = $conn->query($dates_sql);
$dates = [];

if ($dates_result->num_rows > 0) {
    while($row = $dates_result->fetch_assoc()) {
        $dates[] = $row['date'];
    }
}
?>

<div class="container mt-5">
    <div class="card bg-dark text-light">
        <div class="card-header">
            <h2>View Attendance Records</h2>
        </div>
        <div class="card-body">
            <form method="get" class="mb-4">
                <div class="form-group">
                    <label for="date">Select Date</label>
                    <input type="date" class="form-control" id="date" name="date" value="<?php echo $selected_date; ?>">
                </div>
                <button type="submit" class="btn btn-primary">View Records</button>
            </form>
            
            <?php if(count($date_attendance) > 0): ?>
                <h3>Attendance for <?php echo $selected_date; ?></h3>
                <table class="table table-dark">
                    <thead>
                        <tr>
                            <th>Student Name</th>
                            <th>Time</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach($date_attendance as $record): ?>
                            <tr>
                                <td><?php echo $record['name']; ?></td>
                                <td><?php echo $record['time']; ?></td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            <?php else: ?>
                <div class="alert alert-info">No attendance records for <?php echo $selected_date; ?></div>
            <?php endif; ?>
            
            <hr class="bg-light my-4">
            
            <h3>Overall Attendance History</h3>
            <?php if(count($dates) > 0 && count($students) > 0): ?>
                <div class="table-responsive">
                    <table class="table table-dark">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <?php foreach($students as $id => $name): ?>
                                    <th><?php echo $name; ?></th>
                                <?php endforeach; ?>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach($dates as $date): ?>
                                <tr>
                                    <td><?php echo $date; ?></td>
                                    <?php 
                                    // Get attendance for this date
                                    $date_records_sql = "SELECT * FROM attendance WHERE date = '$date'";
                                    $date_records_result = $conn->query($date_records_sql);
                                    $date_records = [];
                                    
                                    if ($date_records_result->num_rows > 0) {
                                        while($row = $date_records_result->fetch_assoc()) {
                                            $date_records[$row['student_id']] = $row['time'];
                                        }
                                    }
                                    
                                    foreach($students as $id => $name): 
                                    ?>
                                        <td>
                                            <?php echo isset($date_records[$id]) ? 'Present' : 'Absent'; ?>
                                        </td>
                                    <?php endforeach; ?>
                                </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>
                
                <a href="export.php" class="btn btn-success mt-3">Export Attendance Records (CSV)</a>
            <?php else: ?>
                <div class="alert alert-info">No attendance records found.</div>
            <?php endif; ?>
        </div>
    </div>
</div>

<?php include 'footer.php'; ?>
```

#### export.php
```php
<?php
include 'db_connection.php';

// Set headers for CSV download
header('Content-Type: text/csv');
header('Content-Disposition: attachment; filename="attendance_records.csv"');

// Create a file pointer connected to the output stream
$output = fopen('php://output', 'w');

// Add column headers
fputcsv($output, ['Date', 'Student Name', 'Time']);

// Get all attendance records
$sql = "SELECT a.date, s.name, a.time FROM attendance a 
        JOIN students s ON a.student_id = s.id 
        ORDER BY a.date DESC, s.name";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
    // Output each row of the data
    while($row = $result->fetch_assoc()) {
        fputcsv($output, $row);
    }
}

fclose($output);
exit;
?>
```

#### css/style.css
```css
body {
    background-color: #121212;
    color: #f8f9fa;
}

.card {
    border-color: #343a40;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
    transition: transform 0.3s;
}

.card:hover {
    transform: translateY(-5px);
}

.jumbotron {
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
    background: linear-gradient(to right, #1a2a6c, #b21f1f, #fdbb2d);
    animation: gradient 15s ease infinite;
    background-size: 400% 400%;
}

@keyframes gradient {
    0% {
        background-position: 0% 50%;
    }
    50% {
        background-position: 100% 50%;
    }
    100% {
        background-position: 0% 50%;
    }
}

.list-group-item {
    transition: background-color 0.3s;
}

.list-group-item:hover {
    background-color: #2d3748 !important;
}

.table-dark {
    background-color: #1e1e1e;
}

.btn-primary {
    background-color: #4c75f2;
    border-color: #4c75f2;
}

.btn-primary:hover {
    background-color: #3a5bbf;
    border-color: #3a5bbf;
}
```

#### js/script.js
```javascript
// Add animation to cards
document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.card');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 8px 16px rgba(0, 0, 0, 0.5)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.5)';
        });
    });
});
```

### Step 3: Create Folders
1. Create the following folders in your application folder:
   - `uploads` - For storing student photos
   - `css` - For CSS files
   - `js` - For JavaScript files

### Step 4: Migration Instructions
1. Export your CSV attendance records from the Streamlit application
2. Copy student photos from `data/faces/` to the `uploads/` folder
3. Create a PHP script to import the data (optional)

### Step 5: Access Your Application
1. Open your browser and go to `http://localhost/attendance_system`

## Additional Information

### Database Schema
```
students
 ├─ id (INT, PK, auto_increment)
 ├─ name (VARCHAR)
 └─ photo_path (VARCHAR)

attendance
 ├─ id (INT, PK, auto_increment)
 ├─ student_id (INT, FK -> students.id)
 ├─ date (DATE)
 └─ time (TIME)
```

### Security Notes
- The default configuration uses the default XAMPP credentials (username: root, no password)
- For production, you should set a proper MySQL password and update the connection details
- Add proper validation and security measures before deploying to a public environment