import face_recognition
import cv2
import os
import numpy as np

# --- 1. "Learning" Phase: Teach the program about your known students ---

# Create empty lists to store the "face prints" (encodings) and their names
known_face_encodings = []
known_face_names = []

# Define the path to your 'database' of known faces
known_faces_dir = "known_faces"
print("Loading known faces...")

# Loop through every file in the known_faces folder
for filename in os.listdir(known_faces_dir):
    # Check if the file is an image
    if filename.endswith((".jpg", ".png", ".jpeg")):
        # Construct the full file path
        filepath = os.path.join(known_faces_dir, filename)
        
        # Load the image
        known_image = face_recognition.load_image_file(filepath)
        
        # Get the "face print" (encoding)
        # We assume [0] because there is only ONE person in each known_face photo
        try:
            encoding = face_recognition.face_encodings(known_image)[0]
            
            # Get the name from the filename (e.g., "susan.jpg" -> "susan")
            name = os.path.splitext(filename)[0]
            
            # Add the encoding and name to our lists
            known_face_encodings.append(encoding)
            known_face_names.append(name)
            print(f"Learned: {name}")

        except IndexError:
            print(f"Warning: No face found in {filename}. Skipping.")


print("...Learning complete.")
print("--------------------")

# --- 2. "Recognition" Phase: Find and identify people in the class photo ---

# Define the path to your test image (MAKE SURE THIS FILENAME IS CORRECT)
test_image_path = "test_images/class_photo.jpg"

# Load the test image (the "class photo")
# We load it with face_recognition to find faces
unknown_image_fr = face_recognition.load_image_file(test_image_path)

# We ALSO load it with OpenCV to be able to draw on it later
# (OpenCV and face_recognition load colors in a different order: BGR vs RGB)
unknown_image_cv = cv2.imread(test_image_path)

# Find all the locations of faces in the class photo
unknown_face_locations = face_recognition.face_locations(unknown_image_fr)
# Get the "face prints" for all those faces
unknown_face_encodings = face_recognition.face_encodings(unknown_image_fr, unknown_face_locations)

print(f"Found {len(unknown_face_locations)} faces in the class photo.")

# Create a list to hold the names of people who are present
students_present = []

# Loop through each face found in the unknown image
for (top, right, bottom, left), face_encoding in zip(unknown_face_locations, unknown_face_encodings):
    
    # Compare this unknown face to ALL the known faces
    matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
    
    name = "Unknown" # Default name if no match is found

    # This part finds the *best* match if there are multiple
    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
    best_match_index = np.argmin(face_distances)
    
    if matches[best_match_index]:
        name = known_face_names[best_match_index]
        
        # Add to our present list, but only if they aren't already in it
        if name not in students_present:
            students_present.append(name)

    # --- 3. "Reporting" Phase: Draw boxes and show the result ---

    # Draw a green box around the face
    cv2.rectangle(unknown_image_cv, (left, top), (right, bottom), (0, 255, 0), 2)
    
    # Draw a black label with the name below the face
    cv2.rectangle(unknown_image_cv, (left, bottom - 25), (right, bottom), (0, 0, 0), cv2.FILLED)
    font = cv2.FONT_HERSHEY_DUPLEX
    cv2.putText(unknown_image_cv, name, (left + 6, bottom - 6), font, 0.8, (255, 255, 255), 1)

# --- Final Output ---

# 1. Print the text report to the terminal
print("--------------------")
print("Attendance Report:")
if students_present:
    for student in students_present:
        print(f"- {student} (Present)")
else:
    print("No known students were found.")
print("--------------------")

# 2. Show the final image with boxes and names
print("Displaying results. Press any key to close the image window.")
cv2.imshow("Smart Attendance Result", unknown_image_cv)
cv2.waitKey(0) # Wait until the user presses a key
cv2.destroyAllWindows() # Close the image window