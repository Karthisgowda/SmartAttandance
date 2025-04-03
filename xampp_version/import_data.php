<?php
// Include database connection
include 'db_connection.php';

$message = "";
$messageType = "";

// Handle form submission
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    if (isset($_FILES["csv_file"]) && $_FILES["csv_file"]["error"] == 0) {
        $target_file = $_FILES["csv_file"]["tmp_name"];
        $fileType = strtolower(pathinfo($_FILES["csv_file"]["name"], PATHINFO_EXTENSION));
        
        // Check if file is a CSV
        if ($fileType != "csv") {
            $message = "Sorry, only CSV files are allowed.";
            $messageType = "danger";
        } else {
            // Read CSV file
            if (($handle = fopen($target_file, "r")) !== FALSE) {
                $header = fgetcsv($handle, 1000, ",");
                
                // Check if CSV structure is valid (for attendance records)
                if (count($header) >= 3 && $header[0] == "Id" && $header[1] == "Name") {
                    $importCount = 0;
                    $skipCount = 0;
                    
                    while (($data = fgetcsv($handle, 1000, ",")) !== FALSE) {
                        if (count($data) >= 3) {
                            $studentId = trim($data[0]);
                            $name = trim($data[1]);
                            
                            // Skip empty rows
                            if (empty($studentId) || empty($name)) {
                                $skipCount++;
                                continue;
                            }
                            
                            // Check if student exists
                            $checkSql = "SELECT * FROM students WHERE student_id = ?";
                            $checkStmt = $conn->prepare($checkSql);
                            $checkStmt->bind_param("s", $studentId);
                            $checkStmt->execute();
                            $checkResult = $checkStmt->get_result();
                            
                            if ($checkResult->num_rows == 0) {
                                // Insert new student
                                $insertSql = "INSERT INTO students (student_id, name) VALUES (?, ?)";
                                $insertStmt = $conn->prepare($insertSql);
                                $insertStmt->bind_param("ss", $studentId, $name);
                                $insertStmt->execute();
                                $insertStmt->close();
                            }
                            $checkStmt->close();
                            
                            // Process attendance if available
                            if (isset($header[2]) && $header[2] == "Date" && isset($header[3]) && $header[3] == "Time" && 
                                isset($data[2]) && isset($data[3])) {
                                
                                $date = trim($data[2]);
                                $time = trim($data[3]);
                                
                                // Skip if date or time is missing
                                if (empty($date) || empty($time)) {
                                    continue;
                                }
                                
                                // Check if attendance already exists
                                $attCheckSql = "SELECT * FROM attendance WHERE student_id = ? AND date = ?";
                                $attCheckStmt = $conn->prepare($attCheckSql);
                                $attCheckStmt->bind_param("ss", $studentId, $date);
                                $attCheckStmt->execute();
                                $attCheckResult = $attCheckStmt->get_result();
                                
                                if ($attCheckResult->num_rows == 0) {
                                    // Insert attendance record
                                    $attInsertSql = "INSERT INTO attendance (student_id, date, time) VALUES (?, ?, ?)";
                                    $attInsertStmt = $conn->prepare($attInsertSql);
                                    $attInsertStmt->bind_param("sss", $studentId, $date, $time);
                                    $attInsertStmt->execute();
                                    $attInsertStmt->close();
                                }
                                $attCheckStmt->close();
                            }
                            
                            $importCount++;
                        } else {
                            $skipCount++;
                        }
                    }
                    
                    fclose($handle);
                    $message = "Import completed successfully! Processed $importCount records, skipped $skipCount invalid records.";
                    $messageType = "success";
                } else {
                    $message = "CSV format is not valid. Please ensure it has columns: Id, Name, Date, Time.";
                    $messageType = "danger";
                }
            } else {
                $message = "Failed to open the file.";
                $messageType = "danger";
            }
        }
    } else {
        $message = "Please select a file to upload.";
        $messageType = "danger";
    }
}

// Close connection
$conn->close();

include 'header.php';
?>

<div class="card">
    <h2>Import Data</h2>
    
    <?php if (!empty($message)): ?>
        <div class="alert alert-<?php echo $messageType; ?>">
            <?php echo $message; ?>
        </div>
    <?php endif; ?>
    
    <div class="card">
        <h3>Import Students and Attendance</h3>
        <p>Upload a CSV file to import student information and attendance records from the Streamlit version.</p>
        
        <form action="import_data.php" method="post" enctype="multipart/form-data">
            <div class="form-group">
                <label for="csv_file">Select CSV File</label>
                <input type="file" id="csv_file" name="csv_file" class="form-control" accept=".csv" required>
            </div>
            
            <button type="submit" class="btn">Import Data</button>
        </form>
        
        <div class="card" style="margin-top: 20px;">
            <h4>CSV Format Requirements</h4>
            <p>The CSV file should have the following columns:</p>
            <ul>
                <li><strong>Id</strong> - Student ID</li>
                <li><strong>Name</strong> - Student Name</li>
                <li><strong>Date</strong> - Attendance Date (YYYY-MM-DD format)</li>
                <li><strong>Time</strong> - Attendance Time (HH:MM:SS format)</li>
            </ul>
            <p>This format matches the export from the Streamlit version of the app.</p>
        </div>
    </div>
    
    <div class="card">
        <h3>Import Student Photos</h3>
        <p>After importing student data, copy the student photos from the Streamlit app's <code>data/student_images</code> folder to the <code>uploads</code> folder in this installation.</p>
    </div>
</div>

<?php include 'footer.php'; ?>
