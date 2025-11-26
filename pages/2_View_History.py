import streamlit as st
import pandas as pd
import os
import auth # <--- Import auth

# --- LOGIN CHECK ---
if not auth.check_password():
    st.stop()
# --- CONFIGURATION ---
ATTENDANCE_FILE = "attendance_log.csv"

st.set_page_config(layout="wide")
st.title("📅 Attendance History")

# --- Check if the log file exists ---
if not os.path.exists(ATTENDANCE_FILE):
    st.error("No attendance has been logged yet. Take attendance from the main page first.")
else:
    # --- Load the data ---
    # We use a button to make sure we're always loading the most recent data
    if st.button("🔄 Refresh Data"):
        pass # Just re-runs the script

    df = pd.read_csv(ATTENDANCE_FILE)
    
    # Make sure 'Date' is a proper datetime object for filtering
    df['Date'] = pd.to_datetime(df['Date'])

    st.write("Here is the complete attendance log. Use the filters below to analyze it.")

    # --- 1. FILTERS ---
    st.header("🔍 Filter and Analyze")
    
    # Create columns for filters to sit side-by-side
    col1, col2 = st.columns(2)

    with col1:
        # Filter by Student Name (allow selecting multiple)
        all_students = sorted(df['Name'].unique())
        selected_students = st.multiselect("Select Students", all_students, default=all_students)

    with col2:
        # Filter by Date Range
        min_date = df['Date'].min()
        max_date = df['Date'].max()
        selected_date_range = st.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

    # --- 2. APPLY FILTERS ---
    
    # Make sure we have a valid date range (at least one day)
    if len(selected_date_range) == 2:
        start_date, end_date = selected_date_range
        
        # Filter the dataframe
        filtered_df = df[
            (df['Name'].isin(selected_students)) &
            (df['Date'] >= pd.to_datetime(start_date)) &
            (df['Date'] <= pd.to_datetime(end_date))
        ]

        # --- 3. DISPLAY RESULTS ---
        st.subheader("Filtered Attendance Data")
        st.dataframe(filtered_df)

        st.subheader("Attendance Summary")
        
        if not filtered_df.empty:
            # Calculate total days attended for each selected student
            summary = filtered_df[filtered_df['Status'] == 'Present'].groupby('Name').size().reset_index(name='Total Days Present')
            
            # Calculate total unique days in the log for the selected range
            total_days_logged = filtered_df['Date'].nunique()
            summary['Total Days Logged'] = total_days_logged
            
            summary['Attendance Percentage'] = ((summary['Total Days Present'] / summary['Total Days Logged']) * 100).round(1)
            
            st.dataframe(summary.set_index('Name'))
            
            # Show a bar chart
            st.bar_chart(summary, x='Name', y='Total Days Present')

        else:
            st.warning("No data found for the selected filters.")
    else:
        st.warning("Please select a valid date range (start and end date).")