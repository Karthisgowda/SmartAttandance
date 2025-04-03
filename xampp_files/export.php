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
