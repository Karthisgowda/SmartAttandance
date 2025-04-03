<?php
// Include database connection
include 'db_connection.php';

$message = "";
$messageType = "";

// Handle form submission
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $student_id = $_POST["student_id"];
    $name = $_POST["name"];
    
    // Check if student ID already exists
    $checkSql = "SELECT * FROM students WHERE student_id = ?";
    $checkStmt = $conn->prepare($checkSql);
    $checkStmt->bind_param("s", $student_id);
    $checkStmt->execute();
    $checkResult = $checkStmt->get_result();
    
    if ($checkResult->num_rows > 0) {
        $message = "Student ID already exists. Please use a different ID.";
        $messageType = "danger";
    } else {
        // Handle photo upload
        $photoPath = null;
        if (isset($_FILES["photo"]) && $_FILES["photo"]["error"] == 0) {
            $target_dir = "uploads/";
            if (!file_exists($target_dir)) {
                mkdir($target_dir, 0777, true);
            }
            
            $target_file = $target_dir . $student_id . "_" . basename($_FILES["photo"]["name"]);
            $imageFileType = strtolower(pathinfo($target_file, PATHINFO_EXTENSION));
            
            // Check if file is an actual image
            $check = getimagesize($_FILES["photo"]["tmp_name"]);
            if ($check !== false) {
                // Check file size (limit to 5MB)
                if ($_FILES["photo"]["size"] <= 5000000) {
                    // Allow only certain file formats
                    if ($imageFileType == "jpg" || $imageFileType == "png" || $imageFileType == "jpeg") {
                        if (move_uploaded_file($_FILES["photo"]["tmp_name"], $target_file)) {
                            $photoPath = $target_file;
                        } else {
                            $message = "Sorry, there was an error uploading your file.";
                            $messageType = "danger";
                        }
                    } else {
                        $message = "Sorry, only JPG, JPEG & PNG files are allowed.";
                        $messageType = "danger";
                    }
                } else {
                    $message = "Sorry, your file is too large. Maximum 5MB allowed.";
                    $messageType = "danger";
                }
            } else {
                $message = "File is not an image.";
                $messageType = "danger";
            }
        }
        
        // If no error message set, proceed with registration
        if (empty($message)) {
            // Insert student into database
            $sql = "INSERT INTO students (student_id, name, photo_path) VALUES (?, ?, ?)";
            $stmt = $conn->prepare($sql);
            $stmt->bind_param("sss", $student_id, $name, $photoPath);
            
            if ($stmt->execute()) {
                $message = "Student registered successfully!";
                $messageType = "success";
            } else {
                $message = "Error: " . $stmt->error;
                $messageType = "danger";
            }
            
            $stmt->close();
        }
    }
    
    $checkStmt->close();
}

// Close connection
$conn->close();

include 'header.php';
?>

<div class="card">
    <h2>Register New Student</h2>
    
    <?php if (!empty($message)): ?>
        <div class="alert alert-<?php echo $messageType; ?>">
            <?php echo $message; ?>
        </div>
    <?php endif; ?>
    
    <form action="register.php" method="post" enctype="multipart/form-data">
        <div class="form-group">
            <label for="student_id">Student ID</label>
            <input type="text" id="student_id" name="student_id" class="form-control" required>
        </div>
        
        <div class="form-group">
            <label for="name">Student Name</label>
            <input type="text" id="name" name="name" class="form-control" required>
        </div>
        
        <div class="form-group">
            <label for="photo">Student Photo</label>
            <input type="file" id="photo" name="photo" class="form-control" accept="image/*">
            <div id="image-preview" class="image-preview">
                <p>Preview will appear here</p>
            </div>
        </div>
        
        <button type="submit" class="btn">Register Student</button>
    </form>
</div>

<?php include 'footer.php'; ?>
