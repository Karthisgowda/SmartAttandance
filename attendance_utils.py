import os
import pandas as pd
from datetime import datetime

def create_attendance_file_if_not_exists(filename):
    """
    Create an attendance CSV file if it doesn't exist.
    
    Args:
        filename: Path to the attendance file
    """
    if not os.path.exists(filename):
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Create an empty CSV file with headers
        df = pd.DataFrame(columns=["Name", "Time"])
        df.to_csv(filename, index=False)

def mark_attendance(name, attendance_file):
    """
    Mark attendance for a person.
    
    Args:
        name: Name of the person
        attendance_file: Path to the attendance file
    """
    # Ensure the attendance file exists
    create_attendance_file_if_not_exists(attendance_file)
    
    # Get current timestamp
    now = datetime.now()
    timestamp = now.strftime("%H:%M:%S")
    
    # Load the attendance file
    attendance_df = pd.read_csv(attendance_file)
    
    # Check if the person is already marked present
    if name in attendance_df["Name"].values:
        # Update the time if the person is already marked
        attendance_df.loc[attendance_df["Name"] == name, "Time"] = timestamp
    else:
        # Add a new entry for the person
        new_row = pd.DataFrame({"Name": [name], "Time": [timestamp]})
        attendance_df = pd.concat([attendance_df, new_row], ignore_index=True)
    
    # Save the updated attendance
    attendance_df.to_csv(attendance_file, index=False)

def get_attendance_log(attendance_file):
    """
    Get the attendance log from a file.
    
    Args:
        attendance_file: Path to the attendance file
        
    Returns:
        DataFrame: Attendance data
    """
    if os.path.exists(attendance_file):
        try:
            return pd.read_csv(attendance_file)
        except Exception as e:
            print(f"Error reading attendance file: {e}")
            return pd.DataFrame(columns=["Name", "Time"])
    else:
        return pd.DataFrame(columns=["Name", "Time"])
