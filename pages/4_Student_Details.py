import streamlit as st
import pandas as pd
import os
import sys
from datetime import date

# Add the main folder to the path (for login_system)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import auth # <--- Import auth

# --- LOGIN CHECK ---
if not auth.check_password():
    st.stop()
# --- CONFIGURATION ---
DETAILS_FILE = "student_details.csv"
KNOWN_FACES_DIR = "known_faces"

# Define your subjects and exam types exactly as requested
SUBJECTS = [
    "25ICMATT111", 
    "25ICCHET212", 
    "25ICBEET104", 
    "25ICATPT105", 
    "25ICVACP108", 
    "25ICFCTT103"
]

EXAMS = ["Internal", "CS1", "CS2", "Sem"]

st.set_page_config(page_title="Student Details", page_icon="📝", layout="wide")
st.title("📝 Student Details & Marks")

# --- 1. FUNCTION TO GET STUDENT NAMES ---
def get_student_list():
    if not os.path.exists(KNOWN_FACES_DIR):
        return []
    return [os.path.splitext(f)[0] for f in os.listdir(KNOWN_FACES_DIR) if f.endswith((".jpg", ".png", ".jpeg"))]

# --- 2. FUNCTION TO LOAD DATABASE (With Auto-Update for New Columns) ---
def load_data():
    # 1. Define ALL columns we need (Basic Info + 24 Mark columns)
    basic_cols = ["Name", "Address", "Contact", "Emergency_Contact", "Blood_Type", "DOB"]
    mark_cols = [f"{sub}_{exam}" for sub in SUBJECTS for exam in EXAMS]
    all_columns = basic_cols + mark_cols

    # 2. If file doesn't exist, create empty one
    if not os.path.exists(DETAILS_FILE):
        return pd.DataFrame(columns=all_columns)
    
    # 3. Load existing file
    df = pd.read_csv(DETAILS_FILE)
    
    # 4. CRITICAL: Add missing columns if they don't exist yet
    # (This prevents crashes when you update the app)
    for col in all_columns:
        if col not in df.columns:
            df[col] = 0 if "_" in col and "Contact" not in col else "" # Default marks to 0, text to empty

    df['DOB'] = df['DOB'].astype(str)
    return df

# --- 3. MAIN UI ---
all_students = get_student_list()
df = load_data()

if not all_students:
    st.warning("No students found! Go to 'Add Student' page first.")
    st.stop()

# Dropdown to select a student
selected_student = st.selectbox("Select Student to Edit", all_students)

# --- GET EXISTING DATA ---
student_data = df[df['Name'] == selected_student]

# Helper function to safely get a value
def get_val(column, default):
    if not student_data.empty and column in student_data.columns:
        val = student_data.iloc[0][column]
        # Check for NaN (empty) values and return default
        if pd.isna(val) or val == "nan": 
            return default
        return val
    return default

# Get Basic Info
current_address = get_val("Address", "")
current_contact = get_val("Contact", "")
current_emergency = get_val("Emergency_Contact", "")
current_blood = get_val("Blood_Type", "Unknown")
current_dob_str = get_val("DOB", "2000-01-01")

try:
    current_dob = date.fromisoformat(current_dob_str)
except ValueError:
    current_dob = date(2000, 1, 1)

# --- EDIT FORM ---
with st.form("details_form"):
    st.subheader(f"Editing: {selected_student}")
    
    # --- SECTION A: PERSONAL DETAILS ---
    with st.expander("👤 Personal Details", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            new_address = st.text_area("Home Address", value=current_address)
            new_dob = st.date_input("Date of Birth", value=current_dob)
            new_blood = st.selectbox("Blood Type", 
                                    ["Unknown", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], 
                                    index=["Unknown", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"].index(current_blood))
        with col2:
            new_contact = st.text_input("Contact Number", value=current_contact)
            new_emergency = st.text_input("Emergency Contact", value=current_emergency)

    # --- SECTION B: ACADEMIC MARKS ---
    st.markdown("### 📚 Academic Marks")
    
    # Create dictionary to hold the new marks
    new_marks = {}
    
    # Create Tabs for the 6 subjects
    tabs = st.tabs(SUBJECTS)

    # Loop through each tab (Subject) and create inputs
    for i, subject in enumerate(SUBJECTS):
        with tabs[i]:
            st.caption(f"Enter marks for **{subject}**")
            c1, c2, c3, c4 = st.columns(4)
            
            # Helper to create number inputs
            def create_input(col_obj, exam_name):
                col_name = f"{subject}_{exam_name}"
                current_mark = float(get_val(col_name, 0.0))
                # Store the input in our dictionary
                new_marks[col_name] = col_obj.number_input(f"{exam_name}", value=current_mark, min_value=0.0, max_value=100.0, key=col_name)

            create_input(c1, "Internal")
            create_input(c2, "CS1")
            create_input(c3, "CS2")
            create_input(c4, "Sem")

    # --- SAVE BUTTON ---
    st.write("") # Spacer
    submitted = st.form_submit_button("💾 Save All Details & Marks")

    if submitted:
        # 1. Collect Basic Data
        final_data = {
            "Name": selected_student,
            "Address": new_address,
            "Contact": new_contact,
            "Emergency_Contact": new_emergency,
            "Blood_Type": new_blood,
            "DOB": str(new_dob)
        }
        
        # 2. Add the Marks Data
        final_data.update(new_marks)
        
        # 3. Update DataFrame
        if selected_student in df['Name'].values:
            idx = df[df['Name'] == selected_student].index[0]
            # Update columns individually to avoid pandas warnings
            for key, value in final_data.items():
                df.at[idx, key] = value
        else:
            new_row = pd.DataFrame([final_data])
            df = pd.concat([df, new_row], ignore_index=True)
            
        # 4. Save to CSV
        df.to_csv(DETAILS_FILE, index=False)
        st.success(f"✅ Data for **{selected_student}** updated successfully!")
        st.rerun() # Refresh to show new data in table

# --- DISPLAY ALL DATA TABLE ---
st.divider()
st.subheader("📋 Class Database")
st.dataframe(df)