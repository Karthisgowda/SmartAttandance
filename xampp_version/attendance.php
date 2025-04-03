<?php
// Include database connection
include 'db_connection.php';

$message = "";
$messageType = "";

// Handle form submission
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $student_id = $_POST["student_id"];
    $date = date("Y-m-d"); // Today's date
    $time = date("H:i:s"); // Current time
    
    // Check if student exists
    $checkSql = "SELECT * FROM students WHERE student_id = ?";
    $checkStmt = $conn->prepare($checkSql);
    $checkStmt->bind_param("s", $student_id);
    $checkStmt->execute();
    $checkResult = $checkStmt->get_result();
    
    if ($checkResult->num_rows == 0) {
        $message = "Student ID does not exist.";
        $messageType = "danger";
    } else {
        $studentData = $checkResult->fetch_assoc();
        
        // Check if attendance already marked for today
        $attendanceSql = "SELECT * FROM attendance WHERE student_id = ? AND date = ?";
        $attendanceStmt = $conn->prepare($attendanceSql);
        $attendanceStmt->bind_param("ss", $student_id, $date);
        $attendanceStmt->execute();
        $attendanceResult = $attendanceStmt->get_result();
        
        if ($attendanceResult->num_rows > 0) {
            $message = "Attendance already marked for " . $studentData["name"] . " today.";
            $messageType = "info";
        } else {
            // Mark attendance
            $markSql = "INSERT INTO attendance (student_id, date, time) VALUES (?, ?, ?)";
            $markStmt = $conn->prepare($markSql);
            $markStmt->bind_param("sss", $student_id, $date, $time);
            
            if ($markStmt->execute()) {
                $message = "Attendance marked successfully for " . $studentData["name"] . "!";
                $messageType = "success";
            } else {
                $message = "Error marking attendance: " . $markStmt->error;
                $messageType = "danger";
            }
            
            $markStmt->close();
        }
        
        $attendanceStmt->close();
    }
    
    $checkStmt->close();
}

// Get all students for dropdown
$sql = "SELECT student_id, name FROM students ORDER BY name";
$result = $conn->query($sql);
$students = [];
if ($result && $result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
        $students[] = $row;
    }
}

// Get today's attendance
$today = date("Y-m-d");
$todaySql = "SELECT a.time, s.name, s.student_id 
             FROM attendance a 
             JOIN students s ON a.student_id = s.student_id 
             WHERE a.date = ? 
             ORDER BY a.time";
$todayStmt = $conn->prepare($todaySql);
$todayStmt->bind_param("s", $today);
$todayStmt->execute();
$todayResult = $todayStmt->get_result();
$todayAttendance = [];
if ($todayResult && $todayResult->num_rows > 0) {
    while($row = $todayResult->fetch_assoc()) {
        $todayAttendance[] = $row;
    }
}
$todayStmt->close();

// Close connection
$conn->close();

include 'header.php';
?>

<div class="card">
    <h2>Mark Attendance</h2>
    
    <?php if (!empty($message)): ?>
        <div class="alert alert-<?php echo $messageType; ?>">
            <?php echo $message; ?>
        </div>
    <?php endif; ?>
    
    <div class="row">
        <div class="col-half">
            <div class="card">
                <h3>Select Student</h3>
                
                <?php if (count($students) > 0): ?>
                    <form action="attendance.php" method="post">
                        <div class="form-group">
                            <label for="student_id">Student</label>
                            <select id="student_id" name="student_id" class="form-control" required>
                                <option value="">-- Select Student --</option>
                                <?php foreach ($students as $student): ?>
                                    <option value="<?php echo $student['student_id']; ?>">
                                        <?php echo $student['name'] . ' (' . $student['student_id'] . ')'; ?>
                                    </option>
                                <?php endforeach; ?>
                            </select>
                        </div>
                        
                        <button type="submit" class="btn">Mark Present</button>
                    </form>
                <?php else: ?>
                    <p>No students registered yet. Please register students first.</p>
                    <a href="register.php" class="btn">Register Student</a>
                <?php endif; ?>
            </div>
        </div>
        
        <div class="col-half">
            <div class="card">
                <h3>Today's Attendance</h3>
                
                <?php if (count($todayAttendance) > 0): ?>
                    <ul>
                        <?php foreach ($todayAttendance as $record): ?>
                            <li>
                                <strong><?php echo $record['name']; ?></strong> (ID: <?php echo $record['student_id']; ?>) - 
                                <?php echo date("h:i A", strtotime($record['time'])); ?>
                            </li>
                        <?php endforeach; ?>
                    </ul>
                <?php else: ?>
                    <p>No attendance marked yet for today.</p>
                <?php endif; ?>
            </div>
        </div>
    </div>
</div>

<?php include 'footer.php'; ?>
