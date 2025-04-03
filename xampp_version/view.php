<?php
// Include database connection
include 'db_connection.php';

// Get selected date (default to today)
$selectedDate = isset($_GET['date']) ? $_GET['date'] : date('Y-m-d');

// Get attendance for selected date
$dateSql = "SELECT a.time, s.name, s.student_id 
            FROM attendance a 
            JOIN students s ON a.student_id = s.student_id 
            WHERE a.date = ? 
            ORDER BY a.time";
$dateStmt = $conn->prepare($dateSql);
$dateStmt->bind_param("s", $selectedDate);
$dateStmt->execute();
$dateResult = $dateStmt->get_result();
$dateAttendance = [];
if ($dateResult && $dateResult->num_rows > 0) {
    while($row = $dateResult->fetch_assoc()) {
        $dateAttendance[] = $row;
    }
}
$dateStmt->close();

// Get all students
$studentsSql = "SELECT student_id, name FROM students ORDER BY name";
$studentsResult = $conn->query($studentsSql);
$allStudents = [];
if ($studentsResult && $studentsResult->num_rows > 0) {
    while($row = $studentsResult->fetch_assoc()) {
        $allStudents[$row['student_id']] = $row['name'];
    }
}

// Get unique dates for which attendance exists
$datesSql = "SELECT DISTINCT date FROM attendance ORDER BY date DESC";
$datesResult = $conn->query($datesSql);
$attendanceDates = [];
if ($datesResult && $datesResult->num_rows > 0) {
    while($row = $datesResult->fetch_assoc()) {
        $attendanceDates[] = $row['date'];
    }
}

// Close connection
$conn->close();

include 'header.php';
?>

<div class="card">
    <h2>View Attendance Records</h2>
    
    <!-- Date Selector -->
    <div class="form-group">
        <label for="date-picker">Select Date</label>
        <form action="view.php" method="get">
            <div style="display: flex; gap: 10px; align-items: center;">
                <input type="date" id="date-picker" name="date" value="<?php echo $selectedDate; ?>" class="form-control" style="max-width: 200px;">
                <button type="submit" class="btn">View</button>
            </div>
        </form>
    </div>
    
    <!-- Attendance for Selected Date -->
    <div class="card">
        <h3>Attendance for <?php echo date("F d, Y", strtotime($selectedDate)); ?></h3>
        
        <?php if (count($dateAttendance) > 0): ?>
            <div class="table-container">
                <table id="attendance-table" class="data-table">
                    <thead>
                        <tr>
                            <th>Student ID</th>
                            <th>Name</th>
                            <th>Time</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($dateAttendance as $record): ?>
                            <tr>
                                <td><?php echo $record['student_id']; ?></td>
                                <td><?php echo $record['name']; ?></td>
                                <td><?php echo date("h:i A", strtotime($record['time'])); ?></td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>
            
            <div style="margin-top: 15px;">
                <button id="print-button" class="btn">Print</button>
                <button onclick="exportTableToCSV('attendance-table', 'attendance_<?php echo $selectedDate; ?>.csv')" class="btn">Export to CSV</button>
            </div>
        <?php else: ?>
            <p>No attendance records found for this date.</p>
        <?php endif; ?>
    </div>
    
    <!-- Overall Attendance Summary -->
    <?php if (count($attendanceDates) > 0 && count($allStudents) > 0): ?>
        <div class="card">
            <h3>Overall Attendance Summary</h3>
            <p>Select a date from the list below to view attendance for that day.</p>
            
            <div class="form-group">
                <label for="date-select">Quick Date Select</label>
                <select id="date-select" class="form-control" onchange="window.location.href='view.php?date='+this.value">
                    <?php foreach ($attendanceDates as $date): ?>
                        <option value="<?php echo $date; ?>" <?php if ($date == $selectedDate) echo "selected"; ?>>
                            <?php echo date("F d, Y", strtotime($date)); ?>
                        </option>
                    <?php endforeach; ?>
                </select>
            </div>
        </div>
    <?php endif; ?>
</div>

<?php include 'footer.php'; ?>
