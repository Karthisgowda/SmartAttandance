<?php
include 'header.php';
include 'db_connection.php';

$message = '';

if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_FILES["csv_file"])) {
    // Handle file upload
    $csv_file = $_FILES["csv_file"]["tmp_name"];
    
    if (($handle = fopen($csv_file, "r")) !== FALSE) {
        // Skip header row
        fgetcsv($handle, 1000, ",");
        
        $imported_count = 0;
        
        while (($data = fgetcsv($handle, 1000, ",")) !== FALSE) {
            if (count($data) >= 3) {
                $date = $data[0];
                $name = $data[1];
                $time = $data[2];
                
                // Check if student exists
                $check_student_sql = "SELECT id FROM students WHERE name = '$name'";
                $check_result = $conn->query($check_student_sql);
                
                $student_id = 0;
                
                if ($check_result->num_rows > 0) {
                    $student_row = $check_result->fetch_assoc();
                    $student_id = $student_row['id'];
                } else {
                    // Create student if not exists
                    $insert_student_sql = "INSERT INTO students (name, photo_path) VALUES ('$name', '')";
                    if ($conn->query($insert_student_sql) === TRUE) {
                        $student_id = $conn->insert_id;
                    }
                }
                
                if ($student_id > 0) {
                    // Insert attendance record
                    $insert_sql = "INSERT INTO attendance (student_id, date, time) 
                                   VALUES ('$student_id', '$date', '$time')
                                   ON DUPLICATE KEY UPDATE time = time";
                    
                    if ($conn->query($insert_sql) === TRUE) {
                        $imported_count++;
                    }
                }
            }
        }
        
        fclose($handle);
        $message = "Successfully imported $imported_count attendance records.";
    } else {
        $message = "Error opening file.";
    }
}
?>

<div class="container mt-5">
    <div class="card bg-dark text-light">
        <div class="card-header">
            <h2>Import Data</h2>
        </div>
        <div class="card-body">
            <p>Use this tool to import attendance data from a CSV file exported from the Streamlit version.</p>
            
            <?php if($message): ?>
                <div class="alert alert-info"><?php echo $message; ?></div>
            <?php endif; ?>
            
            <form method="post" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="csv_file">Select CSV File</label>
                    <input type="file" class="form-control-file" id="csv_file" name="csv_file" accept=".csv" required>
                </div>
                <p class="text-warning">Note: The CSV file should have the format: Date, Name, Time</p>
                <button type="submit" class="btn btn-primary">Import Data</button>
            </form>
            
            <hr class="bg-light my-4">
            
            <h3>Photo Migration</h3>
            <p>To migrate student photos:</p>
            <ol>
                <li>Copy the student photos from your Streamlit app's faces folder</li>
                <li>Place them in the uploads folder of this XAMPP application</li>
                <li>Update the photo paths in the database manually</li>
            </ol>
        </div>
    </div>
</div>

<?php include 'footer.php'; ?>
