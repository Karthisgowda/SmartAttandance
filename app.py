import streamlit as st
import pandas as pd
import os
import time
import datetime
from datetime import datetime
import base64
from PIL import Image
import io

# Set page config
st.set_page_config(
    page_title="Face Recognition Attendance System",
    page_icon="📊",
    layout="wide"
)

# Create necessary directories if they don't exist
os.makedirs("data/student_images", exist_ok=True)
os.makedirs("data/attendance", exist_ok=True)

# Initialize attendance file
def initialize_attendance_file():
    today = datetime.now().strftime("%Y-%m-%d")
    file_path = os.path.join("data/attendance", f"attendance_{today}.csv")
    if not os.path.exists(file_path):
        df = pd.DataFrame(columns=["Name", "Time", "Date"])
        df.to_csv(file_path, index=False)
    return file_path

# Get attendance file for a specific date
def get_attendance_file(date):
    date_str = date.strftime("%Y-%m-%d")
    return os.path.join("data/attendance", f"attendance_{date_str}.csv")

# Mark attendance
def mark_attendance(name):
    file_path = initialize_attendance_file()
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        # Check if already marked today
        if not ((df["Name"] == name) & (df["Date"] == date_str)).any():
            new_row = pd.DataFrame({"Name": [name], "Time": [time_str], "Date": [date_str]})
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(file_path, index=False)
            return True
    else:
        df = pd.DataFrame({"Name": [name], "Time": [time_str], "Date": [date_str]})
        df.to_csv(file_path, index=False)
        return True
    return False

# Get all registered students
def get_registered_students():
    students = []
    student_dir = "data/student_images"
    if os.path.exists(student_dir):
        students = [f.split(".")[0] for f in os.listdir(student_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
    return students

# Get all attendance records
def get_all_attendance():
    all_files = [f for f in os.listdir("data/attendance") if f.startswith("attendance_") and f.endswith(".csv")]
    if not all_files:
        return pd.DataFrame(columns=["Name", "Time", "Date"])
    
    all_data = []
    for file in all_files:
        file_path = os.path.join("data/attendance", file)
        try:
            df = pd.read_csv(file_path)
            all_data.append(df)
        except:
            pass
    
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    return pd.DataFrame(columns=["Name", "Time", "Date"])

# Initialize session states
if 'students' not in st.session_state:
    st.session_state.students = get_registered_students()
if 'current_mode' not in st.session_state:
    st.session_state.current_mode = "Home"
if 'uploaded_image' not in st.session_state:
    st.session_state.uploaded_image = None
if 'manually_marked' not in st.session_state:
    st.session_state.manually_marked = []

# Application title
st.title("Face Recognition Attendance System")

# Sidebar menu
st.sidebar.title("Menu")
app_mode = st.sidebar.selectbox("Choose Mode:", ["Home", "Register New Student", "Manual Attendance", "View Attendance"])

# Home Page
if app_mode == "Home":
    st.markdown("## Welcome to the Attendance System")
    st.markdown("""
    This application allows you to:
    
    * Register new students to the system
    * Manually mark attendance
    * View attendance history
    
    ### Currently Registered Students
    """)
    
    students = get_registered_students()
    if students:
        for student in students:
            st.write(f"- {student}")
    else:
        st.info("No students registered yet. Go to 'Register New Student' to add students.")

# Register New Student
elif app_mode == "Register New Student":
    st.markdown("## Register New Student")
    
    # Input for the name
    student_name = st.text_input("Enter Student's Name:")
    
    # Check if name already exists
    if student_name and student_name in get_registered_students():
        st.warning(f"A student named '{student_name}' is already registered. Please use a different name.")
    elif student_name:
        # Upload image
        uploaded_file = st.file_uploader("Upload Student Photo", type=["jpg", "jpeg", "png"])
        
        if uploaded_file is not None:
            # Display image
            image = Image.open(uploaded_file)
            st.image(image, caption=f"Photo of {student_name}", width=300)
            
            # Register button
            if st.button("Register Student"):
                # Save the image
                image_path = os.path.join("data/student_images", f"{student_name}.jpg")
                image.save(image_path)
                
                # Update registered students list
                st.session_state.students = get_registered_students()
                
                st.success(f"Student {student_name} registered successfully!")
                time.sleep(2)
                st.rerun()

# Manual Attendance
elif app_mode == "Manual Attendance":
    st.markdown("## Manual Attendance")
    
    students = get_registered_students()
    
    if not students:
        st.warning("No students registered yet. Please register students first.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Mark Attendance")
            
            # Create a selection box for students
            selected_student = st.selectbox("Select Student", students)
            
            # Mark attendance button
            if st.button("Mark Present"):
                success = mark_attendance(selected_student)
                if success:
                    st.success(f"Attendance marked for {selected_student}")
                    if selected_student not in st.session_state.manually_marked:
                        st.session_state.manually_marked.append(selected_student)
                else:
                    st.info(f"Attendance already marked for {selected_student} today")
        
        with col2:
            st.subheader("Today's Attendance")
            
            # Show students marked present today
            today = datetime.now().strftime("%Y-%m-%d")
            file_path = get_attendance_file(datetime.now())
            
            if os.path.exists(file_path):
                today_df = pd.read_csv(file_path)
                if not today_df.empty:
                    for _, row in today_df.iterrows():
                        st.write(f"✅ {row['Name']} - {row['Time']}")
                else:
                    st.info("No attendance marked yet for today")
            else:
                st.info("No attendance marked yet for today")

# View Attendance
elif app_mode == "View Attendance":
    st.markdown("## View Attendance History")
    
    # Date selection
    selected_date = st.date_input("Select Date", datetime.now().date())
    attendance_file_path = get_attendance_file(selected_date)
    
    if os.path.exists(attendance_file_path):
        df = pd.read_csv(attendance_file_path)
        if not df.empty:
            st.markdown(f"### Attendance for {selected_date.strftime('%Y-%m-%d')}")
            st.dataframe(df)
        else:
            st.info(f"No attendance records for {selected_date.strftime('%Y-%m-%d')}")
    else:
        st.info(f"No attendance records for {selected_date.strftime('%Y-%m-%d')}")
    
    # Show overall attendance history
    st.markdown("### Overall Attendance History")
    attendance_history = get_all_attendance()
    
    if not attendance_history.empty:
        # Create a pivot table for easier visualization
        try:
            pivot_df = attendance_history.pivot_table(
                index='Date', 
                columns='Name', 
                values='Time', 
                aggfunc='first',
                fill_value='Absent'
            )
            
            # Replace actual times with "Present"
            for col in pivot_df.columns:
                pivot_df[col] = pivot_df[col].apply(lambda x: "Present" if x != "Absent" else "Absent")
            
            st.dataframe(pivot_df)
        except:
            st.dataframe(attendance_history)
        
        # Download button for attendance history
        csv = attendance_history.to_csv(index=False)
        st.download_button(
            label="Download Attendance History",
            data=csv,
            file_name="attendance_history.csv",
            mime="text/csv",
        )
    else:
        st.info("No attendance records found.")
