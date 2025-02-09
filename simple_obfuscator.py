import cv2
import numpy as np
import face_recognition

def analyze_faces(image_path):
    """Analyze faces in an image and return face locations and encodings."""
    # Load image and convert BGR to RGB (face_recognition uses RGB)
    image = cv2.imread(image_path)
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Find faces and their encodings
    face_locations = face_recognition.face_locations(rgb_image)
    face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
    
    return len(face_locations), face_encodings

def pixelate_face(image, face_cascade_path='haarcascade_frontalface_default.xml'):
    # Load the cascade classifier
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + face_cascade_path)
    
    # Convert to grayscale for face detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    
    # For each face, apply pixelation
    for (x, y, w, h) in faces:
        # Extract the face region
        face_roi = image[y:y+h, x:x+w]
        
        # Pixelate by scaling down and up
        pixel_size = max(w, h) // 20  # Adjust this value to change pixelation level
        if pixel_size < 1:
            pixel_size = 1
            
        small = cv2.resize(face_roi, (w//pixel_size, h//pixel_size), interpolation=cv2.INTER_LINEAR)
        pixelated = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
        
        # Put the pixelated face back into the image
        image[y:y+h, x:x+w] = pixelated
    
    return image

def compare_faces(original_encodings, processed_encodings, threshold=0.6):
    """Compare face encodings between original and processed images."""
    results = []
    
    for orig_encoding in original_encodings:
        # Try to find this face in the processed image
        if processed_encodings:
            # Compare with all faces in processed image
            matches = face_recognition.compare_faces(processed_encodings, orig_encoding, tolerance=threshold)
            if True in matches:
                results.append("Face still recognizable")
            else:
                results.append("Face successfully obfuscated")
        else:
            results.append("Face not detected in processed image")
            
    return results

def process_image(input_path, output_path):
    # Read image
    image = cv2.imread(input_path)
    if image is None:
        raise ValueError("Could not read the image")
    
    # Get original face analysis
    original_count, original_encodings = analyze_faces(input_path)
    
    # Process image
    processed = pixelate_face(image.copy())
    
    # Save processed image
    cv2.imwrite(output_path, processed)
    
    # Get processed face analysis
    processed_count, processed_encodings = analyze_faces(output_path)
    
    # Compare faces
    comparison_results = compare_faces(original_encodings, processed_encodings)
    
    # Prepare analysis results
    analysis = {
        'original_faces': original_count,
        'processed_faces': processed_count,
        'face_comparisons': comparison_results
    }
    
    return analysis
