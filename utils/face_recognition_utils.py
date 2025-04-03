import cv2
import numpy as np
import os
import face_recognition
import pickle

# Define constants
FACES_DIR = "data/faces"
ENCODINGS_FILE = os.path.join(FACES_DIR, "encodings.pickle")

def load_known_faces():
    """
    Load known face encodings and names from the encodings file
    
    Returns:
        tuple: (list of face encodings, list of corresponding names)
    """
    # Initialize empty lists
    known_face_encodings = []
    known_face_names = []
    
    # Check if encodings file exists
    if os.path.exists(ENCODINGS_FILE):
        with open(ENCODINGS_FILE, 'rb') as f:
            data = pickle.load(f)
            known_face_encodings = data.get("encodings", [])
            known_face_names = data.get("names", [])
    
    return known_face_encodings, known_face_names

def save_known_faces(known_face_encodings, known_face_names):
    """
    Save face encodings and names to the encodings file
    
    Args:
        known_face_encodings (list): List of face encodings
        known_face_names (list): List of corresponding names
    """
    # Create directory if it doesn't exist
    os.makedirs(FACES_DIR, exist_ok=True)
    
    # Save encodings to file
    data = {
        "encodings": known_face_encodings,
        "names": known_face_names
    }
    with open(ENCODINGS_FILE, 'wb') as f:
        pickle.dump(data, f)

def add_face_encoding(image, name):
    """
    Add a new face encoding for the given image and name
    
    Args:
        image (numpy.ndarray): Image containing the face
        name (str): Name of the person
        
    Returns:
        bool: True if face was detected and added, False otherwise
    """
    # Detect face locations
    face_locations = face_recognition.face_locations(image)
    
    # If no faces detected, return False
    if len(face_locations) == 0:
        return False
    
    # Get face encodings
    face_encodings = face_recognition.face_encodings(image, face_locations)
    
    # Get the first face encoding
    face_encoding = face_encodings[0]
    
    # Load existing data
    known_face_encodings, known_face_names = load_known_faces()
    
    # Add new face encoding and name
    known_face_encodings.append(face_encoding)
    known_face_names.append(name)
    
    # Save updated data
    save_known_faces(known_face_encodings, known_face_names)
    
    return True

def detect_known_faces(frame, known_face_encodings, known_face_names):
    """
    Detect and recognize faces in the given frame
    
    Args:
        frame (numpy.ndarray): Image frame to process
        known_face_encodings (list): List of known face encodings
        known_face_names (list): List of corresponding names
        
    Returns:
        tuple: (list of face locations, list of recognized names)
    """
    # If there are no known faces, return empty results
    if len(known_face_encodings) == 0:
        return [], []
    
    # Resize frame for faster processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    
    # Find all face locations and encodings in the current frame
    face_locations = face_recognition.face_locations(small_frame)
    face_encodings = face_recognition.face_encodings(small_frame, face_locations)
    
    face_names = []
    for face_encoding in face_encodings:
        # Compare face with known faces
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"
        
        # Use the known face with the smallest distance to the new face
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        if len(face_distances) > 0:  # Check if the list is not empty
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
        
        face_names.append(name)
    
    # Convert face locations from 1/4 size back to full size
    face_locations = [(top * 4, right * 4, bottom * 4, left * 4) 
                      for (top, right, bottom, left) in face_locations]
    
    return face_locations, face_names
