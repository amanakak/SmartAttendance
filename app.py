import streamlit as st
import face_recognition
import cv2
import numpy as np
import os
import pandas as pd
from datetime import datetime

import auth  # <--- IMPORT THE NEW FILE

# --- LOGIN CHECK (Add this block right here) ---
if not auth.check_password():
    st.stop()  # Stop the script if not logged in
    
# --- CONFIGURATION ---
KNOWN_FACES_DIR = "known_faces"
ATTENDANCE_FILE = "attendance_log.csv"

# --- 1. FUNCTION TO LOAD KNOWN FACES ---
@st.cache_resource
def load_known_faces():
    known_encodings = []
    known_names = []
    
    if not os.path.exists(KNOWN_FACES_DIR):
        os.makedirs(KNOWN_FACES_DIR)
        return [], []

    for filename in os.listdir(KNOWN_FACES_DIR):
        if filename.endswith((".jpg", ".png", ".jpeg")):
            filepath = os.path.join(KNOWN_FACES_DIR, filename)
            image = face_recognition.load_image_file(filepath)
            try:
                encoding = face_recognition.face_encodings(image)[0]
                name = os.path.splitext(filename)[0]
                known_encodings.append(encoding)
                known_names.append(name)
            except IndexError:
                pass
    
    return known_encodings, known_names

# --- 2. FUNCTION TO SAVE ATTENDANCE ---
def mark_attendance(name, status):
    if not os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, 'w') as f:
            f.write('Name,Time,Date,Status\n')
            
    with open(ATTENDANCE_FILE, 'a') as f:
        now = datetime.now()
        time_str = now.strftime('%H:%M:%S')
        date_str = now.strftime('%Y-%m-%d')
        f.write(f'{name},{time_str},{date_str},{status}\n')

# --- 3. FUNCTION TO PROCESS AN IMAGE (from camera or upload) ---
# We make this a function to avoid duplicating code
def process_image(image_bytes, known_encodings, known_names):
    # Convert the file buffer to an image OpenCV can read
    cv2_img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    
    # Convert BGR (OpenCV standard) to RGB (face_recognition standard)
    rgb_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)

    # Find faces
    face_locations = face_recognition.face_locations(rgb_img)
    face_encodings = face_recognition.face_encodings(rgb_img, face_locations)

    st.success(f"Found {len(face_locations)} faces in the image.")

    found_names = []

    # Process each face found
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.6)
        name = "Unknown"
        
        face_distances = face_recognition.face_distance(known_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        
        if matches[best_match_index]:
            name = known_names[best_match_index]
        
        found_names.append(name)

        # Draw box on the image for the UI
        color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
        cv2.rectangle(cv2_img, (left, top), (right, bottom), color, 2)
        cv2.putText(cv2_img, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    # Show the annotated image
    st.image(cv2_img, channels="BGR", caption="Processed Image")

    # --- REPORTING & CHARTING ---
    st.subheader("Attendance Report")

    present_students = set(name for name in found_names if name != "Unknown")
    all_students = set(known_names)
    absent_students = all_students - present_students

    attendance_data = []
    for student in all_students:
        status = "Present" if student in present_students else "Absent"
        attendance_data.append({"Student Name": student, "Status": status})
        
        # Save to CSV file
        mark_attendance(student, status)

    df = pd.DataFrame(attendance_data)

    # 1. Show the Data Table
    st.dataframe(df.style.applymap(lambda v: 'color: green' if v == 'Present' else 'color: red', subset=['Status']))

    # 2. Show the Bar Chart
    st.subheader("Visual Chart")
    count_data = pd.DataFrame({
        "Status": ["Present", "Absent"],
        "Count": [len(present_students), len(absent_students)]
    })
    st.bar_chart(count_data.set_index("Status"))

    st.success(f"Attendance has been logged to '{ATTENDANCE_FILE}'!")

# --- 4. THE MAIN UI ---
st.title("📸 Smart Attendance System")

# Load the database
known_encodings, known_names = load_known_faces()

# Show the list of students expected (the database)
if st.checkbox("Show Class List (Database)"):
    if known_names:
        st.write(f"Loaded {len(known_names)} students: {', '.join(known_names)}")
    else:
        st.warning("No students found in 'known_faces' folder. Please add student photos.")

st.info("Use your webcam to take a picture OR upload an existing photo.")

# --- INPUT OPTION 1: CAMERA ---
img_file_buffer = st.camera_input("Take a picture of the class")

# --- INPUT OPTION 2: FILE UPLOAD ---
# st.or_()  <--- THIS LINE IS REMOVED
uploaded_file = st.file_uploader("Or upload a class photo", type=["jpg", "png", "jpeg"])

# --- PROCESSING LOGIC ---
if img_file_buffer is not None:
    # A photo was taken with the camera
    st.write("Processing camera photo...")
    process_image(img_file_buffer.getvalue(), known_encodings, known_names)

elif uploaded_file is not None:
    # A file was uploaded
    st.write("Processing uploaded file...")
    process_image(uploaded_file.getvalue(), known_encodings, known_names)