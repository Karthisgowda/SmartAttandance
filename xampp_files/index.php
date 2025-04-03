<?php
include 'header.php';
?>

<div class="container mt-5">
    <div class="jumbotron bg-dark text-light">
        <h1 class="display-4">Face Recognition Attendance System</h1>
        <p class="lead">Welcome to the XAMPP version of the Face Recognition Attendance System</p>
        <hr class="my-4 bg-light">
        <p>Choose an option below to get started</p>
    </div>
    
    <div class="row">
        <div class="col-md-6 mb-4">
            <div class="card bg-dark text-light">
                <div class="card-body">
                    <h5 class="card-title">Register Student</h5>
                    <p class="card-text">Add a new student with photo to the system</p>
                    <a href="register.php" class="btn btn-primary">Register</a>
                </div>
            </div>
        </div>
        
        <div class="col-md-6 mb-4">
            <div class="card bg-dark text-light">
                <div class="card-body">
                    <h5 class="card-title">Mark Attendance</h5>
                    <p class="card-text">Record attendance for registered students</p>
                    <a href="attendance.php" class="btn btn-primary">Attendance</a>
                </div>
            </div>
        </div>
        
        <div class="col-md-6 mb-4">
            <div class="card bg-dark text-light">
                <div class="card-body">
                    <h5 class="card-title">View Records</h5>
                    <p class="card-text">View and search attendance records</p>
                    <a href="view.php" class="btn btn-primary">View Records</a>
                </div>
            </div>
        </div>
        
        <div class="col-md-6 mb-4">
            <div class="card bg-dark text-light">
                <div class="card-body">
                    <h5 class="card-title">Export Data</h5>
                    <p class="card-text">Export attendance records as CSV</p>
                    <a href="export.php" class="btn btn-primary">Export</a>
                </div>
            </div>
        </div>
        
        <div class="col-md-6 mb-4">
            <div class="card bg-dark text-light">
                <div class="card-body">
                    <h5 class="card-title">Import Data</h5>
                    <p class="card-text">Import data from Streamlit version</p>
                    <a href="import_data.php" class="btn btn-primary">Import</a>
                </div>
            </div>
        </div>
    </div>
</div>

<?php include 'footer.php'; ?>
