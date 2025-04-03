<?php include 'header.php'; ?>

<div class="card">
    <h2>Welcome to Face Recognition Attendance System</h2>
    <p>This system helps you track student attendance easily and efficiently.</p>
    
    <div class="row">
        <div class="col-half">
            <div class="card">
                <h3>Getting Started</h3>
                <ol>
                    <li>Register students using the "Register Student" page</li>
                    <li>Mark attendance daily using the "Mark Attendance" page</li>
                    <li>View and analyze attendance records in "View Records"</li>
                    <li>Export data for further analysis in "Export Data"</li>
                </ol>
                <a href="register.php" class="btn">Register New Student</a>
            </div>
        </div>
        
        <div class="col-half">
            <div class="card">
                <h3>Recent Activity</h3>
                <?php
                // Include database connection
                include 'db_connection.php';
                
                // Get recent attendance (last 5 records)
                $sql = "SELECT a.date, a.time, s.name, s.student_id 
                        FROM attendance a 
                        JOIN students s ON a.student_id = s.student_id 
                        ORDER BY a.date DESC, a.time DESC LIMIT 5";
                $result = $conn->query($sql);
                
                if ($result && $result->num_rows > 0) {
                    echo "<ul>";
                    while($row = $result->fetch_assoc()) {
                        echo "<li>" . $row["name"] . " (ID: " . $row["student_id"] . ") - " . 
                             date("M d, Y", strtotime($row["date"])) . " at " . 
                             date("h:i A", strtotime($row["time"])) . "</li>";
                    }
                    echo "</ul>";
                } else {
                    echo "<p>No recent attendance records.</p>";
                }
                
                // Get total students count
                $sql = "SELECT COUNT(*) as total FROM students";
                $result = $conn->query($sql);
                $studentCount = 0;
                if ($result && $result->num_rows > 0) {
                    $studentCount = $result->fetch_assoc()["total"];
                }
                
                // Close connection
                $conn->close();
                ?>
                
                <p>Total Students Registered: <strong><?php echo $studentCount; ?></strong></p>
                <a href="view.php" class="btn">View All Records</a>
            </div>
        </div>
    </div>
</div>

<?php include 'footer.php'; ?>
