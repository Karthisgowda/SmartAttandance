<?php
include 'header.php';
include 'db_connection.php';

// Get selected date or default to today
$selected_date = isset($_GET['date']) ? $_GET['date'] : date('Y-m-d');
$student_filter = isset($_GET['student']) ? $_GET['student'] : '';

// Get unique dates for dropdown
$dates = array();
$dates_sql = "SELECT DISTINCT date FROM attendance ORDER BY date DESC";
$dates_result = $conn->query($dates_sql);

if ($dates_result->num_rows > 0) {
    while($row = $dates_result->fetch_assoc()) {
        $dates[] = $row['date'];
    }
}

// Get all students for filter dropdown
$students = array();
$students_sql = "SELECT * FROM students ORDER BY name";
$students_result = $conn->query($students_sql);

if ($students_result->num_rows > 0) {
    while($row = $students_result->fetch_assoc()) {
        $students[] = $row;
    }
}

// Get attendance records for selected date
$attendance = array();
$sql = "SELECT a.*, s.name, s.photo_path 
       FROM attendance a 
       JOIN students s ON a.student_id = s.id 
       WHERE 1=1";

if ($selected_date) {
    $sql .= " AND a.date = '$selected_date'";
}

if ($student_filter) {
    $sql .= " AND a.student_id = '$student_filter'";
}

$sql .= " ORDER BY a.time";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
        $attendance[] = $row;
    }
}

// Get attendance statistics
$stats = array();

// Total records
$stats_sql = "SELECT COUNT(*) as total FROM attendance";
$stats_result = $conn->query($stats_sql);
if ($stats_result->num_rows > 0) {
    $row = $stats_result->fetch_assoc();
    $stats['total'] = $row['total'];
}

// Total students
$stats_sql = "SELECT COUNT(*) as total FROM students";
$stats_result = $conn->query($stats_sql);
if ($stats_result->num_rows > 0) {
    $row = $stats_result->fetch_assoc();
    $stats['students'] = $row['total'];
}

// Today's attendance
$today = date('Y-m-d');
$stats_sql = "SELECT COUNT(*) as total FROM attendance WHERE date = '$today'";
$stats_result = $conn->query($stats_sql);
if ($stats_result->num_rows > 0) {
    $row = $stats_result->fetch_assoc();
    $stats['today'] = $row['total'];
}
?>

<div class="container mt-5">
    <div class="row">
        <div class="col-md-12">
            <div class="card bg-dark text-light">
                <div class="card-header">
                    <h2>Attendance Records</h2>
                </div>
                <div class="card-body">
                    <div class="row mb-4">
                        <div class="col-md-4">
                            <div class="card bg-info text-white">
                                <div class="card-body">
                                    <h5 class="card-title">Total Attendance Records</h5>
                                    <p class="card-text display-4"><?php echo isset($stats['total']) ? $stats['total'] : 0; ?></p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card bg-success text-white">
                                <div class="card-body">
                                    <h5 class="card-title">Registered Students</h5>
                                    <p class="card-text display-4"><?php echo isset($stats['students']) ? $stats['students'] : 0; ?></p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card bg-primary text-white">
                                <div class="card-body">
                                    <h5 class="card-title">Today's Attendance</h5>
                                    <p class="card-text display-4"><?php echo isset($stats['today']) ? $stats['today'] : 0; ?></p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <form method="get" class="mb-4">
                        <div class="row">
                            <div class="col-md-5">
                                <div class="form-group">
                                    <label for="date">Select Date</label>
                                    <select class="form-control" id="date" name="date">
                                        <option value="">All Dates</option>
                                        <?php foreach ($dates as $date): ?>
                                            <option value="<?php echo $date; ?>" <?php echo ($date == $selected_date) ? 'selected' : ''; ?>>
                                                <?php echo date('Y-m-d (l)', strtotime($date)); ?>
                                            </option>
                                        <?php endforeach; ?>
                                    </select>
                                </div>
                            </div>
                            <div class="col-md-5">
                                <div class="form-group">
                                    <label for="student">Filter by Student</label>
                                    <select class="form-control" id="student" name="student">
                                        <option value="">All Students</option>
                                        <?php foreach ($students as $student): ?>
                                            <option value="<?php echo $student['id']; ?>" <?php echo ($student['id'] == $student_filter) ? 'selected' : ''; ?>>
                                                <?php echo $student['name']; ?>
                                            </option>
                                        <?php endforeach; ?>
                                    </select>
                                </div>
                            </div>
                            <div class="col-md-2 d-flex align-items-end">
                                <button type="submit" class="btn btn-primary w-100">Apply Filters</button>
                            </div>
                        </div>
                    </form>
                    
                    <div class="table-responsive">
                        <table class="table table-dark">
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Student</th>
                                    <th>Time</th>
                                    <th>Photo</th>
                                </tr>
                            </thead>
                            <tbody>
                                <?php if (count($attendance) > 0): ?>
                                    <?php foreach ($attendance as $record): ?>
                                        <tr>
                                            <td><?php echo date('Y-m-d (l)', strtotime($record['date'])); ?></td>
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
                                <?php else: ?>
                                    <tr>
                                        <td colspan="4" class="text-center">No attendance records found.</td>
                                    </tr>
                                <?php endif; ?>
                            </tbody>
                        </table>
                    </div>
                    
                    <div class="mt-3">
                        <a href="export.php" class="btn btn-success">Export to CSV</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
// Auto-submit form when dropdown changes
document.getElementById('date').addEventListener('change', function() {
    this.form.submit();
});

document.getElementById('student').addEventListener('change', function() {
    this.form.submit();
});
</script>

<?php include 'footer.php'; ?>
