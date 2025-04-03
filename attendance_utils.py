import pandas as pd
import os
from datetime import datetime

def initialize_attendance_file():
    """
    Initialize the attendance CSV file if it doesn't exist
    """
    attendance_file = 'data/attendance_records.csv'
    
    if not os.path.exists(attendance_file):
        # Create an empty DataFrame with required columns
        df = pd.DataFrame(columns=['User_ID', 'Date', 'Time'])
        
        # Save the DataFrame to CSV
        df.to_csv(attendance_file, index=False)
        print(f"Initialized attendance file: {attendance_file}")

def mark_attendance(user_id):
    """
    Mark attendance for a user
    
    Args:
        user_id: ID of the user to mark attendance for
    """
    attendance_file = 'data/attendance_records.csv'
    
    # Get current date and time
    now = datetime.now()
    date = now.strftime('%Y-%m-%d')
    time = now.strftime('%H:%M:%S')
    
    # Load existing attendance records
    df = pd.read_csv(attendance_file)
    
    # Check if the user already has attendance for today
    today_records = df[(df['User_ID'] == user_id) & (df['Date'] == date)]
    
    if today_records.empty:
        # Add new attendance record
        new_record = pd.DataFrame({
            'User_ID': [user_id],
            'Date': [date],
            'Time': [time]
        })
        
        # Append to the CSV file
        df = pd.concat([df, new_record], ignore_index=True)
        df.to_csv(attendance_file, index=False)
        print(f"Marked attendance for {user_id} at {time} on {date}")

def get_attendance_records():
    """
    Get all attendance records
    
    Returns:
        DataFrame containing all attendance records
    """
    attendance_file = 'data/attendance_records.csv'
    
    if os.path.exists(attendance_file):
        return pd.read_csv(attendance_file)
    else:
        return pd.DataFrame(columns=['User_ID', 'Date', 'Time'])

def get_registered_users():
    """
    Get list of all registered users
    
    Returns:
        List of registered user IDs
    """
    users_dir = 'data/registered_users'
    
    if not os.path.exists(users_dir):
        os.makedirs(users_dir, exist_ok=True)
        return []
    
    # Get all directories in the registered_users folder
    users = [d for d in os.listdir(users_dir) 
             if os.path.isdir(os.path.join(users_dir, d)) and not d.startswith('.')]
    
    return users
