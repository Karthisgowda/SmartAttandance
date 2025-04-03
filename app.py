import streamlit as st
import cv2
import numpy as np
import os
import pandas as pd
from datetime import datetime
import time
from face_recognition_utils import (
    detect_known_faces,
    add_face_encoding,
    load_known_faces
)
from attendance_utils import (
    mark_attendance,
    get_attendance_log,
    create_attendance_file_if_not_exists
)

# Page configuration
st.set_page_config(
    page_title="Face Recognition Attendance System",
    page_icon="🧑‍💻",
    layout="wide"
)

# Create necessary directories if they don't exist
os.makedirs("data/known_faces", exist_ok=True)
os.makedirs("data/attendance_logs", exist_ok=True)

# Initialize session state variables if they don't exist
if 'stop_camera' not in st.session_state:
    st.session_state.stop_camera = False
if 'new_person_name' not in st.session_state:
    st.session_state.new_person_name = ""
if 'capture_image' not in st.session_state:
    st.session_state.capture_image = False
if 'captured_image' not in st.session_state:
    st.session_state.captured_image = None
if 'confirmation_step' not in st.session_state:
    st.session_state.confirmation_step = False
if 'known_names' not in st.session_state:
    st.session_state.known_names = []
if 'last_attendance_check' not in st.session_state:
    st.session_state.last_attendance_check = {}

# Function to reset the add person flow
def reset_add_person_flow():
    st.session_state.new_person_name = ""
    st.session_state.capture_image = False
    st.session_state.captured_image = None
    st.session_state.confirmation_step = False

# Load known faces on app startup
@st.cache_resource
def initialize_known_faces():
    return load_known_faces()

# Main title and description
st.title("Face Recognition Attendance System")
st.markdown("An automated system that uses facial recognition to track attendance")

# Create tabs for different functionalities
tab1, tab2, tab3 = st.tabs(["Take Attendance", "Add New Person", "View Attendance Log"])

# Today's date for attendance file
today = datetime.now().strftime("%Y-%m-%d")
attendance_file = f"data/attendance_logs/attendance_{today}.csv"
create_attendance_file_if_not_exists(attendance_file)

# Initialize the known faces
known_face_encodings, known_face_names = initialize_known_faces()
st.session_state.known_names = known_face_names

# Tab 1: Take Attendance
with tab1:
    st.header("Take Attendance")
    
    # Instructions
    st.markdown("""
    1. Click 'Start Camera' to begin face recognition.
    2. The system will automatically recognize registered faces and mark attendance.
    3. Click 'Stop Camera' when done.
    """)
    
    # Camera controls
    col1, col2 = st.columns(2)
    start_button = col1.button("Start Camera", key="start_cam")
    stop_button = col2.button("Stop Camera", key="stop_cam")
    
    if stop_button:
        st.session_state.stop_camera = True
    
    if start_button:
        st.session_state.stop_camera = False
    
    # Camera feed placeholder
    camera_placeholder = st.empty()
    
    # Status message placeholder
    status_message = st.empty()
    
    # Check if there are any known faces
    if len(known_face_names) == 0:
        st.warning("No registered faces found. Please add a person in the 'Add New Person' tab.")
    
    # Start the camera if the button is clicked and not stopped
    if start_button or (not st.session_state.stop_camera and 'start_cam' in st.session_state):
        try:
            # Initialize webcam
            cap = cv2.VideoCapture(0)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            if not cap.isOpened():
                st.error("Error: Could not open webcam. Please check your camera connection.")
            else:
                while not st.session_state.stop_camera:
                    # Read frame from webcam
                    ret, frame = cap.read()
                    if not ret:
                        st.error("Failed to capture image from camera.")
                        break
                    
                    # Process the frame for face recognition
                    face_locations, face_names = detect_known_faces(
                        frame,
                        known_face_encodings,
                        known_face_names
                    )
                    
                    # Draw rectangles and labels for each detected face
                    for (top, right, bottom, left), name in zip(face_locations, face_names):
                        # Draw a rectangle around the face
                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                        
                        # Draw a label with the name below the face
                        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
                        cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1)
                        
                        # Mark attendance if the person is recognized
                        if name != "Unknown":
                            current_time = datetime.now()
                            # Limit attendance marking to once every 60 seconds per person
                            if name not in st.session_state.last_attendance_check or \
                               (current_time - st.session_state.last_attendance_check[name]).total_seconds() > 60:
                                mark_attendance(name, attendance_file)
                                st.session_state.last_attendance_check[name] = current_time
                                status_message.success(f"Attendance marked for {name}")
                    
                    # Convert BGR to RGB for display
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Display the image in Streamlit
                    camera_placeholder.image(rgb_frame, channels="RGB", use_column_width=True)
                    
                    # Add a short delay to reduce CPU usage
                    time.sleep(0.1)
                
                # Release the webcam when done
                cap.release()
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            if 'cap' in locals() and cap.isOpened():
                cap.release()

# Tab 2: Add New Person
with tab2:
    st.header("Add New Person")
    
    # Instructions
    st.markdown("""
    1. Enter the name of the person to add.
    2. Click 'Capture Image' to take a photo.
    3. Confirm the image quality and positioning.
    4. Click 'Save Person' to add them to the system.
    """)
    
    # Input for person's name
    st.session_state.new_person_name = st.text_input("Enter Person's Name", value=st.session_state.new_person_name)
    
    # Check if the name already exists
    name_exists = st.session_state.new_person_name.strip() in st.session_state.known_names
    
    if st.session_state.new_person_name.strip() == "":
        st.warning("Please enter a name.")
    elif name_exists:
        st.warning(f"A person with the name '{st.session_state.new_person_name}' already exists. Please use a different name.")
    
    # Image capture and confirmation section
    col1, col2 = st.columns(2)
    
    # Capture button
    capture_button = col1.button("Capture Image", disabled=name_exists or st.session_state.new_person_name.strip() == "")
    
    if capture_button:
        st.session_state.capture_image = True
        st.session_state.confirmation_step = False
        st.session_state.captured_image = None
    
    # Reset button
    reset_button = col2.button("Reset", on_click=reset_add_person_flow)
    
    # Camera feed and captured image placeholders
    camera_view = st.empty()
    confirmation_view = st.empty()
    
    # Capture image from webcam
    if st.session_state.capture_image and not st.session_state.confirmation_step and not name_exists:
        try:
            cap = cv2.VideoCapture(0)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            if not cap.isOpened():
                st.error("Error: Could not open webcam. Please check your camera connection.")
            else:
                with camera_view.container():
                    st.write("Position your face in the frame and press 'Take Photo'")
                    frame_placeholder = st.empty()
                    take_photo_button = st.button("Take Photo")
                    
                    while not take_photo_button:
                        # Read frame from webcam
                        ret, frame = cap.read()
                        if not ret:
                            st.error("Failed to capture image from camera.")
                            break
                        
                        # Convert BGR to RGB for display
                        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        
                        # Display the image in Streamlit
                        frame_placeholder.image(rgb_frame, channels="RGB", use_column_width=True)
                        
                        # Check if button is pressed
                        if take_photo_button:
                            break
                        
                        # Add a short delay to reduce CPU usage
                        time.sleep(0.1)
                        
                        # Rerun to check if button was pressed
                        if not take_photo_button:
                            time.sleep(0.1)
                            take_photo_button = st.button("Take Photo", key="take_photo_recheck")
                
                # If Take Photo button was pressed, store the image
                if take_photo_button:
                    ret, frame = cap.read()
                    if ret:
                        st.session_state.captured_image = frame.copy()
                        st.session_state.confirmation_step = True
                        st.session_state.capture_image = False
                
                # Release the webcam
                cap.release()
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            if 'cap' in locals() and cap.isOpened():
                cap.release()
    
    # Confirmation step
    if st.session_state.confirmation_step and st.session_state.captured_image is not None:
        with confirmation_view.container():
            st.write("Review the captured image:")
            
            # Display the captured image
            rgb_image = cv2.cvtColor(st.session_state.captured_image, cv2.COLOR_BGR2RGB)
            st.image(rgb_image, channels="RGB", width=400)
            
            col1, col2 = st.columns(2)
            save_button = col1.button("Save Person")
            retake_button = col2.button("Retake Photo")
            
            if save_button:
                # Check if face is detected in the image
                face_locations = face_recognition_utils.face_locations(rgb_image)
                
                if len(face_locations) == 0:
                    st.error("No face detected in the image. Please retake the photo.")
                elif len(face_locations) > 1:
                    st.error("Multiple faces detected. Please ensure only one person is in the frame.")
                else:
                    # Add the face encoding to the known faces
                    success = add_face_encoding(
                        st.session_state.captured_image, 
                        st.session_state.new_person_name
                    )
                    
                    if success:
                        st.success(f"Successfully added {st.session_state.new_person_name} to the system!")
                        # Reload known faces
                        known_face_encodings, known_face_names = load_known_faces()
                        st.session_state.known_names = known_face_names
                        # Reset the flow
                        reset_add_person_flow()
                        # Rerun the app to update the UI
                        st.rerun()
                    else:
                        st.error("Failed to add the person. Please try again.")
            
            if retake_button:
                st.session_state.capture_image = True
                st.session_state.confirmation_step = False
                st.session_state.captured_image = None

# Tab 3: View Attendance Log
with tab3:
    st.header("Attendance Log")
    
    # Date selection for viewing attendance
    available_dates = [f.split("_")[1].split(".")[0] for f in os.listdir("data/attendance_logs") 
                      if f.startswith("attendance_") and f.endswith(".csv")]
    
    if not available_dates:
        st.warning("No attendance records found.")
    else:
        # Sort dates in descending order (most recent first)
        available_dates.sort(reverse=True)
        
        selected_date = st.selectbox("Select Date", available_dates)
        
        # Load and display attendance for the selected date
        selected_file = f"data/attendance_logs/attendance_{selected_date}.csv"
        
        if os.path.exists(selected_file):
            attendance_df = get_attendance_log(selected_file)
            
            if attendance_df.empty:
                st.info(f"No attendance records for {selected_date}.")
            else:
                st.write(f"Attendance for {selected_date}:")
                st.dataframe(attendance_df)
                
                # Add download button for the CSV
                csv = attendance_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"attendance_{selected_date}.csv",
                    mime="text/csv",
                )
        else:
            st.error(f"Attendance file for {selected_date} not found.")
