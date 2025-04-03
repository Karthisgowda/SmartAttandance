import cv2
import numpy as np
import face_recognition
import os
import shutil

def detect_faces_in_frame(frame):
    """
    Detect faces in a frame using face_recognition library
    
    Args:
        frame: RGB image frame
        
    Returns:
        List of face locations (top, right, bottom, left)
    """
    # Reduce frame size for faster processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    
    # Find all face locations in the frame
    face_locations = face_recognition.face_locations(small_frame)
    
    # Scale back up the face locations
    return [(top * 4, right * 4, bottom * 4, left * 4) for (top, right, bottom, left) in face_locations]

def extract_face_encodings(frame, face_locations):
    """
    Extract face encodings for the detected faces
    
    Args:
        frame: RGB image frame
        face_locations: List of face locations (top, right, bottom, left)
        
    Returns:
        List of face encodings
    """
    # Compute the facial encodings for the faces
    return face_recognition.face_encodings(frame, face_locations)

def compare_faces(face_encoding, known_face_encodings, known_face_names, tolerance=0.6):
    """
    Compare a face encoding against known face encodings
    
    Args:
        face_encoding: Face encoding to compare
        known_face_encodings: List of known face encodings
        known_face_names: List of names corresponding to known face encodings
        tolerance: How much distance between faces to consider a match
        
    Returns:
        (match_found, name): Tuple indicating if a match was found and the name
    """
    # Compare against all known faces
    matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=tolerance)
    
    # Use the known face with the smallest distance to the new face
    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
    
    if len(face_distances) > 0:
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            return True, known_face_names[best_match_index]
    
    return False, None

def register_new_user(user_id, frame, face_location):
    """
    Register a new user by saving their face encoding
    
    Args:
        user_id: Identifier for the user
        frame: RGB image frame
        face_location: Location of the face in the frame
        
    Returns:
        bool: True if registration was successful, False otherwise
    """
    try:
        # Create directory for the user
        user_dir = os.path.join("data/registered_users", user_id)
        os.makedirs(user_dir, exist_ok=True)
        
        # Extract face encoding
        face_encoding = face_recognition.face_encodings(frame, [face_location])[0]
        
        # Save the face encoding
        np.save(os.path.join(user_dir, "encoding.npy"), face_encoding)
        
        # Save the face image
        top, right, bottom, left = face_location
        face_image = frame[top:bottom, left:right]
        
        # Convert RGB to BGR for OpenCV
        face_image_bgr = cv2.cvtColor(face_image, cv2.COLOR_RGB2BGR)
        cv2.imwrite(os.path.join(user_dir, "face.jpg"), face_image_bgr)
        
        return True
    except Exception as e:
        print(f"Error registering user: {e}")
        # Clean up if registration failed
        if os.path.exists(user_dir):
            shutil.rmtree(user_dir)
        return False
