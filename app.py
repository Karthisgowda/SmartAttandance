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

# Load custom CSS
def load_css():
    with open("style.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        
load_css()

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

# Application title with animated header and logo
logo_html = '''
<div class="main-header glow">
    <div style="display: flex; align-items: center; justify-content: center;">
        <img src="data:image/svg+xml;base64,{}" style="width:50px; margin-right:10px;">
        <h1>Smart Attendance System</h1>
    </div>
</div>
'''

# Read and encode logo
with open('assets/logo.svg', 'rb') as f:
    logo = base64.b64encode(f.read()).decode()

st.markdown(logo_html.format(logo), unsafe_allow_html=True)

# Sidebar menu
st.sidebar.title("Menu")
# Use session state for app mode to maintain selection across reruns
if 'app_mode' not in st.session_state:
    st.session_state.app_mode = "Home"

# Get the app mode from session state if we're redirecting from registration
if st.session_state.current_mode == "Home":
    index = 0
    st.session_state.current_mode = st.session_state.app_mode
else:
    index = None

app_mode = st.sidebar.selectbox("Choose Mode:", 
                               ["Home", "Register New Student", "Manual Attendance", "View Attendance", "XAMPP Version"],
                               index=index,
                               key="app_mode_select")

# Home Page
if app_mode == "Home":
    st.markdown('<div class="welcome-message"><h2>Welcome to the Smart Attendance System</h2></div>', unsafe_allow_html=True)
    
    # Create a card layout
    st.markdown('<div class="card-grid">', unsafe_allow_html=True)
    
    # Feature card
    st.markdown('''
    <div class="stcard">
        <h3>System Features</h3>
        <ul class="feature-list">
            <li>Register students with photo identification</li>
            <li>Mark attendance with just one click</li>
            <li>View daily attendance records</li>
            <li>Generate attendance reports and analytics</li>
        </ul>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### Currently Registered Students")
    
    students = get_registered_students()
    if students:
        st.markdown('<div class="student-list">', unsafe_allow_html=True)
        for student in students:
            st.markdown(f'<div class="student-item">{student}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No students registered yet. Go to 'Register New Student' to add students.")

# Register New Student
elif app_mode == "Register New Student":
    st.markdown('<div class="registration-form"><h2>Register New Student</h2></div>', unsafe_allow_html=True)
    
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
                # Save the image - convert to RGB to handle transparency
                image_path = os.path.join("data/student_images", f"{student_name}.jpg")
                if image.mode == 'RGBA':
                    image = image.convert('RGB')
                image.save(image_path)
                
                # Update registered students list
                st.session_state.students = get_registered_students()
                
                st.success(f"Student {student_name} registered successfully!")
                # Set mode to Home for redirection
                st.session_state.current_mode = "Home"
                time.sleep(1)
                # Redirect to Home page
                st.sidebar.selectbox("Choose Mode:", ["Home", "Register New Student", "Manual Attendance", "View Attendance", "XAMPP Version"], index=0)
                st.rerun()

# Manual Attendance
elif app_mode == "Manual Attendance":
    st.markdown('<div class="glass-panel"><h2>Manual Attendance</h2></div>', unsafe_allow_html=True)
    
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
                        st.markdown(f'<div class="attendance-mark">✅ {row["Name"]} - {row["Time"]}</div>', unsafe_allow_html=True)
                else:
                    st.info("No attendance marked yet for today")
            else:
                st.info("No attendance marked yet for today")

# View Attendance
elif app_mode == "View Attendance":
    st.markdown('<div class="glass-panel"><h2>View Attendance History</h2></div>', unsafe_allow_html=True)
    
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

# XAMPP Version
elif app_mode == "XAMPP Version":
    st.markdown('<div class="glass-panel"><h2>XAMPP Version</h2></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="stcard">
        <h3>About XAMPP Version</h3>
        <p>This is a special version of the Face Recognition Attendance System designed to run on XAMPP (Apache, MySQL, PHP).</p>
        <p>If you want to deploy this system on a web server or locally using XAMPP, this version is for you!</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="stcard">
            <h3>Features</h3>
            <ul class="feature-list">
                <li>Similar user interface with dark theme</li>
                <li>Uses MySQL database instead of CSV files</li>
                <li>Student registration with photo upload</li>
                <li>Attendance marking system</li>
                <li>Records viewing and export</li>
                <li>Data import from Streamlit version</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stcard">
            <h3>Requirements</h3>
            <ul class="feature-list">
                <li>XAMPP installed on your system</li>
                <li>Web browser</li>
                <li>Basic knowledge of web hosting</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### Download XAMPP Version")
    
    # Provide download for the XAMPP version
    col1, col2 = st.columns(2)
    
    with col1:
        try:
            with open("xampp_version/downloads/face_recognition_attendance_system_xampp_version.zip", "rb") as fp:
                btn1 = st.download_button(
                    label="Download ZIP Version (Windows)",
                    data=fp,
                    file_name="face_recognition_attendance_system_xampp_version.zip",
                    mime="application/zip",
                )
        except FileNotFoundError:
            st.warning("ZIP version not available. Please use the TAR.GZ version instead.")
    
    with col2:
        try:
            with open("xampp_version/downloads/face_recognition_attendance_system_xampp_version.tar.gz", "rb") as fp:
                btn2 = st.download_button(
                    label="Download TAR.GZ Version (Linux/Mac)",
                    data=fp,
                    file_name="face_recognition_attendance_system_xampp_version.tar.gz",
                    mime="application/gzip",
                )
        except FileNotFoundError:
            st.warning("TAR.GZ version not available. Please use the ZIP version instead.")
    
    st.markdown("""
    ### Installation Instructions
    
    1. Download and extract the ZIP file
    2. For Windows users: Run `install.bat` to automatically install to XAMPP
    3. For Mac/Linux users: Run `install.sh` to install to XAMPP
    4. Start XAMPP services (Apache and MySQL)
    5. Create the database using phpMyAdmin
    6. Import `database_setup.sql` to set up the tables
    7. Access the application at http://localhost/attendance_system
    
    For detailed instructions, refer to the README.txt file included in the download.
    """)
    
    # Data Migration
    st.markdown("### Data Migration")
    st.markdown("""
    If you want to migrate your data from this Streamlit app to the XAMPP version:
    
    1. Download your attendance history using the "Download Attendance History" button in the View Attendance page
    2. Import this CSV file using the "Import Data" option in the XAMPP version
    3. Copy student photos from the `data/student_images` folder to the `uploads` folder in the XAMPP installation
    
    The XAMPP version includes tools to help with this migration process.
    """)
