import streamlit as st
import pandas as pd
import io
import base64
import os
import re
from datetime import datetime
import hashlib

# Document text extraction
try:
    import pdfplumber
except ImportError:
    pdfplumber = None
try:
    import docx2txt
except ImportError:
    docx2txt = None

st.set_page_config(
    page_title="Applicant CV Screening – Gesner Deslandes",
    page_icon="👔",
    layout="wide"
)

# ---------- Custom CSS with spinning symbols ----------
st.markdown(
    """
    <style>
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    .spinning-recruit {
        animation: spin 4s linear infinite;
        font-size: 60px;
        text-align: center;
        margin-bottom: 20px;
    }
    .stApp {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0b2b2b, #1a4a4a);
    }
    .stButton button {
        background-color: #ff6b6b !important;
        color: white !important;
        border-radius: 30px !important;
        font-weight: bold;
    }
    h1, h2, h3, p, div, span, label {
        color: #ffffff !important;
    }
    .job-card {
        background: rgba(255,255,255,0.1);
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 5px solid #ff9a3c;
    }
    .score-high {
        color: #a5ffb2;
        font-weight: bold;
    }
    .score-medium {
        color: #ffd966;
        font-weight: bold;
    }
    .score-low {
        color: #ff8a8a;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- Session State ----------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "job_positions" not in st.session_state:
    # Load sample data if empty
    st.session_state.job_positions = pd.DataFrame({
        "id": [1, 2],
        "title": ["Senior Python Developer", "Data Scientist"],
        "description": ["Build web apps with Streamlit", "Analyse data and build ML models"],
        "required_skills": ["Python,Streamlit,API", "Python,SQL,Machine Learning"],
        "min_experience": [3, 2]
    })
if "applications" not in st.session_state:
    st.session_state.applications = pd.DataFrame(columns=["applicant_name", "email", "job_title", "score", "cv_text_preview", "date"])

# Helper functions for CV text extraction
def extract_text_from_pdf(file_bytes):
    if pdfplumber is None:
        return "PDF extraction not available. Please install pdfplumber."
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    except:
        return ""

def extract_text_from_docx(file_bytes):
    if docx2txt is None:
        return "DOCX extraction not available. Please install docx2txt."
    try:
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name
        text = docx2txt.process(tmp_path)
        os.unlink(tmp_path)
        return text
    except:
        return ""

def extract_text_from_txt(file_bytes):
    try:
        return file_bytes.decode("utf-8")
    except:
        return ""

def extract_cv_text(uploaded_file):
    file_bytes = uploaded_file.read()
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(file_bytes)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(file_bytes)
    elif uploaded_file.type == "text/plain":
        return extract_text_from_txt(file_bytes)
    else:
        return "Unsupported file type."

def compute_match_score(cv_text, job_skills, job_description):
    cv_lower = cv_text.lower()
    skills_list = [s.strip().lower() for s in job_skills.split(",")]
    matches = 0
    for skill in skills_list:
        if skill in cv_lower:
            matches += 1
    skill_score = (matches / len(skills_list)) * 100 if skills_list else 50
    # Also check description keywords
    desc_keywords = re.findall(r'\b\w{4,}\b', job_description.lower())
    desc_matches = sum(1 for kw in desc_keywords if kw in cv_lower)
    desc_score = (desc_matches / max(len(desc_keywords), 1)) * 100
    overall = (skill_score * 0.7 + desc_score * 0.3)
    return round(overall, 2)

# ---------- Login Page ----------
def login():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="spinning-recruit">👔</div>', unsafe_allow_html=True)
        st.title("📄 Applicant CV Screening")
        st.markdown("### Job Position Qualification Recruitment")
        st.markdown("Built by **Gesner Deslandes**")
        st.markdown("---")
        password = st.text_input("Enter Admin Password", type="password")
        if st.button("🔓 Unlock System"):
            if password == "20082010":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password. Access denied.")

# ---------- Main App ----------
def main_app():
    # Sidebar with your info
    with st.sidebar:
        st.markdown('<div style="text-align:center; font-size:50px; animation: spin 4s linear infinite;">🌍</div>', unsafe_allow_html=True)
        st.markdown("### GlobalInternet.py")
        st.markdown("**Gesner Deslandes** – Engineer in Chief, Founder")
        st.markdown("---")
        st.markdown("📧 deslandes78@gmail.com")
        st.markdown("📞 (509) 4738-5663")
        st.markdown("[🌐 Website](https://globalinternetsitepy-abh7v6tnmskxxnuplrdcgk.streamlit.app/)")
        st.markdown("---")
        st.markdown("**Recruitment Tool v1.0**")
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.rerun()

    st.markdown('<div class="spinning-recruit" style="font-size:40px;">👔 📄 👔</div>', unsafe_allow_html=True)
    st.title("Applicant CV Screening Software")
    st.markdown("### Professional Recruitment & Qualification Analysis")
    st.markdown("---")

    tabs = st.tabs(["📌 Job Positions", "📝 Screen CV", "📊 Applications", "📧 Email Integration"])

    # ---------- Job Positions Management ----------
    with tabs[0]:
        st.subheader("Manage Job Positions")
        col1, col2 = st.columns([2,1])
        with col1:
            with st.expander("➕ Add New Position"):
                new_title = st.text_input("Job Title")
                new_desc = st.text_area("Job Description")
                new_skills = st.text_input("Required Skills (comma separated)", placeholder="e.g., Python,Streamlit,SQL")
                new_exp = st.number_input("Minimum Experience (years)", min_value=0, step=1)
                if st.button("Add Position"):
                    if new_title and new_desc:
                        new_id = len(st.session_state.job_positions) + 1
                        new_row = pd.DataFrame({
                            "id": [new_id],
                            "title": [new_title],
                            "description": [new_desc],
                            "required_skills": [new_skills],
                            "min_experience": [new_exp]
                        })
                        st.session_state.job_positions = pd.concat([st.session_state.job_positions, new_row], ignore_index=True)
                        st.success(f"Position '{new_title}' added.")
                        st.rerun()
        with col2:
            st.markdown("#### Current Positions")
            if len(st.session_state.job_positions) > 0:
                for idx, row in st.session_state.job_positions.iterrows():
                    with st.container():
                        st.markdown(f'<div class="job-card"><strong>{row["title"]}</strong><br>{row["description"]}<br>🎯 Skills: {row["required_skills"]}<br>⏱️ Min exp: {row["min_experience"]} yrs</div>', unsafe_allow_html=True)
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button(f"✏️ Edit", key=f"edit_{row['id']}"):
                                st.session_state.edit_id = row['id']
                                st.session_state.edit_title = row['title']
                                st.session_state.edit_desc = row['description']
                                st.session_state.edit_skills = row['required_skills']
                                st.session_state.edit_exp = row['min_experience']
                        with col_b:
                            if st.button(f"🗑️ Delete", key=f"del_{row['id']}"):
                                st.session_state.job_positions = st.session_state.job_positions[st.session_state.job_positions['id'] != row['id']]
                                st.rerun()
                # Edit form if edit_id exists
                if 'edit_id' in st.session_state:
                    st.markdown("---")
                    st.subheader(f"Editing: {st.session_state.edit_title}")
                    new_title = st.text_input("Title", value=st.session_state.edit_title)
                    new_desc = st.text_area("Description", value=st.session_state.edit_desc)
                    new_skills = st.text_input("Skills", value=st.session_state.edit_skills)
                    new_exp = st.number_input("Experience", value=int(st.session_state.edit_exp))
                    if st.button("Save Changes"):
                        idx = st.session_state.job_positions[st.session_state.job_positions['id'] == st.session_state.edit_id].index[0]
                        st.session_state.job_positions.at[idx, 'title'] = new_title
                        st.session_state.job_positions.at[idx, 'description'] = new_desc
                        st.session_state.job_positions.at[idx, 'required_skills'] = new_skills
                        st.session_state.job_positions.at[idx, 'min_experience'] = new_exp
                        del st.session_state.edit_id
                        st.rerun()
            else:
                st.info("No job positions yet. Add one above.")

    # ---------- Screen CV ----------
    with tabs[1]:
        st.subheader("Applicant CV Screening")
        st.markdown("Upload a CV and select a job position to analyse qualification.")
        applicant_name = st.text_input("Applicant Full Name")
        applicant_email = st.text_input("Applicant Email")
        uploaded_cv = st.file_uploader("Upload CV (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
        job_options = st.session_state.job_positions['title'].tolist()
        selected_job = st.selectbox("Select Job Position", job_options) if job_options else None
        
        if st.button("🔍 Analyse CV") and uploaded_cv and applicant_name and selected_job:
            with st.spinner("Extracting text and matching..."):
                cv_text = extract_cv_text(uploaded_cv)
                if cv_text and len(cv_text) > 50:
                    job_row = st.session_state.job_positions[st.session_state.job_positions['title'] == selected_job].iloc[0]
                    score = compute_match_score(cv_text, job_row['required_skills'], job_row['description'])
                    # Store application
                    new_app = pd.DataFrame({
                        "applicant_name": [applicant_name],
                        "email": [applicant_email],
                        "job_title": [selected_job],
                        "score": [score],
                        "cv_text_preview": [cv_text[:500] + "..."],
                        "date": [datetime.now().strftime("%Y-%m-%d %H:%M")]
                    })
                    st.session_state.applications = pd.concat([st.session_state.applications, new_app], ignore_index=True)
                    # Show result
                    st.success(f"Analysis complete! Match score: {score}%")
                    if score >= 70:
                        st.markdown(f'<p class="score-high">✅ Highly qualified – Score: {score}%</p>', unsafe_allow_html=True)
                    elif score >= 50:
                        st.markdown(f'<p class="score-medium">⚠️ Partially qualified – Score: {score}%</p>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<p class="score-low">❌ Low match – Score: {score}%</p>', unsafe_allow_html=True)
                    # Option to send email (simulate)
                    st.info(f"Application recorded. An email notification would be sent to {applicant_email} and admin (deslandes78@gmail.com).")
                else:
                    st.error("Could not extract text from CV. Please ensure file is not empty and format is supported.")
        elif not selected_job:
            st.warning("Please add job positions first.")

    # ---------- Applications List ----------
    with tabs[2]:
        st.subheader("All Applications")
        if len(st.session_state.applications) > 0:
            st.dataframe(st.session_state.applications[["applicant_name", "email", "job_title", "score", "date"]], use_container_width=True)
            # Download CSV
            csv = st.session_state.applications.to_csv(index=False)
            st.download_button("📥 Download Applications CSV", data=csv, file_name="applications.csv")
            # View details
            selected_app = st.selectbox("View full CV preview", st.session_state.applications['applicant_name'].tolist())
            app_row = st.session_state.applications[st.session_state.applications['applicant_name'] == selected_app].iloc[0]
            st.text_area("CV Text Preview", app_row['cv_text_preview'], height=200)
        else:
            st.info("No applications yet. Screen some CVs.")

    # ---------- Email Integration Info ----------
    with tabs[3]:
        st.subheader("📧 Email Integration")
        st.markdown("""
        **How to receive CVs by email:**  
        Applicants can send their CV and details directly to:  
        `deslandes78@gmail.com`  
        
        **To automatically screen emails:**  
        - This software currently accepts CV uploads directly.  
        - For full email integration (IMAP), an advanced version can be built to fetch emails from a dedicated mailbox and auto‑screen attachments.  
        
        **Note:** All uploaded CVs are stored in the system and can be reviewed in the **Applications** tab.  
        
        *For inquiries about custom email integration, contact the developer.*
        """)
        st.info("📩 Admin email: deslandes78@gmail.com | Applicant submissions via this portal are immediately screened.")

if not st.session_state.authenticated:
    login()
else:
    main_app()
