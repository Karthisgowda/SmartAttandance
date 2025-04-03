import os
import cv2
import numpy as np
import face_recognition
import pickle
import time

# Path to the known faces directory
KNOWN_FACES_DIR = "data/known_faces"

def load_known_faces():
    """
    Load all known face encodings from the known_faces directory.
    
    Returns:
        tuple: (known_face_encodings, known_face_names)
    """
    known_face_encodings = []
    known_face_names = []
    
    # Ensure the directory exists
    os.makedirs(KNOWN_FACES_DIR, exist_ok=True)
    
    # Get all pickle files from the known_faces directory
    for filename in os.listdir(KNOWN_FACES_DIR):
        if filename.endswith(".pkl"):
            try:
                with open(os.path.join(KNOWN_FACES_DIR, filename), 'rb') as f:
                    data = pickle.load(f)
                    encoding = data['encoding']
                    name = data['name']
                    
                    known_face_encodings.append(encoding)
                    known_face_names.append(name)
            except Exception as e:
                print(f"Error loading face encoding from {filename}: {e}")
    
    return known_face_encodings, known_face_names

def detect_known_faces(frame, known_face_encodings, known_face_names):
    """
    Detect and recognize faces in a frame.
    
    Args:
        frame: The video frame to process
        known_face_encodings: List of known face encodings
        known_face_names: List of names corresponding to the encodings
        
    Returns:
        tuple: (face_locations, face_names)
    """
    # Resize frame for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    
    # Convert the image from BGR color (OpenCV) to RGB color (face_recognition)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    
    # Find all face locations and face encodings in the current frame
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
    
    face_names = []
    for face_encoding in face_encodings:
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
        name = "Unknown"
        
        # If a match was found, use the first one
        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]
        
        face_names.append(name)
    
    # Scale face locations back to original frame size
    face_locations = [(top * 4, right * 4, bottom * 4, left * 4) 
                      for (top, right, bottom, left) in face_locations]
    
    return face_locations, face_names

def add_face_encoding(frame, name):
    """
    Add a new face encoding to the known faces.
    
    Args:
        frame: Video frame containing the face
        name: Name of the person
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Convert the image from BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect face locations
        face_locations = face_recognition.face_locations(rgb_frame)
        
        if len(face_locations) != 1:
            return False  # Require exactly one face
        
        # Compute face encoding
        face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
        
        # Prepare data to save
        data = {
            'name': name,
            'encoding': face_encoding,
            'timestamp': time.time()
        }
        
        # Create a filename based on the name (replacing spaces with underscores)
        filename = f"{name.replace(' ', '_')}_{int(time.time())}.pkl"
        filepath = os.path.join(KNOWN_FACES_DIR, filename)
        
        # Save the encoding to a pickle file
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
        
        return True
    
    except Exception as e:
        print(f"Error adding face encoding: {e}")
        return False
