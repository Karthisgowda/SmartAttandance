import streamlit as st
import cv2
import pandas as pd
import numpy as np
import os
import time
from datetime import datetime
from face_recognition_utils import (
    detect_faces_in_frame,
    extract_face_encodings,
    compare_faces,
    register_new_user
)
from attendance_utils import (
    mark_attendance,
    get_attendance_records,
    initialize_attendance_file,
    get_registered_users
)

# Ensure directories exist
os.makedirs("data/registered_users", exist_ok=True)

# Initialize attendance file if it doesn't exist
initialize_attendance_file()

# Set page config
st.set_page_config(
    page_title="Face Recognition Attendance System",
    page_icon="📊",
    layout="wide"
)

# Create session state variables
if 'current_view' not in st.session_state:
    st.session_state.current_view = "Home"
if 'camera_running' not in st.session_state:
    st.session_state.camera_running = False
if 'frame_placeholder' not in st.session_state:
    st.session_state.frame_placeholder = None
if 'last_recognized_time' not in st.session_state:
    st.session_state.last_recognized_time = {}

# Set camera resolution
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# App title and navigation
st.title("Face Recognition Attendance System")

# Navigation menu
tabs = st.tabs(["Home", "Attendance", "Register New User"])

# Home tab
with tabs[0]:
    st.header("Welcome to Face Recognition Attendance System")
    st.write("This system automatically marks attendance when it recognizes registered faces.")
    
    # Start/Stop camera button
    if st.button("Start Camera" if not st.session_state.camera_running else "Stop Camera"):
        st.session_state.camera_running = not st.session_state.camera_running
        if not st.session_state.camera_running:
            # Release the camera when stopped
            if 'cap' in st.session_state and st.session_state.cap is not None:
                st.session_state.cap.release()
    
    # Create a placeholder for the camera feed
    camera_col, info_col = st.columns([3, 1])
    with camera_col:
        frame_placeholder = st.empty()
    
    with info_col:
        info_placeholder = st.empty()
    
    # Camera processing
    if st.session_state.camera_running:
        try:
            # Initialize camera
            if 'cap' not in st.session_state or st.session_state.cap is None:
                st.session_state.cap = cv2.VideoCapture(0)
                st.session_state.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
                st.session_state.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
            
            registered_users = get_registered_users()
            
            # Display info about registered users
            info_placeholder.write(f"Registered Users: {len(registered_users)}")
            if registered_users:
                info_placeholder.write("Recognized Users:")
            
            # Create a dictionary to store user face encodings
            if 'known_face_encodings' not in st.session_state or 'known_face_names' not in st.session_state:
                st.session_state.known_face_encodings = []
                st.session_state.known_face_names = []
                
                # Load registered user face encodings
                for user_id in registered_users:
                    user_folder = os.path.join("data/registered_users", user_id)
                    if os.path.exists(os.path.join(user_folder, "encoding.npy")):
                        encoding = np.load(os.path.join(user_folder, "encoding.npy"))
                        st.session_state.known_face_encodings.append(encoding)
                        st.session_state.known_face_names.append(user_id)
            
            # Loop to continuously grab frames from the camera
            while st.session_state.camera_running:
                ret, frame = st.session_state.cap.read()
                if not ret:
                    st.error("Failed to capture image from camera")
                    st.session_state.camera_running = False
                    break
                
                # Convert the frame from BGR (OpenCV) to RGB (face_recognition)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Detect faces in the frame
                face_locations = detect_faces_in_frame(rgb_frame)
                
                # Extract face encodings
                face_encodings = extract_face_encodings(rgb_frame, face_locations)
                
                # Initialize list to store recognized names
                face_names = []
                
                # Compare each face encoding with known encodings
                for face_encoding in face_encodings:
                    if len(st.session_state.known_face_encodings) > 0:
                        matches, name = compare_faces(
                            face_encoding, 
                            st.session_state.known_face_encodings,
                            st.session_state.known_face_names
                        )
                        
                        if matches:
                            face_names.append(name)
                            
                            # Check if we need to mark attendance (limit to once per minute per person)
                            current_time = time.time()
                            if name not in st.session_state.last_recognized_time or \
                               (current_time - st.session_state.last_recognized_time[name]) > 60:
                                mark_attendance(name)
                                st.session_state.last_recognized_time[name] = current_time
                        else:
                            face_names.append("Unknown")
                    else:
                        face_names.append("Unknown")
                
                # Draw boxes and labels on faces
                for (top, right, bottom, left), name in zip(face_locations, face_names):
                    # Draw a box around the face
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    
                    # Draw a label with the name below the face
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.75, (255, 255, 255), 2)
                
                # Convert the frame to RGB for display in Streamlit
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Update the frame in the Streamlit app
                frame_placeholder.image(frame, channels="RGB", use_column_width=True)
                
                # Update recognized users info
                recognized_names = list(set([name for name in face_names if name != "Unknown"]))
                recognized_info = ""
                for name in recognized_names:
                    recognized_info += f"- {name}\n"
                
                if recognized_names:
                    info_placeholder.write("Recognized Users:")
                    info_placeholder.text(recognized_info)
                
        except Exception as e:
            st.error(f"Error: {e}")
            st.session_state.camera_running = False
            if 'cap' in st.session_state and st.session_state.cap is not None:
                st.session_state.cap.release()
    else:
        # Show placeholder image when camera is not running
        frame_placeholder.info("Camera is turned off. Click 'Start Camera' to begin.")

# Attendance tab
with tabs[1]:
    st.header("Attendance Records")
    
    # Add date selector for filtering
    date_filter = st.date_input("Select Date", datetime.now().date())
    
    # Format date for filtering
    date_str = date_filter.strftime("%Y-%m-%d")
    
    # Get and display attendance records
    attendance_df = get_attendance_records()
    
    if attendance_df.empty:
        st.info("No attendance records found.")
    else:
        # Filter by selected date
        filtered_df = attendance_df[attendance_df["Date"] == date_str]
        
        if filtered_df.empty:
            st.info(f"No attendance records for {date_str}.")
        else:
            st.write(f"Showing attendance for {date_str}")
            st.dataframe(filtered_df)
        
        # Add download button for the CSV
        csv = attendance_df.to_csv(index=False)
        st.download_button(
            label="Download Full Attendance CSV",
            data=csv,
            file_name="attendance_records.csv",
            mime="text/csv",
        )

# Register New User tab
with tabs[2]:
    st.header("Register New User")
    
    # Form for new user registration
    with st.form("registration_form"):
        user_id = st.text_input("User ID (Name)")
        
        # Camera capture for registration
        capture_col, preview_col = st.columns(2)
        
        with capture_col:
            st.write("Please ensure your face is clearly visible")
            capture_button = st.form_submit_button("Capture Image")
        
        # Process the registration
        if capture_button and user_id:
            try:
                # Initialize camera
                cap = cv2.VideoCapture(0)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
                
                st.write("Capturing image...")
                time.sleep(2)  # Give time for camera to initialize
                
                # Capture frame
                ret, frame = cap.read()
                cap.release()
                
                if not ret:
                    st.error("Failed to capture image from camera")
                else:
                    # Convert to RGB for face_recognition
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Detect faces
                    face_locations = detect_faces_in_frame(rgb_frame)
                    
                    if not face_locations:
                        st.error("No face detected! Please try again.")
                    elif len(face_locations) > 1:
                        st.error("Multiple faces detected! Please ensure only one face is in the frame.")
                    else:
                        # Register the user
                        success = register_new_user(user_id, rgb_frame, face_locations[0])
                        
                        if success:
                            st.success(f"User {user_id} registered successfully!")
                            # Clear the session state to reload encodings
                            if 'known_face_encodings' in st.session_state:
                                del st.session_state.known_face_encodings
                            if 'known_face_names' in st.session_state:
                                del st.session_state.known_face_names
                            
                            # Show the captured image
                            with preview_col:
                                st.image(rgb_frame, caption=f"Registered: {user_id}", use_column_width=True)
                        else:
                            st.error("Failed to register user. Please try again.")
            
            except Exception as e:
                st.error(f"Error during registration: {e}")
        elif capture_button:
            st.warning("Please enter a User ID")
    
    # Display list of registered users
    st.subheader("Registered Users")
    registered_users = get_registered_users()
    
    if not registered_users:
        st.info("No users registered yet.")
    else:
        for user in registered_users:
            st.write(f"- {user}")
