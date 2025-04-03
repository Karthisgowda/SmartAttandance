<?php
include 'header.php';
include 'db_connection.php';

$message = '';
$messageType = '';

// Create uploads directory if it doesn't exist
if (!file_exists('uploads')) {
    mkdir('uploads', 0777, true);
}

if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['name'])) {
    $name = $_POST['name'];
    $photoPath = '';
    
    // Handle photo upload
    if (isset($_FILES['photo']) && $_FILES['photo']['error'] == 0) {
        $allowed = array('jpg', 'jpeg', 'png');
        $filename = $_FILES['photo']['name'];
        $ext = pathinfo($filename, PATHINFO_EXTENSION);
        
        if (in_array(strtolower($ext), $allowed)) {
            $newFileName = $name . '_' . time() . '.' . $ext;
            $target = 'uploads/' . $newFileName;
            
            if (move_uploaded_file($_FILES['photo']['tmp_name'], $target)) {
                $photoPath = $target;
                
                // Insert student to database
                $sql = "INSERT INTO students (name, photo_path) VALUES ('$name', '$photoPath')";
                
                if ($conn->query($sql) === TRUE) {
                    $message = "Student registered successfully!";
                    $messageType = "success";
                } else {
                    $message = "Error: " . $sql . "<br>" . $conn->error;
                    $messageType = "danger";
                }
            } else {
                $message = "Failed to upload photo.";
                $messageType = "danger";
            }
        } else {
            $message = "Invalid file format. Only JPG, JPEG, and PNG are allowed.";
            $messageType = "warning";
        }
    } else {
        // Insert student without photo
        $sql = "INSERT INTO students (name) VALUES ('$name')";
        
        if ($conn->query($sql) === TRUE) {
            $message = "Student registered without photo.";
            $messageType = "success";
        } else {
            $message = "Error: " . $sql . "<br>" . $conn->error;
            $messageType = "danger";
        }
    }
}

// Get list of registered students
$students = array();
$sql = "SELECT * FROM students ORDER BY name";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
        $students[] = $row;
    }
}
?>

<div class="container mt-5">
    <div class="row">
        <div class="col-md-6">
            <div class="card bg-dark text-light">
                <div class="card-header">
                    <h2>Register New Student</h2>
                </div>
                <div class="card-body">
                    <?php if ($message): ?>
                        <div class="alert alert-<?php echo $messageType; ?>"><?php echo $message; ?></div>
                    <?php endif; ?>
                    
                    <form method="post" enctype="multipart/form-data">
                        <div class="form-group">
                            <label for="name">Student Name</label>
                            <input type="text" class="form-control" id="name" name="name" required>
                        </div>
                        
                        <div class="form-group">
                            <label for="photo">Student Photo</label>
                            <input type="file" class="form-control-file" id="photo" name="photo">
                            <small class="text-muted">Upload a clear, front-facing photo</small>
                        </div>
                        
                        <div id="photo-preview-container" class="mt-3 d-none">
                            <img id="photo-preview" class="photo-preview" alt="Preview">
                        </div>
                        
                        <button type="submit" class="btn btn-primary mt-3">Register Student</button>
                    </form>
                </div>
            </div>
        </div>
        
        <div class="col-md-6">
            <div class="card bg-dark text-light">
                <div class="card-header">
                    <h2>Registered Students</h2>
                </div>
                <div class="card-body">
                    <?php if (count($students) > 0): ?>
                        <div class="table-responsive">
                            <table class="table table-dark">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Name</th>
                                        <th>Photo</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <?php foreach ($students as $student): ?>
                                        <tr>
                                            <td><?php echo $student['id']; ?></td>
                                            <td><?php echo $student['name']; ?></td>
                                            <td>
                                                <?php if ($student['photo_path']): ?>
                                                    <img src="<?php echo $student['photo_path']; ?>" alt="<?php echo $student['name']; ?>" width="50" class="rounded">
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
                        <p>No students registered yet.</p>
                    <?php endif; ?>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
// Preview uploaded image
document.getElementById('photo').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        const previewContainer = document.getElementById('photo-preview-container');
        const preview = document.getElementById('photo-preview');
        
        reader.onload = function(e) {
            preview.src = e.target.result;
            previewContainer.classList.remove('d-none');
        }
        
        reader.readAsDataURL(file);
    }
});
</script>

<?php include 'footer.php'; ?>
