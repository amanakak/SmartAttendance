import streamlit as st
import cv2
import numpy as np
import os

import auth # <--- Import auth

# --- LOGIN CHECK ---
if not auth.check_password():
    st.stop()

# --- CONFIGURATION ---
KNOWN_FACES_DIR = "known_faces"

st.set_page_config(page_title="Add Student", page_icon="➕")
st.title("➕ Add New Student")

st.write("Use this page to add a new student to the database.")

# --- INPUTS ---
student_name = st.text_input("Enter Student Name")
input_method = st.radio("Choose Input Method", ["Camera", "Upload File"], horizontal=True)

img_buffer = None

if input_method == "Camera":
    img_buffer = st.camera_input("Take a clear photo of the face")
else:
    img_buffer = st.file_uploader("Upload a photo", type=["jpg", "jpeg", "png"])

# --- SAVE LOGIC ---
if st.button("Save Student to Database"):
    if not student_name:
        st.error("❌ Please enter a student name.")
    elif img_buffer is None:
        st.error("❌ Please take a photo or upload a file.")
    else:
        try:
            # 1. Convert the uploaded/captured file to an OpenCV image
            bytes_data = img_buffer.getvalue()
            cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

            # 2. Check if the folder exists (just in case)
            if not os.path.exists(KNOWN_FACES_DIR):
                os.makedirs(KNOWN_FACES_DIR)

            # 3. Save the image as a JPG file using the student's name
            # We replace spaces with underscores just to be safe (e.g., "John Doe" -> "John_Doe.jpg")
            safe_filename = student_name.replace(" ", "_") + ".jpg"
            save_path = os.path.join(KNOWN_FACES_DIR, safe_filename)
            
            # Write the image
            cv2.imwrite(save_path, cv2_img)

            st.success(f"✅ Successfully added **{student_name}** to the database!")
            
            # 4. CRITICAL: Clear the cache so the Main App reloads the new face!
            st.cache_resource.clear()
            st.info("The system has been updated. You can now go to the Main Page and take attendance.")

        except Exception as e:
            st.error(f"Error saving student: {e}")