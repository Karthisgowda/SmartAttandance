<?php
include 'header.php';
include 'db_connection.php';

$message = '';
$messageType = '';

// Mark attendance
if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['student_id'])) {
    $student_id = $_POST['student_id'];
    $date = date('Y-m-d');
    $time = date('H:i:s');
    
    // Check if attendance already marked for today
    $check_sql = "SELECT * FROM attendance WHERE student_id = '$student_id' AND date = '$date'";
    $check_result = $conn->query($check_sql);
    
    if ($check_result->num_rows > 0) {
        $message = "Attendance already marked for this student today!";
        $messageType = "warning";
    } else {
        // Insert attendance record
        $sql = "INSERT INTO attendance (student_id, date, time) VALUES ('$student_id', '$date', '$time')";
        
        if ($conn->query($sql) === TRUE) {
            // Get student name for confirmation message
            $name_sql = "SELECT name FROM students WHERE id = '$student_id'";
            $name_result = $conn->query($name_sql);
            
            if ($name_result->num_rows > 0) {
                $student = $name_result->fetch_assoc();
                $message = "Attendance marked for " . $student['name'] . " at " . $time;
                $messageType = "success";
            } else {
                $message = "Attendance marked successfully!";
                $messageType = "success";
            }
        } else {
            $message = "Error: " . $sql . "<br>" . $conn->error;
            $messageType = "danger";
        }
    }
}

// Get list of students for dropdown
$students = array();
$sql = "SELECT * FROM students ORDER BY name";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
        $students[] = $row;
    }
}

// Get today's attendance
$today_attendance = array();
$today = date('Y-m-d');
$today_sql = "SELECT a.*, s.name, s.photo_path 
              FROM attendance a 
              JOIN students s ON a.student_id = s.id 
              WHERE a.date = '$today' 
              ORDER BY a.time DESC";
$today_result = $conn->query($today_sql);

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
                    <?php if ($message): ?>
                        <div class="alert alert-<?php echo $messageType; ?>"><?php echo $message; ?></div>
                    <?php endif; ?>
                    
                    <?php if (count($students) > 0): ?>
                        <form method="post">
                            <div class="form-group">
                                <label for="student_id">Select Student</label>
                                <select class="form-control" id="student_id" name="student_id" required>
                                    <option value="">-- Select Student --</option>
                                    <?php foreach ($students as $student): ?>
                                        <option value="<?php echo $student['id']; ?>"><?php echo $student['name']; ?></option>
                                    <?php endforeach; ?>
                                </select>
                            </div>
                            
                            <div class="form-group">
                                <label>Current Date & Time</label>
                                <input type="text" class="form-control" value="<?php echo date('Y-m-d H:i:s'); ?>" readonly>
                            </div>
                            
                            <button type="submit" class="btn btn-primary">Mark Attendance</button>
                        </form>
                    <?php else: ?>
                        <div class="alert alert-warning">
                            No students registered. <a href="register.php" class="alert-link">Register students</a> first.
                        </div>
                    <?php endif; ?>
                </div>
            </div>
            
            <!-- Student Gallery for quick selection -->
            <?php if (count($students) > 0): ?>
                <div class="card bg-dark text-light mt-4">
                    <div class="card-header">
                        <h3>Quick Selection</h3>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <?php foreach ($students as $student): ?>
                                <div class="col-md-4 col-sm-6 mb-3">
                                    <div class="card bg-dark student-card" onclick="selectStudent(<?php echo $student['id']; ?>)">
                                        <?php if ($student['photo_path']): ?>
                                            <img src="<?php echo $student['photo_path']; ?>" class="card-img-top student-image" alt="<?php echo $student['name']; ?>">
                                        <?php else: ?>
                                            <div class="card-img-top student-image bg-secondary d-flex justify-content-center align-items-center">
                                                <i class="fa fa-user fa-3x text-light"></i>
                                            </div>
                                        <?php endif; ?>
                                        <div class="card-body p-2 text-center">
                                            <h6 class="card-title mb-0"><?php echo $student['name']; ?></h6>
                                        </div>
                                    </div>
                                </div>
                            <?php endforeach; ?>
                        </div>
                    </div>
                </div>
            <?php endif; ?>
        </div>
        
        <div class="col-md-6">
            <div class="card bg-dark text-light">
                <div class="card-header">
                    <h2>Today's Attendance</h2>
                    <span class="text-muted">Date: <?php echo date('Y-m-d (l)'); ?></span>
                </div>
                <div class="card-body">
                    <?php if (count($today_attendance) > 0): ?>
                        <div class="table-responsive">
                            <table class="table table-dark">
                                <thead>
                                    <tr>
                                        <th>Student</th>
                                        <th>Time</th>
                                        <th>Photo</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <?php foreach ($today_attendance as $record): ?>
                                        <tr>
                                            <td><?php echo $record['name']; ?></td>
                                            <td><?php echo date('h:i A', strtotime($record['time'])); ?></td>
                                            <td>
                                                <?php if ($record['photo_path']): ?>
                                                    <img src="<?php echo $record['photo_path']; ?>" alt="<?php echo $record['name']; ?>" width="50" class="rounded">
                                                <?php else: ?>
                                                    <span class="text-muted">No photo</span>
                                                <?php endif; ?>
                                            </td>
                                        </tr>
                                    <?php endforeach; ?>
                                </tbody>
                            </table>
                        </div>
                    <?php else: ?>
                        <p>No attendance records for today.</p>
                    <?php endif; ?>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function selectStudent(id) {
    document.getElementById('student_id').value = id;
}
</script>

<?php include 'footer.php'; ?>
