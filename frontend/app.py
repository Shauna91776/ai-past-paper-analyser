# Streamlit dashboard script (UI for uploads & stats)

import streamlit as st
import requests
import pandas as pd

API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="High-Yield Past Paper Analyzer",
    page_icon="📚",
    layout="wide"
)

st.title("📚 High-Yield Past Paper Analyzer")
st.markdown("Your local, privacy-focused exam revision assistant.")

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["📊 High-Yield Dashboard", "📤 Upload Past Paper", "⚙️ Manage Scopes"])

# --- PAGE 1: HIGH-YIELD DASHBOARD ---
if page == "📊 High-Yield Dashboard":
    st.header("High-Yield Topic Analytics")
    st.markdown("Topics ranked by cumulative mark allocations across all indexed past papers. Focus here first for maximum study returns!")

    try:
        response = requests.get(f"{API_BASE_URL}/analytics/high-yield")
        if response.status_code == 200:
            data = response.json()
            if not data:
                st.info("No past papers indexed yet! Head over to the 'Upload Past Paper' tab to get started.")
            else:
                df = pd.DataFrame(data)
                
                # Display metrics row
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Indexed Topics", len(df))
                with col2:
                    st.metric("Highest-Yield Topic", df.iloc[0]["topic_name"] if not df.empty else "N/A")
                with col3:
                    st.metric("Max Cumulative Marks", int(df["total_marks"].max()) if not df.empty else 0)

                st.markdown("---")
                
                # Display Bar Chart of Marks per Topic
                st.subheader("Mark Weighting Breakdown per Topic")
                chart_data = df.set_index("topic_name")[["total_marks"]]
                st.bar_chart(chart_data)

                # Display Data Table
                st.subheader("Detailed Topic Summary Table")
                st.dataframe(df, use_container_width=True)
        else:
            st.error("Could not fetch analytics from the backend. Make sure your FastAPI server is running!")
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Connection error: Could not reach the FastAPI backend at `http://localhost:8000`. Please start your server!")

# --- PAGE 2: UPLOAD PAST PAPER ---
elif page == "📤 Upload Past Paper":
    st.header("Upload & Parse Past Paper PDF")
    st.markdown("Upload a past exam paper. The local AI will automatically extract questions, marks, and map them to your active scope.")

    # Fetch existing subjects to populate dropdown
    try:
        scopes_resp = requests.get(f"{API_BASE_URL}/scopes/")
        scopes = scopes_resp.json() if scopes_resp.status_code == 200 else []
        subjects = list(set([s["subject_name"] for s in scopes]))
    except:
        subjects = []
        scopes = []

    with st.form("upload_form"):
        subject_name = st.selectbox("Subject Name", subjects if subjects else ["Mathematics", "Physics", "Computer Science"])
        term_or_grade = st.text_input("Term / Grade Level (e.g., Grade 9 Term 3)", "Grade 9 Exam")
        year = st.number_input("Exam Year", min_value=2000, max_value=2030, value=2026, step=1)
        
        uploaded_file = st.file_uploader("Upload Past Paper PDF", type=["pdf"])
        
        submit_button = st.form_submit_button("Parse & Index Paper")

    if submit_button:
        if not uploaded_file:
            st.warning("Please upload a PDF file first.")
        elif not scopes:
            st.warning("No curriculum scopes found in the database. Please add scopes in the 'Manage Scopes' tab first!")
        else:
            with st.spinner("🤖 AI is reading and parsing the past paper locally via Ollama... This may take a moment."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                params = {
                    "subject_name": subject_name,
                    "term_or_grade": term_or_grade,
                    "year": year
                }
                try:
                    res = requests.post(f"{API_BASE_URL}/papers/upload/", files=files, params=params)
                    if res.status_code == 200:
                        result_data = res.json()
                        st.success(f"🎉 Success! {result_data.get('message')}")
                        st.info(f"Indexed **{result_data.get('questions_indexed')}** questions from paper: *{result_data.get('paper_title')}*")
                    else:
                        st.error(f"Error parsing paper: {res.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Failed to connect to backend: {str(e)}")

# --- PAGE 3: MANAGE SCOPES ---
elif page == "⚙️ Manage Scopes":
    st.header("Manage Curriculum Scopes")
    st.markdown("Define your subject taxonomy so the AI knows exactly which topics are allowed during extraction.")

    # Display current scopes
    try:
        res = requests.get(f"{API_BASE_URL}/scopes/")
        current_scopes = res.json() if res.status_code == 200 else []
        if current_scopes:
            st.subheader("Current Active Scopes")
            st.dataframe(pd.DataFrame(current_scopes)[["id", "subject_name", "topic_name", "description"]], use_container_width=True)
        else:
            st.info("No scopes added yet. Add your first topic below!")
    except:
        st.warning("Could not load scopes from server.")

    st.markdown("---")
    st.subheader("Add New Curriculum Topic")
    
    with st.form("scope_form"):
        new_subject = st.text_input("Subject Name (e.g., Mathematics)")
        new_topic = st.text_input("Topic Name (e.g., Algebraic Expressions)")
        new_desc = st.text_area("Description / Sub-topics (Optional)")
        
        add_scope_btn = st.form_submit_button("Save Topic to Scope")
        
    if add_scope_btn:
        if not new_subject or not new_topic:
            st.warning("Please provide both a Subject Name and a Topic Name.")
        else:
            payload = {
                "subject_name": new_subject,
                "topic_name": new_topic,
                "description": new_desc
            }
            try:
                res = requests.post(f"{API_BASE_URL}/scopes/", json=payload)
                if res.status_code == 200:
                    st.success(f"Successfully added topic '{new_topic}' under '{new_subject}'!")
                    st.rerun()
                else:
                    st.error("Failed to add scope.")
            except Exception as e:
                st.error(f"Connection error: {str(e)}")