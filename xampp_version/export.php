<?php
// Include database connection
include 'db_connection.php';

// Get start and end dates (default to current month)
$startDate = isset($_GET['start_date']) ? $_GET['start_date'] : date('Y-m-01');
$endDate = isset($_GET['end_date']) ? $_GET['end_date'] : date('Y-m-t');

// Function to generate attendance report
function generateAttendanceReport($conn, $startDate, $endDate) {
    // Get all students
    $studentsSql = "SELECT student_id, name FROM students ORDER BY name";
    $studentsResult = $conn->query($studentsSql);
    $students = [];
    if ($studentsResult && $studentsResult->num_rows > 0) {
        while($row = $studentsResult->fetch_assoc()) {
            $students[$row['student_id']] = $row['name'];
        }
    }
    
    // Get all dates in the range
    $dates = [];
    $current = strtotime($startDate);
    $end = strtotime($endDate);
    while($current <= $end) {
        $dates[] = date('Y-m-d', $current);
        $current = strtotime('+1 day', $current);
    }
    
    // Get attendance data
    $attendanceSql = "SELECT student_id, date FROM attendance WHERE date BETWEEN ? AND ? ORDER BY date";
    $attendanceStmt = $conn->prepare($attendanceSql);
    $attendanceStmt->bind_param("ss", $startDate, $endDate);
    $attendanceStmt->execute();
    $attendanceResult = $attendanceStmt->get_result();
    
    $attendanceMap = [];
    if ($attendanceResult && $attendanceResult->num_rows > 0) {
        while($row = $attendanceResult->fetch_assoc()) {
            $attendanceMap[$row['student_id'] . '_' . $row['date']] = true;
        }
    }
    $attendanceStmt->close();
    
    // Generate report data
    $reportData = [];
    foreach ($students as $studentId => $name) {
        $row = [
            'student_id' => $studentId,
            'name' => $name
        ];
        
        $presentCount = 0;
        foreach ($dates as $date) {
            $key = $studentId . '_' . $date;
            $status = isset($attendanceMap[$key]) ? 'Present' : 'Absent';
            $row[date('Y-m-d', strtotime($date))] = $status;
            
            if ($status === 'Present') {
                $presentCount++;
            }
        }
        
        // Calculate attendance percentage
        $totalDays = count($dates);
        $percentage = ($totalDays > 0) ? round(($presentCount / $totalDays) * 100, 2) : 0;
        $row['attendance_percentage'] = $percentage;
        
        $reportData[] = $row;
    }
    
    return [
        'students' => $students,
        'dates' => $dates,
        'report' => $reportData
    ];
}

// Get report data
$report = generateAttendanceReport($conn, $startDate, $endDate);

// Close connection
$conn->close();

include 'header.php';
?>

<div class="card">
    <h2>Export Attendance Data</h2>
    
    <!-- Date Range Selector -->
    <div class="card">
        <h3>Select Date Range</h3>
        <form action="export.php" method="get">
            <div class="row">
                <div class="col-half">
                    <div class="form-group">
                        <label for="start_date">Start Date</label>
                        <input type="date" id="start_date" name="start_date" value="<?php echo $startDate; ?>" class="form-control">
                    </div>
                </div>
                <div class="col-half">
                    <div class="form-group">
                        <label for="end_date">End Date</label>
                        <input type="date" id="end_date" name="end_date" value="<?php echo $endDate; ?>" class="form-control">
                    </div>
                </div>
            </div>
            <button type="submit" class="btn">Generate Report</button>
        </form>
    </div>
    
    <!-- Report Table -->
    <div class="card">
        <h3>Attendance Report: <?php echo date("M d, Y", strtotime($startDate)); ?> to <?php echo date("M d, Y", strtotime($endDate)); ?></h3>
        
        <?php if (count($report['students']) > 0): ?>
            <div class="table-container">
                <table id="report-table" class="data-table">
                    <thead>
                        <tr>
                            <th>Student ID</th>
                            <th>Name</th>
                            <?php foreach ($report['dates'] as $date): ?>
                                <th><?php echo date("M d", strtotime($date)); ?></th>
                            <?php endforeach; ?>
                            <th>Attendance %</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($report['report'] as $row): ?>
                            <tr>
                                <td><?php echo $row['student_id']; ?></td>
                                <td><?php echo $row['name']; ?></td>
                                
                                <?php foreach ($report['dates'] as $date): ?>
                                    <td>
                                        <?php 
                                        $status = $row[date('Y-m-d', strtotime($date))];
                                        if ($status === 'Present') {
                                            echo "✓";
                                        } else {
                                            echo "✗";
                                        }
                                        ?>
                                    </td>
                                <?php endforeach; ?>
                                
                                <td><?php echo $row['attendance_percentage']; ?>%</td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>
            
            <div style="margin-top: 15px;">
                <button id="print-button" class="btn">Print Report</button>
                <button onclick="exportTableToCSV('report-table', 'attendance_report_<?php echo $startDate; ?>_to_<?php echo $endDate; ?>.csv')" class="btn">Export to CSV</button>
            </div>
        <?php else: ?>
            <p>No students registered in the system.</p>
        <?php endif; ?>
    </div>
</div>

<?php include 'footer.php'; ?>
