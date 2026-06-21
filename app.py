import streamlit as st
import pandas as pd
import io
import os
import re
from datetime import datetime
import hashlib
import requests
import json
import base64
from pathlib import Path

# Document text extraction
try:
    import pdfplumber
except ImportError:
    pdfplumber = None
try:
    import docx2txt
except ImportError:
    docx2txt = None

# Groq AI
try:
    from groq import Groq
except ImportError:
    Groq = None

# Supabase
try:
    from supabase import create_client, Client
except ImportError:
    Client = None

# Text-to-Speech (gTTS)
try:
    from gtts import gTTS
except ImportError:
    gTTS = None

# Translation
try:
    from googletrans import Translator
except ImportError:
    Translator = None

st.set_page_config(
    page_title="Applicant CV Screening – Gesner Deslandes",
    page_icon="👔",
    layout="wide"
)

# ---------- Translation Dictionary ----------
TRANSLATIONS = {
    "en": {
        "app_title": "Applicant CV Screening Software",
        "app_subtitle": "Professional Recruitment & Qualification Analysis",
        "job_positions": "📌 Job Positions",
        "screen_cv": "📝 Screen CV",
        "applications": "📊 Applications",
        "email_integration": "📧 Email Integration",
        "bulk_screening": "📋 Bulk Screening",
        "manage_jobs": "Manage Job Positions",
        "add_position": "➕ Add New Position",
        "job_title": "Job Title",
        "job_description": "Job Description",
        "required_skills": "Required Skills (comma separated)",
        "min_experience": "Minimum Experience (years)",
        "add_position_btn": "Add Position",
        "current_positions": "Current Positions",
        "edit": "✏️ Edit",
        "delete": "🗑️ Delete",
        "save_changes": "Save Changes",
        "applicant_name": "Applicant Full Name",
        "applicant_email": "Applicant Email",
        "upload_cv": "Upload CV (PDF, DOCX, TXT)",
        "select_job": "Select Job Position",
        "analyze_cv": "🔍 Analyse CV",
        "highly_qualified": "✅ Highly qualified",
        "partially_qualified": "⚠️ Partially qualified",
        "low_match": "❌ Low match",
        "all_applications": "All Applications",
        "download_csv": "📥 Download Applications CSV",
        "view_cv_preview": "View full CV preview",
        "cv_text_preview": "CV Text Preview",
        "email_integration_desc": "📧 Email Integration",
        "admin_email": "📩 Admin email: deslandes78@gmail.com | Applicant submissions via this portal are immediately screened.",
        "ai_voice": "🔊 AI Voice",
        "voice_language": "Voice Language",
        "speak_text": "🔊 Speak Text",
        "speak_acceptance": "📢 Read Acceptance Email",
        "translate_language": "🌐 Translate App Language",
        "translate_btn": "Translate",
        "ai_email_generator": "📧 AI Email Generator",
        "generate_email": "📝 Generate Acceptance Email",
        "copy_email": "📋 Copy to Clipboard",
        "send_email": "📤 Send Email",
        "email_api_key": "🔑 Email API Key (SendGrid)",
        "recipient_email": "Recipient Email",
        "subject": "Subject",
        "email_body": "Email Body",
        "select_all": "Select All",
        "bulk_upload": "📂 Upload Multiple CVs (Up to 10)",
        "bulk_analyze": "🔍 Analyze All CVs",
        "candidate": "Candidate",
        "match_score": "Match Score",
        "status": "Status",
        "actions": "Actions",
        "no_cv": "No CV uploaded yet.",
        "no_jobs": "Please add job positions first.",
        "recording": "Recording application..."
    },
    "fr": {
        "app_title": "Logiciel de Criblage de CV",
        "app_subtitle": "Recrutement Professionnel & Analyse de Qualification",
        "job_positions": "📌 Postes",
        "screen_cv": "📝 Cribler un CV",
        "applications": "📊 Candidatures",
        "email_integration": "📧 Intégration Email",
        "bulk_screening": "📋 Criblage en Masse",
        "manage_jobs": "Gérer les Postes",
        "add_position": "➕ Ajouter un Poste",
        "job_title": "Titre du Poste",
        "job_description": "Description du Poste",
        "required_skills": "Compétences Requises (séparées par des virgules)",
        "min_experience": "Expérience Minimale (années)",
        "add_position_btn": "Ajouter le Poste",
        "current_positions": "Postes Actuels",
        "edit": "✏️ Modifier",
        "delete": "🗑️ Supprimer",
        "save_changes": "Enregistrer les Modifications",
        "applicant_name": "Nom Complet du Candidat",
        "applicant_email": "Email du Candidat",
        "upload_cv": "Télécharger le CV (PDF, DOCX, TXT)",
        "select_job": "Sélectionner le Poste",
        "analyze_cv": "🔍 Analyser le CV",
        "highly_qualified": "✅ Hautement qualifié",
        "partially_qualified": "⚠️ Partiellement qualifié",
        "low_match": "❌ Faible correspondance",
        "all_applications": "Toutes les Candidatures",
        "download_csv": "📥 Télécharger les Candidatures (CSV)",
        "view_cv_preview": "Voir l'aperçu du CV",
        "cv_text_preview": "Aperçu du CV",
        "email_integration_desc": "📧 Intégration Email",
        "admin_email": "📩 Email admin : deslandes78@gmail.com | Les soumissions sont immédiatement analysées.",
        "ai_voice": "🔊 Voix IA",
        "voice_language": "Langue de la Voix",
        "speak_text": "🔊 Lire le Texte",
        "speak_acceptance": "📢 Lire l'Email d'Acceptation",
        "translate_language": "🌐 Traduire l'Application",
        "translate_btn": "Traduire",
        "ai_email_generator": "📧 Générateur d'Email IA",
        "generate_email": "📝 Générer l'Email d'Acceptation",
        "copy_email": "📋 Copier",
        "send_email": "📤 Envoyer l'Email",
        "email_api_key": "🔑 Clé API Email (SendGrid)",
        "recipient_email": "Email du Destinataire",
        "subject": "Sujet",
        "email_body": "Corps de l'Email",
        "select_all": "Tout Sélectionner",
        "bulk_upload": "📂 Télécharger plusieurs CVs (jusqu'à 10)",
        "bulk_analyze": "🔍 Analyser tous les CVs",
        "candidate": "Candidat",
        "match_score": "Score de Correspondance",
        "status": "Statut",
        "actions": "Actions",
        "no_cv": "Aucun CV téléchargé.",
        "no_jobs": "Veuillez d'abord ajouter des postes.",
        "recording": "Enregistrement de la candidature..."
    },
    "es": {
        "app_title": "Software de Cribado de CV",
        "app_subtitle": "Reclutamiento Profesional y Análisis de Calificación",
        "job_positions": "📌 Puestos",
        "screen_cv": "📝 Evaluar CV",
        "applications": "📊 Solicitudes",
        "email_integration": "📧 Integración de Correo",
        "bulk_screening": "📋 Evaluación Masiva",
        "manage_jobs": "Gestionar Puestos",
        "add_position": "➕ Añadir Puesto",
        "job_title": "Título del Puesto",
        "job_description": "Descripción del Puesto",
        "required_skills": "Habilidades Requeridas (separadas por comas)",
        "min_experience": "Experiencia Mínima (años)",
        "add_position_btn": "Añadir Puesto",
        "current_positions": "Puestos Actuales",
        "edit": "✏️ Editar",
        "delete": "🗑️ Eliminar",
        "save_changes": "Guardar Cambios",
        "applicant_name": "Nombre Completo del Candidato",
        "applicant_email": "Correo del Candidato",
        "upload_cv": "Subir CV (PDF, DOCX, TXT)",
        "select_job": "Seleccionar Puesto",
        "analyze_cv": "🔍 Analizar CV",
        "highly_qualified": "✅ Altamente calificado",
        "partially_qualified": "⚠️ Parcialmente calificado",
        "low_match": "❌ Baja coincidencia",
        "all_applications": "Todas las Solicitudes",
        "download_csv": "📥 Descargar Solicitudes (CSV)",
        "view_cv_preview": "Ver vista previa del CV",
        "cv_text_preview": "Vista previa del CV",
        "email_integration_desc": "📧 Integración de Correo Electrónico",
        "admin_email": "📩 Correo admin: deslandes78@gmail.com | Las solicitudes se analizan inmediatamente.",
        "ai_voice": "🔊 Voz IA",
        "voice_language": "Idioma de la Voz",
        "speak_text": "🔊 Leer Texto",
        "speak_acceptance": "📢 Leer Correo de Aceptación",
        "translate_language": "🌐 Traducir Aplicación",
        "translate_btn": "Traducir",
        "ai_email_generator": "📧 Generador de Correo IA",
        "generate_email": "📝 Generar Correo de Aceptación",
        "copy_email": "📋 Copiar",
        "send_email": "📤 Enviar Correo",
        "email_api_key": "🔑 Clave API de Correo (SendGrid)",
        "recipient_email": "Correo del Destinatario",
        "subject": "Asunto",
        "email_body": "Cuerpo del Correo",
        "select_all": "Seleccionar Todo",
        "bulk_upload": "📂 Subir Múltiples CVs (Hasta 10)",
        "bulk_analyze": "🔍 Analizar Todos los CVs",
        "candidate": "Candidato",
        "match_score": "Puntuación de Coincidencia",
        "status": "Estado",
        "actions": "Acciones",
        "no_cv": "No se ha subido ningún CV.",
        "no_jobs": "Por favor, añade puestos primero.",
        "recording": "Registrando solicitud..."
    },
    "zh": {
        "app_title": "简历筛选软件",
        "app_subtitle": "专业招聘与资格分析",
        "job_positions": "📌 职位管理",
        "screen_cv": "📝 简历筛选",
        "applications": "📊 申请记录",
        "email_integration": "📧 邮件集成",
        "bulk_screening": "📋 批量筛选",
        "manage_jobs": "管理职位",
        "add_position": "➕ 添加新职位",
        "job_title": "职位名称",
        "job_description": "职位描述",
        "required_skills": "所需技能（逗号分隔）",
        "min_experience": "最低经验（年）",
        "add_position_btn": "添加职位",
        "current_positions": "当前职位",
        "edit": "✏️ 编辑",
        "delete": "🗑️ 删除",
        "save_changes": "保存更改",
        "applicant_name": "申请人全名",
        "applicant_email": "申请人邮箱",
        "upload_cv": "上传简历（PDF， DOCX， TXT）",
        "select_job": "选择职位",
        "analyze_cv": "🔍 分析简历",
        "highly_qualified": "✅ 高度符合",
        "partially_qualified": "⚠️ 部分符合",
        "low_match": "❌ 匹配度低",
        "all_applications": "所有申请",
        "download_csv": "📥 下载申请记录（CSV）",
        "view_cv_preview": "查看简历预览",
        "cv_text_preview": "简历文本预览",
        "email_integration_desc": "📧 邮件集成",
        "admin_email": "📩 管理员邮箱：deslandes78@gmail.com | 申请将立即被筛选。",
        "ai_voice": "🔊 AI 语音",
        "voice_language": "语音语言",
        "speak_text": "🔊 朗读文本",
        "speak_acceptance": "📢 朗读录用邮件",
        "translate_language": "🌐 翻译应用语言",
        "translate_btn": "翻译",
        "ai_email_generator": "📧 AI 邮件生成器",
        "generate_email": "📝 生成录用邮件",
        "copy_email": "📋 复制到剪贴板",
        "send_email": "📤 发送邮件",
        "email_api_key": "🔑 邮件 API 密钥（SendGrid）",
        "recipient_email": "收件人邮箱",
        "subject": "主题",
        "email_body": "邮件正文",
        "select_all": "全选",
        "bulk_upload": "📂 上传多个简历（最多10个）",
        "bulk_analyze": "🔍 分析所有简历",
        "candidate": "候选人",
        "match_score": "匹配分数",
        "status": "状态",
        "actions": "操作",
        "no_cv": "尚未上传简历。",
        "no_jobs": "请先添加职位。",
        "recording": "正在记录申请..."
    }
}

# ---------- Initialize API Clients ----------
def init_groq_client():
    try:
        api_key = st.secrets.get("GROQ_API_KEY")
        if Groq and api_key:
            return Groq(api_key=api_key)
    except:
        pass
    return None

def init_supabase_client():
    try:
        url = st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_ANON_KEY")
        if Client and url and key:
            return create_client(url, key)
    except:
        pass
    return None

def get_global_surveillance_key():
    try:
        return st.secrets.get("GLOBAL_SURVEILLANCE_KEY")
    except:
        return None

def get_email_api_key():
    try:
        return st.secrets.get("EMAIL_API_KEY")
    except:
        return None

groq_client = init_groq_client()
supabase_client = init_supabase_client()
global_surveillance_key = get_global_surveillance_key()
email_api_key = get_email_api_key()

# ---------- Session State ----------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "language" not in st.session_state:
    st.session_state.language = "en"
if "voice_language" not in st.session_state:
    st.session_state.voice_language = "en"
if "ai_email_body" not in st.session_state:
    st.session_state.ai_email_body = ""
if "bulk_results" not in st.session_state:
    st.session_state.bulk_results = []

# Load data from Supabase or session state
def load_job_positions():
    if supabase_client:
        try:
            response = supabase_client.table("job_positions").select("*").execute()
            if response.data:
                return pd.DataFrame(response.data)
        except:
            pass
    return st.session_state.get("job_positions", pd.DataFrame({
        "id": [1, 2],
        "title": ["Senior Python Developer", "Data Scientist"],
        "description": ["Build web apps with Streamlit", "Analyse data and build ML models"],
        "required_skills": ["Python,Streamlit,API", "Python,SQL,Machine Learning"],
        "min_experience": [3, 2]
    }))

def load_applications():
    if supabase_client:
        try:
            response = supabase_client.table("applications").select("*").execute()
            if response.data:
                return pd.DataFrame(response.data)
        except:
            pass
    return st.session_state.get("applications", pd.DataFrame(columns=["applicant_name", "email", "job_title", "score", "cv_text_preview", "date"]))

if "job_positions" not in st.session_state:
    st.session_state.job_positions = load_job_positions()
if "applications" not in st.session_state:
    st.session_state.applications = load_applications()

# ---------- Helper Functions ----------
def t(key):
    """Translate a key based on current language."""
    translations = TRANSLATIONS.get(st.session_state.language, TRANSLATIONS["en"])
    return translations.get(key, key)

def extract_text_from_pdf(file_bytes):
    if pdfplumber is None:
        return "PDF extraction not available."
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
        return "DOCX extraction not available."
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
    desc_keywords = re.findall(r'\b\w{4,}\b', job_description.lower())
    desc_matches = sum(1 for kw in desc_keywords if kw in cv_lower)
    desc_score = (desc_matches / max(len(desc_keywords), 1)) * 100
    overall = (skill_score * 0.7 + desc_score * 0.3)
    return round(overall, 2)

def analyze_cv_with_groq(cv_text, job_title, job_description, job_skills):
    if not groq_client:
        return None, None, None, None

    prompt = f"""
    You are an expert HR recruiter. Analyze the following CV against the job requirements.

    Job Title: {job_title}
    Job Description: {job_description}
    Required Skills: {job_skills}

    CV Text:
    {cv_text[:3000]}

    Provide your analysis in JSON format:
    {{
        "match_score": 85,
        "summary": "Brief 2-3 sentence summary of the candidate's fit",
        "strengths": ["Strength 1", "Strength 2"],
        "weaknesses": ["Weakness 1", "Weakness 2"],
        "recommendation": "Interview"
    }}
    """

    try:
        response = groq_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "You are an expert HR recruiter. Respond only in valid JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)
        return (
            result.get("match_score", 50),
            result.get("summary", "Analysis completed."),
            result.get("strengths", []),
            result.get("weaknesses", [])
        )
    except:
        return None, None, None, None

def generate_acceptance_email(cv_text, job_title, score, strengths, weaknesses):
    """Generate an acceptance email using Groq AI."""
    if not groq_client:
        # Fallback email template
        return f"""
Subject: Congratulations! You have been selected for {job_title}

Dear Candidate,

We are pleased to inform you that after carefully reviewing your application, we have decided to move forward with your candidacy for the position of {job_title}.

Your CV demonstrates strong alignment with our requirements, with a match score of {score}%.

Our hiring team was particularly impressed with your experience and skills.

We would like to invite you for the next stage of our recruitment process.

Best regards,
The Hiring Management Team
GlobalInternet.py
"""

    prompt = f"""
    Generate a professional acceptance email to be sent to a candidate who has been selected for an interview.

    Job Title: {job_title}
    Match Score: {score}%
    Candidate Strengths: {', '.join(strengths) if strengths else 'Strong qualifications'}
    Areas for Improvement: {', '.join(weaknesses) if weaknesses else 'None significant'}

    CV Text (excerpt):
    {cv_text[:1000]}

    The email should:
    1. Congratulate the candidate
    2. Mention their match score
    3. Reference their key strengths
    4. Invite them to the next stage (interview or further discussion)
    5. Be signed by "The Hiring Management Team"
    6. Be warm and professional

    Format as a complete email with Subject, Salutation, Body, and Closing.
    """

    try:
        response = groq_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "You are an HR professional. Generate a warm, professional acceptance email."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=600
        )
        return response.choices[0].message.content
    except:
        return """
Subject: Congratulations! You have been selected for {job_title}

Dear Candidate,

We are pleased to inform you that after carefully reviewing your application, we have decided to move forward with your candidacy for the position of {job_title}.

Your CV demonstrates strong alignment with our requirements. Our hiring team was impressed with your qualifications.

We would like to invite you for the next stage of our recruitment process.

Best regards,
The Hiring Management Team
GlobalInternet.py
"""

def check_email_breach(email):
    if not global_surveillance_key:
        return None, "Global Surveillance API key not configured."
    try:
        # Replace with actual endpoint
        url = "https://api.globalsurveillance.com/v1/breach-check"
        headers = {"Authorization": f"Bearer {global_surveillance_key}", "Content-Type": "application/json"}
        payload = {"email": email}
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            breaches = data.get("breaches", [])
            if breaches:
                return True, f"⚠️ Found in {len(breaches)} breach(es)."
            else:
                return False, "✅ No breaches found."
        else:
            return None, f"API error: {response.status_code}"
    except:
        return None, "Error checking breach."

def save_to_supabase(table, data):
    if not supabase_client:
        return False
    try:
        supabase_client.table(table).insert(data).execute()
        return True
    except:
        return False

def text_to_speech(text, lang):
    """Generate audio from text using gTTS."""
    if not gTTS:
        return None
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes
    except:
        return None

def send_email_with_sendgrid(api_key, to_email, subject, body):
    """Send email using SendGrid API."""
    try:
        url = "https://api.sendgrid.com/v3/mail/send"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "personalizations": [{"to": [{"email": to_email}]}],
            "from": {"email": "deslandes78@gmail.com"},
            "subject": subject,
            "content": [{"type": "text/plain", "value": body}]
        }
        response = requests.post(url, json=data, headers=headers, timeout=30)
        return response.status_code == 202
    except:
        return False

# ---------- Login Page ----------
def login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="spinning-recruit">👔</div>', unsafe_allow_html=True)
        st.title(t("app_title"))
        st.markdown(f"### {t('app_subtitle')}")
        st.markdown("Built by **Gesner Deslandes**")

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if groq_client:
                st.success("🤖 Groq: ✅")
            else:
                st.warning("🤖 Groq: ❌")
        with col_b:
            if supabase_client:
                st.success("🗄️ Supabase: ✅")
            else:
                st.warning("🗄️ Supabase: ❌")
        with col_c:
            if global_surveillance_key:
                st.success("🛡️ GlobalSurv: ✅")
            else:
                st.warning("🛡️ GlobalSurv: ❌")

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
    # ---------- Sidebar ----------
    with st.sidebar:
        st.markdown('<div style="text-align:center; font-size:50px; animation: spin 4s linear infinite;">🌍</div>', unsafe_allow_html=True)
        st.markdown("### GlobalInternet.py")
        st.markdown("**Gesner Deslandes** – Engineer in Chief, Founder")
        st.markdown("---")

        # Language Selection
        st.markdown("### 🌐 Language Settings")
        lang_map = {"English": "en", "Français": "fr", "Español": "es", "中文": "zh"}
        selected_lang_display = st.selectbox(
            t("translate_language"),
            list(lang_map.keys()),
            index=list(lang_map.values()).index(st.session_state.language)
        )
        st.session_state.language = lang_map[selected_lang_display]

        st.markdown("---")

        # AI Voice Section
        st.markdown(f"### {t('ai_voice')}")
        voice_lang_map = {"English": "en", "Français": "fr", "Español": "es", "中文": "zh"}
        selected_voice = st.selectbox(
            t("voice_language"),
            list(voice_lang_map.keys()),
            index=list(voice_lang_map.values()).index(st.session_state.voice_language)
        )
        st.session_state.voice_language = voice_lang_map[selected_voice]

        voice_text = st.text_area("Text to Speak", "Welcome to GlobalInternet.py recruitment system.", height=80)
        if st.button(t("speak_text")):
            audio = text_to_speech(voice_text, st.session_state.voice_language)
            if audio:
                st.audio(audio, format="audio/mp3")
            else:
                st.error("gTTS not installed. Please run: pip install gTTS")

        if st.button(t("speak_acceptance")):
            if st.session_state.ai_email_body:
                audio = text_to_speech(st.session_state.ai_email_body[:500], st.session_state.voice_language)
                if audio:
                    st.audio(audio, format="audio/mp3")
                else:
                    st.error("gTTS not installed.")
            else:
                st.warning("Generate an acceptance email first.")

        st.markdown("---")

        # Email API Key
        st.markdown(f"### {t('email_api_key')}")
        email_api_input = st.text_input("SendGrid API Key", type="password", value=email_api_key or "")
        if email_api_input:
            st.success("✅ API Key Set")

        st.markdown("---")
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.rerun()

    # ---------- Main Content ----------
    st.markdown('<div class="spinning-recruit" style="font-size:40px;">👔 📄 👔</div>', unsafe_allow_html=True)
    st.title(t("app_title"))
    st.markdown(f"### {t('app_subtitle')}")
    st.markdown("---")

    # Add Bulk Screening tab
    tabs = st.tabs([
        t("job_positions"),
        t("screen_cv"),
        t("applications"),
        t("email_integration"),
        t("bulk_screening")
    ])

    # ---------- Job Positions Management ----------
    with tabs[0]:
        st.subheader(t("manage_jobs"))
        col1, col2 = st.columns([2, 1])
        with col1:
            with st.expander(t("add_position")):
                new_title = st.text_input(t("job_title"))
                new_desc = st.text_area(t("job_description"))
                new_skills = st.text_input(t("required_skills"), placeholder="e.g., Python,Streamlit,SQL")
                new_exp = st.number_input(t("min_experience"), min_value=0, step=1)
                if st.button(t("add_position_btn")):
                    if new_title and new_desc:
                        new_id = len(st.session_state.job_positions) + 1
                        new_row = {
                            "id": new_id,
                            "title": new_title,
                            "description": new_desc,
                            "required_skills": new_skills,
                            "min_experience": new_exp
                        }
                        if supabase_client:
                            save_to_supabase("job_positions", new_row)
                        st.session_state.job_positions = pd.concat([
                            st.session_state.job_positions,
                            pd.DataFrame([new_row])
                        ], ignore_index=True)
                        st.success(f"Position '{new_title}' added.")
                        st.rerun()
        with col2:
            st.markdown(f"#### {t('current_positions')}")
            if len(st.session_state.job_positions) > 0:
                for idx, row in st.session_state.job_positions.iterrows():
                    with st.container():
                        st.markdown(f'<div class="job-card"><strong>{row["title"]}</strong><br>{row["description"]}<br>🎯 Skills: {row["required_skills"]}<br>⏱️ Min exp: {row["min_experience"]} yrs</div>', unsafe_allow_html=True)
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button(t("edit"), key=f"edit_{row['id']}"):
                                st.session_state.edit_id = row['id']
                                st.session_state.edit_title = row['title']
                                st.session_state.edit_desc = row['description']
                                st.session_state.edit_skills = row['required_skills']
                                st.session_state.edit_exp = row['min_experience']
                        with col_b:
                            if st.button(t("delete"), key=f"del_{row['id']}"):
                                if supabase_client:
                                    supabase_client.table("job_positions").delete().eq("id", row['id']).execute()
                                st.session_state.job_positions = st.session_state.job_positions[
                                    st.session_state.job_positions['id'] != row['id']
                                ]
                                st.rerun()
                if 'edit_id' in st.session_state:
                    st.markdown("---")
                    st.subheader(f"Editing: {st.session_state.edit_title}")
                    new_title = st.text_input(t("job_title"), value=st.session_state.edit_title)
                    new_desc = st.text_area(t("job_description"), value=st.session_state.edit_desc)
                    new_skills = st.text_input(t("required_skills"), value=st.session_state.edit_skills)
                    new_exp = st.number_input(t("min_experience"), value=int(st.session_state.edit_exp))
                    if st.button(t("save_changes")):
                        idx = st.session_state.job_positions[
                            st.session_state.job_positions['id'] == st.session_state.edit_id
                        ].index[0]
                        st.session_state.job_positions.at[idx, 'title'] = new_title
                        st.session_state.job_positions.at[idx, 'description'] = new_desc
                        st.session_state.job_positions.at[idx, 'required_skills'] = new_skills
                        st.session_state.job_positions.at[idx, 'min_experience'] = new_exp
                        if supabase_client:
                            supabase_client.table("job_positions").update({
                                "title": new_title,
                                "description": new_desc,
                                "required_skills": new_skills,
                                "min_experience": new_exp
                            }).eq("id", st.session_state.edit_id).execute()
                        del st.session_state.edit_id
                        st.rerun()
            else:
                st.info("No job positions yet. Add one above.")

    # ---------- Screen CV ----------
    with tabs[1]:
        st.subheader(t("screen_cv"))
        st.markdown("Upload a CV and select a job position to analyse qualification.")

        if groq_client:
            st.info("🤖 **AI-Powered Analysis**: Groq is enabled. You will get a detailed AI analysis.")
        else:
            st.warning("⚠️ Groq AI not configured. Falling back to basic keyword matching.")

        applicant_name = st.text_input(t("applicant_name"))
        applicant_email = st.text_input(t("applicant_email"))
        uploaded_cv = st.file_uploader(t("upload_cv"), type=["pdf", "docx", "txt"])
        job_options = st.session_state.job_positions['title'].tolist()
        selected_job = st.selectbox(t("select_job"), job_options) if job_options else None

        if applicant_email and st.checkbox("Check email for data breaches"):
            with st.spinner("Checking email..."):
                breached, breach_message = check_email_breach(applicant_email)
                if breached is True:
                    st.markdown(f'<p class="breach-warning">{breach_message}</p>', unsafe_allow_html=True)
                elif breached is False:
                    st.markdown(f'<p class="breach-safe">{breach_message}</p>', unsafe_allow_html=True)
                else:
                    st.warning(breach_message)

        if st.button(t("analyze_cv")) and uploaded_cv and applicant_name and selected_job:
            with st.spinner(t("recording")):
                cv_text = extract_cv_text(uploaded_cv)
                if cv_text and len(cv_text) > 50:
                    job_row = st.session_state.job_positions[
                        st.session_state.job_positions['title'] == selected_job
                    ].iloc[0]

                    ai_score, ai_summary, ai_strengths, ai_weaknesses = analyze_cv_with_groq(
                        cv_text,
                        job_row['title'],
                        job_row['description'],
                        job_row['required_skills']
                    )

                    if ai_score is not None:
                        score = ai_score
                        st.markdown("---")
                        st.markdown(f'<span class="ai-badge">🤖 AI-Powered Analysis</span>', unsafe_allow_html=True)
                        st.markdown(f"### Match Score: **{score}%**")

                        if score >= 70:
                            st.markdown(f'<p class="score-high">{t("highly_qualified")} – Score: {score}%</p>', unsafe_allow_html=True)
                        elif score >= 50:
                            st.markdown(f'<p class="score-medium">{t("partially_qualified")} – Score: {score}%</p>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<p class="score-low">{t("low_match")} – Score: {score}%</p>', unsafe_allow_html=True)

                        st.markdown(f"**Summary:** {ai_summary}")
                        if ai_strengths:
                            st.markdown("**Strengths:**")
                            for s in ai_strengths:
                                st.markdown(f"- ✅ {s}")
                        if ai_weaknesses:
                            st.markdown("**Areas for improvement:**")
                            for w in ai_weaknesses:
                                st.markdown(f"- ⚠️ {w}")

                        # Generate acceptance email
                        email_body = generate_acceptance_email(cv_text, job_row['title'], score, ai_strengths, ai_weaknesses)
                        st.session_state.ai_email_body = email_body

                        st.markdown("---")
                        st.subheader(t("ai_email_generator"))
                        st.text_area(t("email_body"), email_body, height=200)

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(t("copy_email")):
                                st.write("📋 Email copied to clipboard!")

                        with col2:
                            if st.button(t("generate_email")):
                                st.session_state.ai_email_body = generate_acceptance_email(
                                    cv_text, job_row['title'], score, ai_strengths, ai_weaknesses
                                )
                                st.rerun()
                    else:
                        score = compute_match_score(cv_text, job_row['required_skills'], job_row['description'])
                        st.success(f"Analysis complete! Match score: {score}%")
                        if score >= 70:
                            st.markdown(f'<p class="score-high">{t("highly_qualified")} – Score: {score}%</p>', unsafe_allow_html=True)
                        elif score >= 50:
                            st.markdown(f'<p class="score-medium">{t("partially_qualified")} – Score: {score}%</p>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<p class="score-low">{t("low_match")} – Score: {score}%</p>', unsafe_allow_html=True)

                    new_app = {
                        "applicant_name": applicant_name,
                        "email": applicant_email,
                        "job_title": selected_job,
                        "score": score,
                        "cv_text_preview": cv_text[:500] + "...",
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    if supabase_client:
                        save_to_supabase("applications", new_app)
                    st.session_state.applications = pd.concat([
                        st.session_state.applications,
                        pd.DataFrame([new_app])
                    ], ignore_index=True)

                    st.info(f"✅ Application recorded. Email notification ready.")
                else:
                    st.error("Could not extract text from CV.")
        elif not selected_job:
            st.warning(t("no_jobs"))

    # ---------- Applications ----------
    with tabs[2]:
        st.subheader(t("all_applications"))
        if len(st.session_state.applications) > 0:
            st.dataframe(
                st.session_state.applications[["applicant_name", "email", "job_title", "score", "date"]],
                use_container_width=True
            )
            csv = st.session_state.applications.to_csv(index=False)
            st.download_button(t("download_csv"), data=csv, file_name="applications.csv")
            selected_app = st.selectbox(
                t("view_cv_preview"),
                st.session_state.applications['applicant_name'].tolist()
            )
            app_row = st.session_state.applications[
                st.session_state.applications['applicant_name'] == selected_app
            ].iloc[0]
            st.text_area(t("cv_text_preview"), app_row['cv_text_preview'], height=200)
        else:
            st.info("No applications yet. Screen some CVs.")

    # ---------- Email Integration ----------
    with tabs[3]:
        st.subheader(t("email_integration_desc"))
        st.markdown("""
        **How to receive CVs by email:**  
        Applicants can send their CV and details directly to:  
        `deslandes78@gmail.com`

        **To automatically screen emails:**  
        - This software currently accepts CV uploads directly.
        - For full email integration (IMAP), an advanced version can be built.

        **Note:** All uploaded CVs are stored in the system and can be reviewed in the **Applications** tab.
        """)
        st.info(t("admin_email"))

        st.markdown("---")
        st.subheader(t("ai_email_generator"))

        if st.session_state.ai_email_body:
            st.text_area("Generated Email", st.session_state.ai_email_body, height=250)

            # Send email directly from app
            with st.expander("📤 Send Email to Candidate"):
                recipient = st.text_input(t("recipient_email"), value="")
                subject = st.text_input(t("subject"), value="Congratulations! You have been selected")
                email_body_edit = st.text_area(t("email_body"), st.session_state.ai_email_body, height=200)

                if st.button(t("send_email")):
                    if email_api_input or email_api_key:
                        key = email_api_input or email_api_key
                        if send_email_with_sendgrid(key, recipient, subject, email_body_edit):
                            st.success("✅ Email sent successfully!")
                        else:
                            st.error("❌ Failed to send email. Check your API key.")
                    else:
                        st.warning("⚠️ Please enter your SendGrid API key in the sidebar.")
        else:
            st.info("Analyze a CV first to generate an acceptance email.")

    # ---------- Bulk Screening ----------
    with tabs[4]:
        st.subheader("📋 Bulk CV Screening")
        st.markdown("Upload up to 10 CVs or documents (CVs, cover letters, bio documents) and analyze them all at once.")

        job_options = st.session_state.job_positions['title'].tolist()
        bulk_job = st.selectbox("Select Job Position for Bulk Analysis", job_options) if job_options else None

        if not bulk_job:
            st.warning("Please add a job position first.")
        else:
            uploaded_files = st.file_uploader(
                "Upload Multiple Files (PDF, DOCX, TXT)",
                type=["pdf", "docx", "txt"],
                accept_multiple_files=True
            )

            if uploaded_files and len(uploaded_files) > 10:
                st.warning("Maximum 10 files allowed. Only the first 10 will be processed.")
                uploaded_files = uploaded_files[:10]

            if uploaded_files and st.button("🔍 Analyze All CVs"):
                st.session_state.bulk_results = []
                progress_bar = st.progress(0)
                status_text = st.empty()

                job_row = st.session_state.job_positions[
                    st.session_state.job_positions['title'] == bulk_job
                ].iloc[0]

                for idx, file in enumerate(uploaded_files):
                    status_text.text(f"Processing {file.name}... ({idx+1}/{len(uploaded_files)})")

                    # Extract text
                    cv_text = extract_cv_text(file)

                    if cv_text and len(cv_text) > 50:
                        # Try AI analysis first
                        ai_score, ai_summary, ai_strengths, ai_weaknesses = analyze_cv_with_groq(
                            cv_text,
                            job_row['title'],
                            job_row['description'],
                            job_row['required_skills']
                        )

                        if ai_score is not None:
                            score = ai_score
                            recommendation = "Interview" if score >= 70 else ("Review" if score >= 50 else "Reject")
                            summary = ai_summary or "Analysis completed."
                        else:
                            score = compute_match_score(cv_text, job_row['required_skills'], job_row['description'])
                            recommendation = "Interview" if score >= 70 else ("Review" if score >= 50 else "Reject")
                            summary = "Keyword-based analysis completed."

                        result = {
                            "file_name": file.name,
                            "candidate_name": file.name.replace(".pdf", "").replace(".docx", "").replace(".txt", ""),
                            "score": score,
                            "recommendation": recommendation,
                            "summary": summary,
                            "strengths": ai_strengths if ai_strengths else [],
                            "weaknesses": ai_weaknesses if ai_weaknesses else [],
                            "cv_text": cv_text[:500] + "..."
                        }
                        st.session_state.bulk_results.append(result)
                    else:
                        st.session_state.bulk_results.append({
                            "file_name": file.name,
                            "candidate_name": file.name,
                            "score": 0,
                            "recommendation": "Error",
                            "summary": "Could not extract text from file.",
                            "strengths": [],
                            "weaknesses": [],
                            "cv_text": ""
                        })

                    progress_bar.progress((idx + 1) / len(uploaded_files))

                status_text.text("✅ Analysis complete!")
                st.success(f"Successfully analyzed {len(st.session_state.bulk_results)} files.")

            # Display bulk results
            if st.session_state.bulk_results:
                st.markdown("---")
                st.subheader("📊 Bulk Analysis Results")

                results_df = pd.DataFrame(st.session_state.bulk_results)[
                    ["file_name", "candidate_name", "score", "recommendation", "summary"]
                ]
                st.dataframe(results_df, use_container_width=True)

                # Show details for each candidate
                for idx, result in enumerate(st.session_state.bulk_results):
                    with st.expander(f"📄 {result['candidate_name']} - Score: {result['score']}% - {result['recommendation']}"):
                        st.markdown(f"**File:** {result['file_name']}")
                        st.markdown(f"**Score:** {result['score']}%")
                        st.markdown(f"**Recommendation:** {result['recommendation']}")
                        st.markdown(f"**Summary:** {result['summary']}")

                        if result['strengths']:
                            st.markdown("**Strengths:**")
                            for s in result['strengths']:
                                st.markdown(f"- ✅ {s}")

                        if result['weaknesses']:
                            st.markdown("**Areas for improvement:**")
                            for w in result['weaknesses']:
                                st.markdown(f"- ⚠️ {w}")

                        st.text_area("CV Preview", result['cv_text'], height=100)

                # Generate bulk acceptance emails
                st.markdown("---")
                st.subheader("📧 Generate Acceptance Emails for All Shortlisted Candidates")

                selected_candidates = st.multiselect(
                    "Select candidates to send acceptance emails to:",
                    [r['candidate_name'] for r in st.session_state.bulk_results if r['score'] >= 70]
                )

                if selected_candidates and st.button("📝 Generate Emails for Selected"):
                    for candidate in selected_candidates:
                        result = next(r for r in st.session_state.bulk_results if r['candidate_name'] == candidate)
                        email = generate_acceptance_email(
                            result['cv_text'],
                            bulk_job,
                            result['score'],
                            result['strengths'],
                            result['weaknesses']
                        )
                        st.text_area(f"Email for {candidate}", email, height=200)

if not st.session_state.authenticated:
    login()
else:
    main_app()
