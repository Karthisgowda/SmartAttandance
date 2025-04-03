import streamlit as st
import cv2
import numpy as np
import pandas as pd
import os
import time
import datetime
from utils.face_recognition_utils import detect_known_faces, load_known_faces, add_face_encoding
from utils.attendance_utils import mark_attendance, get_attendance_file, load_attendance_history

# Set page config
st.set_page_config(
    page_title="Face Recognition Attendance System",
    page_icon="📊",
    layout="wide"
)

# Create necessary directories if they don't exist
os.makedirs("data/faces", exist_ok=True)
os.makedirs("data/attendance", exist_ok=True)

# Initialize session states
if 'registered_names' not in st.session_state:
    st.session_state.registered_names = []
if 'current_frame' not in st.session_state:
    st.session_state.current_frame = None
if 'attendance_marked' not in st.session_state:
    st.session_state.attendance_marked = []
if 'camera_active' not in st.session_state:
    st.session_state.camera_active = False

# Application title
st.title("Face Recognition Attendance System")

# Sidebar menu
st.sidebar.title("Menu")
app_mode = st.sidebar.selectbox("Choose Mode:", ["Home", "Register New Face", "Take Attendance", "View Attendance"])

# Load known faces
known_face_encodings, known_face_names = load_known_faces()
st.session_state.registered_names = known_face_names

# Home Page
if app_mode == "Home":
    st.markdown("## Welcome to Face Recognition Attendance System")
    st.markdown("""
    This application allows you to:
    
    * Register new faces to the system
    * Take attendance using face recognition
    * View attendance history
    
    ### Currently Registered Users
    """)
    
    if len(st.session_state.registered_names) > 0:
        registered_df = pd.DataFrame({"Name": st.session_state.registered_names})
        st.dataframe(registered_df)
    else:
        st.info("No users registered yet. Go to 'Register New Face' to add users.")

# Register New Face
elif app_mode == "Register New Face":
    st.markdown("## Register New Face")
    
    # Input for the name
    person_name = st.text_input("Enter Person's Name:")
    
    # Check if name already exists
    if person_name and person_name in st.session_state.registered_names:
        st.warning(f"A person named '{person_name}' is already registered. Please use a different name.")
        person_name = ""
    
    col1, col2 = st.columns(2)
    
    # Camera feed for registration
    with col1:
        if person_name:
            register_button = st.button("Start Camera for Registration")
            stop_button = st.button("Stop Camera")
            
            if register_button:
                st.session_state.camera_active = True
            
            if stop_button:
                st.session_state.camera_active = False
            
            if st.session_state.camera_active:
                camera_placeholder = st.empty()
                try:
                    cap = cv2.VideoCapture(0)
                    while st.session_state.camera_active:
                        ret, frame = cap.read()
                        if not ret:
                            st.error("Failed to access the camera. Please check your camera connection.")
                            break
                        
                        # Convert to RGB for display and face recognition
                        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        st.session_state.current_frame = rgb_frame.copy()
                        
                        # Display the frame
                        camera_placeholder.image(rgb_frame, channels="RGB", use_column_width=True)
                        time.sleep(0.1)  # To reduce CPU usage
                    
                    cap.release()
                except Exception as e:
                    st.error(f"Error accessing camera: {e}")
    
    # Capture and register
    with col2:
        if st.session_state.current_frame is not None and person_name:
            st.image(st.session_state.current_frame, caption="Current Frame", use_column_width=True)
            if st.button("Capture and Register"):
                with st.spinner("Processing..."):
                    # Save face encoding
                    success = add_face_encoding(st.session_state.current_frame, person_name)
                    if success:
                        st.success(f"Successfully registered {person_name}!")
                        # Reload known faces
                        known_face_encodings, known_face_names = load_known_faces()
                        st.session_state.registered_names = known_face_names
                        st.session_state.current_frame = None
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("No face detected in the image. Please try again.")

# Take Attendance
elif app_mode == "Take Attendance":
    st.markdown("## Take Attendance")
    
    # Check if there are registered faces
    if len(known_face_encodings) == 0:
        st.warning("No faces registered yet. Please register faces before taking attendance.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            start_button = st.button("Start Camera")
            stop_button = st.button("Stop Camera")
            
            if start_button:
                st.session_state.camera_active = True
                # Reset attendance marked list
                st.session_state.attendance_marked = []
            
            if stop_button:
                st.session_state.camera_active = False
            
            if st.session_state.camera_active:
                camera_placeholder = st.empty()
                try:
                    cap = cv2.VideoCapture(0)
                    while st.session_state.camera_active:
                        ret, frame = cap.read()
                        if not ret:
                            st.error("Failed to access the camera. Please check your camera connection.")
                            break
                        
                        # Convert to RGB for display and face recognition
                        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        
                        # Detect faces
                        face_locations, face_names = detect_known_faces(rgb_frame, known_face_encodings, known_face_names)
                        
                        # Draw rectangles and names on the frame
                        for (top, right, bottom, left), name in zip(face_locations, face_names):
                            # Draw rectangle around the face
                            cv2.rectangle(rgb_frame, (left, top), (right, bottom), (0, 255, 0), 2)
                            
                            # Draw a label with the name below the face
                            cv2.rectangle(rgb_frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
                            cv2.putText(rgb_frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
                            
                            # Mark attendance if not already marked
                            if name != "Unknown" and name not in st.session_state.attendance_marked:
                                mark_attendance(name)
                                st.session_state.attendance_marked.append(name)
                        
                        # Display the frame
                        camera_placeholder.image(rgb_frame, channels="RGB", use_column_width=True)
                        time.sleep(0.1)  # To reduce CPU usage
                    
                    cap.release()
                except Exception as e:
                    st.error(f"Error accessing camera: {e}")
        
        with col2:
            st.markdown("### Attendance Marked Today")
            
            # Display the list of people who have been marked present
            if st.session_state.attendance_marked:
                for name in st.session_state.attendance_marked:
                    st.success(f"✅ {name}")
            else:
                st.info("No attendance marked yet. Start the camera and face recognition to mark attendance.")

# View Attendance
elif app_mode == "View Attendance":
    st.markdown("## View Attendance History")
    
    # Date selection
    selected_date = st.date_input("Select Date", datetime.date.today())
    attendance_file_path = get_attendance_file(selected_date)
    
    if os.path.exists(attendance_file_path):
        df = pd.read_csv(attendance_file_path)
        st.markdown(f"### Attendance for {selected_date}")
        st.dataframe(df)
    else:
        st.info(f"No attendance records found for {selected_date}")
    
    # Show overall attendance history
    st.markdown("### Overall Attendance History")
    attendance_history = load_attendance_history()
    
    if not attendance_history.empty:
        # Create a pivot table for easier visualization
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
