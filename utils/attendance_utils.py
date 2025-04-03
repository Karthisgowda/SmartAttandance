import os
import pandas as pd
import datetime
import glob

# Define constants
ATTENDANCE_DIR = "data/attendance"

def get_attendance_file(date=None):
    """
    Get the attendance file path for the given date
    
    Args:
        date (datetime.date, optional): Date for the attendance file. Defaults to today.
        
    Returns:
        str: Path to the attendance file
    """
    if date is None:
        date = datetime.date.today()
    
    # Format date for filename
    date_str = date.strftime("%Y-%m-%d")
    
    # Create directory if it doesn't exist
    os.makedirs(ATTENDANCE_DIR, exist_ok=True)
    
    # Return file path
    return os.path.join(ATTENDANCE_DIR, f"attendance_{date_str}.csv")

def mark_attendance(name):
    """
    Mark attendance for the given name
    
    Args:
        name (str): Name of the person
    """
    # Get attendance file path for today
    file_path = get_attendance_file()
    
    # Check if file exists
    if os.path.exists(file_path):
        # Load existing attendance data
        df = pd.read_csv(file_path)
        
        # Check if person already marked for today
        if name not in df['Name'].values:
            # Add new entry
            time_now = datetime.datetime.now().strftime("%H:%M:%S")
            date_today = datetime.date.today().strftime("%Y-%m-%d")
            new_row = {'Name': name, 'Time': time_now, 'Date': date_today}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            
            # Save updated attendance
            df.to_csv(file_path, index=False)
    else:
        # Create new attendance file
        time_now = datetime.datetime.now().strftime("%H:%M:%S")
        date_today = datetime.date.today().strftime("%Y-%m-%d")
        df = pd.DataFrame({'Name': [name], 'Time': [time_now], 'Date': [date_today]})
        
        # Save new attendance file
        df.to_csv(file_path, index=False)

def load_attendance_history():
    """
    Load all attendance records
    
    Returns:
        pandas.DataFrame: DataFrame containing all attendance records
    """
    # Get all attendance files
    attendance_files = glob.glob(os.path.join(ATTENDANCE_DIR, "attendance_*.csv"))
    
    # If no files found, return empty DataFrame
    if not attendance_files:
        return pd.DataFrame()
    
    # Initialize empty list to store DataFrames
    dfs = []
    
    # Load each file and append to list
    for file_path in attendance_files:
        try:
            df = pd.read_csv(file_path)
            dfs.append(df)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    # Concatenate all DataFrames
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    else:
        return pd.DataFrame()
