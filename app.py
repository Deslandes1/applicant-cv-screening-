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
        "recording": "Recording application...",
        "check_breach": "Check email for data breaches",
        "breach_check": "Checking email in breach databases...",
        "breach_found": "⚠️ Found in {count} breach(es).",
        "breach_not_found": "✅ No breaches found.",
        "breach_error": "Error checking breach.",
        "unsupported_file": "Unsupported file type.",
        "analysis_complete": "Analysis complete! Match score: {score}%",
        "ai_powered": "🤖 AI-Powered Analysis",
        "summary": "Summary",
        "strengths": "Strengths",
        "weaknesses": "Areas for improvement",
        "recommendation": "Recommendation",
        "application_recorded": "✅ Application recorded. Email notification ready.",
        "copy_email_success": "📋 Email copied to clipboard!",
        "email_sent_success": "✅ Email sent successfully!",
        "email_sent_fail": "❌ Failed to send email. Check your API key.",
        "email_api_missing": "⚠️ Please enter your SendGrid API key in the sidebar.",
        "bulk_analysis_title": "📊 Bulk Analysis Results",
        "select_candidates": "Select candidates to send acceptance emails to:",
        "generate_emails": "📝 Generate Emails for Selected",
        "email_for": "Email for {candidate}",
        "max_10_files": "Maximum 10 files allowed. Only the first 10 will be processed.",
        "processing_file": "Processing {file}... ({idx}/{total})",
        "analysis_complete_bulk": "✅ Analysis complete!",
        "success_analyzed": "Successfully analyzed {count} files.",
        "error_extract_text": "Could not extract text from CV.",
        "describe_app": "🎤 Describe This App",
        "listening_guide": "📢 Audio description is playing..."
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
        "recording": "Enregistrement de la candidature...",
        "check_breach": "Vérifier l'email dans les fuites de données",
        "breach_check": "Vérification de l'email dans les bases de données de fuites...",
        "breach_found": "⚠️ Trouvé dans {count} fuite(s).",
        "breach_not_found": "✅ Aucune fuite trouvée.",
        "breach_error": "Erreur lors de la vérification.",
        "unsupported_file": "Type de fichier non supporté.",
        "analysis_complete": "Analyse terminée ! Score de correspondance : {score}%",
        "ai_powered": "🤖 Analyse par IA",
        "summary": "Résumé",
        "strengths": "Points forts",
        "weaknesses": "Points à améliorer",
        "recommendation": "Recommandation",
        "application_recorded": "✅ Candidature enregistrée. Email de notification prêt.",
        "copy_email_success": "📋 Email copié dans le presse-papiers !",
        "email_sent_success": "✅ Email envoyé avec succès !",
        "email_sent_fail": "❌ Échec de l'envoi de l'email. Vérifiez votre clé API.",
        "email_api_missing": "⚠️ Veuillez saisir votre clé API SendGrid dans la barre latérale.",
        "bulk_analysis_title": "📊 Résultats de l'Analyse en Masse",
        "select_candidates": "Sélectionnez les candidats pour envoyer des emails d'acceptation :",
        "generate_emails": "📝 Générer les Emails pour les Sélectionnés",
        "email_for": "Email pour {candidate}",
        "max_10_files": "Maximum 10 fichiers autorisés. Seuls les 10 premiers seront traités.",
        "processing_file": "Traitement de {file}... ({idx}/{total})",
        "analysis_complete_bulk": "✅ Analyse terminée !",
        "success_analyzed": "{count} fichiers analysés avec succès.",
        "error_extract_text": "Impossible d'extraire le texte du CV.",
        "describe_app": "🎤 Décrire cette Application",
        "listening_guide": "📢 La description audio est en cours de lecture..."
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
        "recording": "Registrando solicitud...",
        "check_breach": "Verificar correo en filtraciones de datos",
        "breach_check": "Verificando correo en bases de datos de filtraciones...",
        "breach_found": "⚠️ Encontrado en {count} filtración(es).",
        "breach_not_found": "✅ No se encontraron filtraciones.",
        "breach_error": "Error al verificar filtraciones.",
        "unsupported_file": "Tipo de archivo no compatible.",
        "analysis_complete": "¡Análisis completo! Puntuación de coincidencia: {score}%",
        "ai_powered": "🤖 Análisis con IA",
        "summary": "Resumen",
        "strengths": "Fortalezas",
        "weaknesses": "Áreas de mejora",
        "recommendation": "Recomendación",
        "application_recorded": "✅ Solicitud registrada. Email de notificación listo.",
        "copy_email_success": "📋 ¡Correo copiado al portapapeles!",
        "email_sent_success": "✅ ¡Correo enviado con éxito!",
        "email_sent_fail": "❌ Error al enviar el correo. Verifica tu clave API.",
        "email_api_missing": "⚠️ Por favor, ingresa tu clave API de SendGrid en la barra lateral.",
        "bulk_analysis_title": "📊 Resultados del Análisis Masivo",
        "select_candidates": "Selecciona candidatos para enviar correos de aceptación:",
        "generate_emails": "📝 Generar Correos para los Seleccionados",
        "email_for": "Correo para {candidate}",
        "max_10_files": "Máximo 10 archivos permitidos. Solo se procesarán los primeros 10.",
        "processing_file": "Procesando {file}... ({idx}/{total})",
        "analysis_complete_bulk": "✅ ¡Análisis completo!",
        "success_analyzed": "{count} archivos analizados con éxito.",
        "error_extract_text": "No se pudo extraer el texto del CV.",
        "describe_app": "🎤 Describir esta Aplicación",
        "listening_guide": "📢 Reproduciendo descripción de audio..."
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
        "recording": "正在记录申请...",
        "check_breach": "检查邮箱是否在数据泄露中",
        "breach_check": "正在检查邮箱是否在泄露数据库中...",
        "breach_found": "⚠️ 在 {count} 次数据泄露中找到。",
        "breach_not_found": "✅ 未发现泄露。",
        "breach_error": "检查泄露时出错。",
        "unsupported_file": "不支持的文件类型。",
        "analysis_complete": "分析完成！匹配分数：{score}%",
        "ai_powered": "🤖 AI 分析",
        "summary": "摘要",
        "strengths": "优势",
        "weaknesses": "改进领域",
        "recommendation": "建议",
        "application_recorded": "✅ 申请已记录。邮件通知已准备。",
        "copy_email_success": "📋 邮件已复制到剪贴板！",
        "email_sent_success": "✅ 邮件已成功发送！",
        "email_sent_fail": "❌ 发送邮件失败。请检查您的 API 密钥。",
        "email_api_missing": "⚠️ 请在侧边栏输入您的 SendGrid API 密钥。",
        "bulk_analysis_title": "📊 批量分析结果",
        "select_candidates": "选择要发送录用邮件的候选人：",
        "generate_emails": "📝 为所选候选人生成邮件",
        "email_for": "给 {candidate} 的邮件",
        "max_10_files": "最多允许10个文件。仅处理前10个。",
        "processing_file": "正在处理 {file}... ({idx}/{total})",
        "analysis_complete_bulk": "✅ 分析完成！",
        "success_analyzed": "成功分析了 {count} 个文件。",
        "error_extract_text": "无法从简历中提取文本。",
        "describe_app": "🎤 描述此应用",
        "listening_guide": "📢 正在播放音频描述..."
    }
}

# ---------- App Description Function ----------
def get_app_description(lang):
    """Return a detailed description of the app in the selected language."""
    descriptions = {
        "en": """
Welcome to the Applicant CV Screening Software, created by Gesner Deslandes, Engineer in Chief at Globalinternet.py.

This powerful recruitment tool helps you screen CVs, cover letters, and bio documents with lightning speed.

Here is how to use it:

First, log in with your admin password. Then, navigate through the tabs:

- In the "Job Positions" tab, you can add, edit, or delete job openings. Each position includes a title, description, required skills, and minimum experience.

- In the "Screen CV" tab, enter the applicant's name and email, upload their CV (PDF, DOCX, or TXT), and select a job. The system will extract the text and analyze it using either our AI engine (Groq) or a keyword-based fallback. You'll get a match score, a summary, strengths, weaknesses, and a recommendation. You can also check if the email has been involved in a data breach.

- Once analyzed, an AI-generated acceptance email is automatically created. You can copy it to your clipboard, or if you have a SendGrid API key, send it directly from the app.

- The "Bulk Screening" tab allows you to upload up to 10 documents at once and analyze them all simultaneously. You can then generate acceptance emails for the shortlisted candidates.

- The "Applications" tab displays all screened candidates with their scores and dates. You can export the data to CSV.

Additional features: 
- You can change the app's language to English, French, Spanish, or Chinese using the sidebar.
- The AI Voice feature can read any text aloud in your chosen language, including the acceptance email.

This software was designed to save recruiters hours of manual work and help you find the best talent faster.

We are proud to say: We are the best!

For any questions, contact us:
Gesner Deslandes / Engineer in Chief at Globalinternet.py
Phone: (509) 4738-5663
Email: deslandes78@gmail.com
""",
        "fr": """
Bienvenue dans le Logiciel de Criblage de CV, créé par Gesner Deslandes, Ingénieur en Chef chez Globalinternet.py.

Cet outil de recrutement puissant vous aide à analyser des CV, des lettres de motivation et des documents bio à une vitesse fulgurante.

Voici comment l'utiliser :

Connectez-vous d'abord avec votre mot de passe administrateur. Ensuite, naviguez dans les onglets :

- Dans l'onglet "Postes", vous pouvez ajouter, modifier ou supprimer des offres d'emploi. Chaque poste comprend un titre, une description, les compétences requises et l'expérience minimale.

- Dans l'onglet "Cribler un CV", saisissez le nom et l'email du candidat, téléchargez son CV (PDF, DOCX ou TXT) et sélectionnez un poste. Le système extraira le texte et l'analysera soit par notre moteur IA (Groq), soit par une méthode de mots-clés. Vous obtiendrez un score de correspondance, un résumé, des points forts, des points faibles et une recommandation. Vous pouvez également vérifier si l'email a été compromis dans une fuite de données.

- Une fois analysé, un email d'acceptation généré par IA est automatiquement créé. Vous pouvez le copier dans le presse-papiers, ou si vous avez une clé API SendGrid, l'envoyer directement depuis l'application.

- L'onglet "Criblage en Masse" vous permet de télécharger jusqu'à 10 documents à la fois et de les analyser simultanément. Vous pouvez ensuite générer des emails d'acceptation pour les candidats présélectionnés.

- L'onglet "Candidatures" affiche tous les candidats criblés avec leurs scores et dates. Vous pouvez exporter les données en CSV.

Fonctionnalités supplémentaires :
- Vous pouvez changer la langue de l'application en anglais, français, espagnol ou chinois via la barre latérale.
- La fonction "Voix IA" peut lire n'importe quel texte à voix haute dans la langue choisie, y compris l'email d'acceptation.

Ce logiciel a été conçu pour faire gagner des heures de travail manuel aux recruteurs et vous aider à trouver les meilleurs talents plus rapidement.

Nous sommes fiers de dire : Nous sommes les meilleurs !

Pour toute question, contactez-nous :
Gesner Deslandes / Ingénieur en Chef chez Globalinternet.py
Téléphone : (509) 4738-5663
Email : deslandes78@gmail.com
""",
        "es": """
Bienvenido al Software de Cribado de CV, creado por Gesner Deslandes, Ingeniero Jefe en Globalinternet.py.

Esta poderosa herramienta de reclutamiento le ayuda a analizar CV, cartas de presentación y documentos biográficos a gran velocidad.

Así es como se usa:

Primero, inicie sesión con su contraseña de administrador. Luego, navegue por las pestañas:

- En la pestaña "Puestos", puede agregar, editar o eliminar ofertas de trabajo. Cada puesto incluye título, descripción, habilidades requeridas y experiencia mínima.

- En la pestaña "Evaluar CV", ingrese el nombre y correo del candidato, suba su CV (PDF, DOCX o TXT) y seleccione un puesto. El sistema extraerá el texto y lo analizará mediante nuestro motor de IA (Groq) o un método basado en palabras clave. Obtendrá una puntuación de coincidencia, un resumen, fortalezas, debilidades y una recomendación. También puede verificar si el correo ha estado en una filtración de datos.

- Una vez analizado, se genera automáticamente un correo de aceptación por IA. Puede copiarlo al portapapeles o, si tiene una clave API de SendGrid, enviarlo directamente desde la aplicación.

- La pestaña "Evaluación Masiva" le permite subir hasta 10 documentos a la vez y analizarlos simultáneamente. Luego puede generar correos de aceptación para los candidatos preseleccionados.

- La pestaña "Solicitudes" muestra todos los candidatos evaluados con sus puntuaciones y fechas. Puede exportar los datos a CSV.

Características adicionales:
- Puede cambiar el idioma de la aplicación a inglés, francés, español o chino desde la barra lateral.
- La función "Voz IA" puede leer cualquier texto en voz alta en el idioma elegido, incluido el correo de aceptación.

Este software fue diseñado para ahorrar horas de trabajo manual a los reclutadores y ayudarle a encontrar el mejor talento más rápido.

Estamos orgullosos de decir: ¡Somos los mejores!

Para cualquier pregunta, contáctenos:
Gesner Deslandes / Ingeniero Jefe en Globalinternet.py
Teléfono: (509) 4738-5663
Email: deslandes78@gmail.com
""",
        "zh": """
欢迎使用简历筛选软件，由 Globalinternet.py 首席工程师 Gesner Deslandes 创建。

这款强大的招聘工具可帮助您快速筛选简历、求职信和个人简介文档。

使用方法如下：

首先，使用管理员密码登录。然后，通过选项卡导航：

- 在“职位管理”选项卡中，您可以添加、编辑或删除职位空缺。每个职位包括标题、描述、所需技能和最低经验。

- 在“简历筛选”选项卡中，输入申请人姓名和邮箱，上传简历（PDF、DOCX 或 TXT），然后选择一个职位。系统将提取文本并使用我们的 AI 引擎（Groq）或基于关键词的方法进行分析。您将获得匹配分数、摘要、优势、不足和建议。您还可以检查邮箱是否曾涉及数据泄露。

- 分析完成后，AI 会自动生成录用邮件。您可以将其复制到剪贴板，或者如果您有 SendGrid API 密钥，可以直接从应用发送。

- “批量筛选”选项卡允许您一次上传多达 10 份文档并同时进行分析。然后您可以为入围的候选人生成录用邮件。

- “申请记录”选项卡显示所有已筛选的候选人及其分数和日期。您可以将数据导出为 CSV。

附加功能：
- 您可以通过侧边栏将应用语言切换为英语、法语、西班牙语或中文。
- “AI 语音”功能可以用您选择的语言朗读任何文本，包括录用邮件。

本软件旨在为招聘人员节省数小时的繁琐工作，并帮助您更快地找到最佳人才。

我们自豪地说：我们是最棒的！

如有任何问题，请联系我们：
Gesner Deslandes / Globalinternet.py 首席工程师
电话：(509) 4738-5663
邮箱：deslandes78@gmail.com
"""
    }
    return descriptions.get(lang, descriptions["en"])

# ---------- Initialize API Clients ----------
def init_groq_client():
    try:
        api_key = st.secrets.get("GROQ_API_KEY")
        if Groq and api_key:
            return Groq(api_key=api_key)
    except Exception:
        pass
    return None

def init_supabase_client():
    try:
        url = st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_ANON_KEY")
        if Client and url and key:
            return create_client(url, key)
    except Exception:
        pass
    return None

def get_global_surveillance_key():
    try:
        return st.secrets.get("GLOBAL_SURVEILLANCE_KEY")
    except Exception:
        return None

def get_email_api_key():
    try:
        return st.secrets.get("EMAIL_API_KEY")
    except Exception:
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
if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

# Load data from Supabase or session state
def load_job_positions():
    if supabase_client:
        try:
            response = supabase_client.table("job_positions").select("*").execute()
            if response.data:
                df = pd.DataFrame(response.data)
                if not df.empty and "id" in df.columns:
                    return df
        except Exception:
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
        except Exception:
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
    except Exception:
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
    except Exception:
        return ""

def extract_text_from_txt(file_bytes):
    try:
        return file_bytes.decode("utf-8")
    except Exception:
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
    skills_list = [s.strip().lower() for s in job_skills.split(",") if s.strip()]
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
    except Exception:
        return None, None, None, None

def generate_acceptance_email(cv_text, job_title, score, strengths, weaknesses):
    """Generate an acceptance email using Groq AI."""
    if not groq_client:
        # Fallback template
        return f"""Subject: Congratulations! You have been selected for {job_title}

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
    except Exception:
        # Fallback if AI fails
        return f"""Subject: Congratulations! You have been selected for {job_title}

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
                return True, len(breaches)
            else:
                return False, 0
        else:
            return None, None
    except Exception:
        return None, None

def save_to_supabase(table, data):
    if not supabase_client:
        return False
    try:
        supabase_client.table(table).insert(data).execute()
        return True
    except Exception:
        return False

def delete_from_supabase(table, id_value, id_column="id"):
    if not supabase_client:
        return False
    try:
        supabase_client.table(table).delete().eq(id_column, id_value).execute()
        return True
    except Exception:
        return False

def update_supabase(table, id_value, data, id_column="id"):
    if not supabase_client:
        return False
    try:
        supabase_client.table(table).update(data).eq(id_column, id_value).execute()
        return True
    except Exception:
        return False

def text_to_speech(text, lang):
    if not gTTS:
        return None
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes
    except Exception:
        return None

def send_email_with_sendgrid(api_key, to_email, subject, body):
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
    except Exception:
        return False

# ---------- Custom CSS ----------
st.markdown("""
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
.ai-badge {
    background: #6c5ce7;
    color: white;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 12px;
    display: inline-block;
}
.breach-warning {
    background: #ff6b6b;
    color: white;
    padding: 5px 15px;
    border-radius: 10px;
    font-weight: bold;
}
.breach-safe {
    background: #51cf66;
    color: white;
    padding: 5px 15px;
    border-radius: 10px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

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

        # NEW: Describe App Button
        if st.button(t("describe_app")):
            description = get_app_description(st.session_state.voice_language)
            audio = text_to_speech(description, st.session_state.voice_language)
            if audio:
                st.audio(audio, format="audio/mp3")
                st.success(t("listening_guide"))
            else:
                st.error("gTTS not installed. Please run: pip install gTTS")

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
                                    delete_from_supabase("job_positions", row['id'])
                                st.session_state.job_positions = st.session_state.job_positions[
                                    st.session_state.job_positions['id'] != row['id']
                                ]
                                st.rerun()
                if st.session_state.edit_id is not None:
                    row_edit = st.session_state.job_positions[st.session_state.job_positions['id'] == st.session_state.edit_id].iloc[0]
                    st.markdown("---")
                    st.subheader(f"Editing: {row_edit['title']}")
                    new_title = st.text_input(t("job_title"), value=row_edit['title'])
                    new_desc = st.text_area(t("job_description"), value=row_edit['description'])
                    new_skills = st.text_input(t("required_skills"), value=row_edit['required_skills'])
                    new_exp = st.number_input(t("min_experience"), value=int(row_edit['min_experience']))
                    if st.button(t("save_changes")):
                        idx = st.session_state.job_positions[st.session_state.job_positions['id'] == st.session_state.edit_id].index[0]
                        st.session_state.job_positions.at[idx, 'title'] = new_title
                        st.session_state.job_positions.at[idx, 'description'] = new_desc
                        st.session_state.job_positions.at[idx, 'required_skills'] = new_skills
                        st.session_state.job_positions.at[idx, 'min_experience'] = new_exp
                        if supabase_client:
                            update_supabase("job_positions", st.session_state.edit_id, {
                                "title": new_title,
                                "description": new_desc,
                                "required_skills": new_skills,
                                "min_experience": new_exp
                            })
                        st.session_state.edit_id = None
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

        if applicant_email and st.checkbox(t("check_breach")):
            with st.spinner(t("breach_check")):
                breached, count = check_email_breach(applicant_email)
                if breached is True:
                    st.markdown(f'<p class="breach-warning">{t("breach_found").format(count=count)}</p>', unsafe_allow_html=True)
                elif breached is False:
                    st.markdown(f'<p class="breach-safe">{t("breach_not_found")}</p>', unsafe_allow_html=True)
                else:
                    st.warning(t("breach_error"))

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
                        st.markdown(f'<span class="ai-badge">{t("ai_powered")}</span>', unsafe_allow_html=True)
                        st.markdown(f"### Match Score: **{score}%**")
                        if score >= 70:
                            st.markdown(f'<p class="score-high">{t("highly_qualified")} – Score: {score}%</p>', unsafe_allow_html=True)
                        elif score >= 50:
                            st.markdown(f'<p class="score-medium">{t("partially_qualified")} – Score: {score}%</p>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<p class="score-low">{t("low_match")} – Score: {score}%</p>', unsafe_allow_html=True)

                        st.markdown(f"**{t('summary')}:** {ai_summary}")
                        if ai_strengths:
                            st.markdown(f"**{t('strengths')}:**")
                            for s in ai_strengths:
                                st.markdown(f"- ✅ {s}")
                        if ai_weaknesses:
                            st.markdown(f"**{t('weaknesses')}:**")
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
                                st.write(t("copy_email_success"))
                        with col2:
                            if st.button(t("generate_email")):
                                st.session_state.ai_email_body = generate_acceptance_email(
                                    cv_text, job_row['title'], score, ai_strengths, ai_weaknesses
                                )
                                st.rerun()
                    else:
                        score = compute_match_score(cv_text, job_row['required_skills'], job_row['description'])
                        st.success(t("analysis_complete").format(score=score))
                        if score >= 70:
                            st.markdown(f'<p class="score-high">{t("highly_qualified")} – Score: {score}%</p>', unsafe_allow_html=True)
                        elif score >= 50:
                            st.markdown(f'<p class="score-medium">{t("partially_qualified")} – Score: {score}%</p>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<p class="score-low">{t("low_match")} – Score: {score}%</p>', unsafe_allow_html=True)

                        # Generate fallback email
                        email_body = generate_acceptance_email(cv_text, job_row['title'], score, [], [])
                        st.session_state.ai_email_body = email_body
                        st.markdown("---")
                        st.subheader(t("ai_email_generator"))
                        st.text_area(t("email_body"), email_body, height=200)

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

                    st.info(t("application_recorded"))
                else:
                    st.error(t("error_extract_text"))
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

            with st.expander("📤 Send Email to Candidate"):
                recipient = st.text_input(t("recipient_email"), value="")
                subject = st.text_input(t("subject"), value="Congratulations! You have been selected")
                email_body_edit = st.text_area(t("email_body"), st.session_state.ai_email_body, height=200)

                if st.button(t("send_email")):
                    api_key_to_use = email_api_input or email_api_key
                    if api_key_to_use:
                        if send_email_with_sendgrid(api_key_to_use, recipient, subject, email_body_edit):
                            st.success(t("email_sent_success"))
                        else:
                            st.error(t("email_sent_fail"))
                    else:
                        st.warning(t("email_api_missing"))
        else:
            st.info("Analyze a CV first to generate an acceptance email.")

    # ---------- Bulk Screening ----------
    with tabs[4]:
        st.subheader("📋 Bulk CV Screening")
        st.markdown("Upload up to 10 CVs or documents (CVs, cover letters, bio documents) and analyze them all at once.")

        job_options = st.session_state.job_positions['title'].tolist()
        bulk_job = st.selectbox("Select Job Position for Bulk Analysis", job_options) if job_options else None

        if not bulk_job:
            st.warning(t("no_jobs"))
        else:
            uploaded_files = st.file_uploader(
                t("bulk_upload"),
                type=["pdf", "docx", "txt"],
                accept_multiple_files=True
            )

            if uploaded_files and len(uploaded_files) > 10:
                st.warning(t("max_10_files"))
                uploaded_files = uploaded_files[:10]

            if uploaded_files and st.button(t("bulk_analyze")):
                st.session_state.bulk_results = []
                progress_bar = st.progress(0)
                status_text = st.empty()

                job_row = st.session_state.job_positions[
                    st.session_state.job_positions['title'] == bulk_job
                ].iloc[0]

                for idx, file in enumerate(uploaded_files):
                    status_text.text(t("processing_file").format(file=file.name, idx=idx+1, total=len(uploaded_files)))
                    cv_text = extract_cv_text(file)
                    if cv_text and len(cv_text) > 50:
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
                            strengths = ai_strengths
                            weaknesses = ai_weaknesses
                        else:
                            score = compute_match_score(cv_text, job_row['required_skills'], job_row['description'])
                            recommendation = "Interview" if score >= 70 else ("Review" if score >= 50 else "Reject")
                            summary = "Keyword-based analysis completed."
                            strengths = []
                            weaknesses = []

                        result = {
                            "file_name": file.name,
                            "candidate_name": file.name.replace(".pdf", "").replace(".docx", "").replace(".txt", ""),
                            "score": score,
                            "recommendation": recommendation,
                            "summary": summary,
                            "strengths": strengths,
                            "weaknesses": weaknesses,
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

                status_text.text(t("analysis_complete_bulk"))
                st.success(t("success_analyzed").format(count=len(st.session_state.bulk_results)))

            # Display bulk results
            if st.session_state.bulk_results:
                st.markdown("---")
                st.subheader(t("bulk_analysis_title"))

                results_df = pd.DataFrame(st.session_state.bulk_results)[
                    ["file_name", "candidate_name", "score", "recommendation", "summary"]
                ]
                st.dataframe(results_df, use_container_width=True)

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

                st.markdown("---")
                st.subheader("📧 Generate Acceptance Emails for All Shortlisted Candidates")

                shortlisted = [r for r in st.session_state.bulk_results if r['score'] >= 70]
                if shortlisted:
                    selected_candidates = st.multiselect(
                        t("select_candidates"),
                        [r['candidate_name'] for r in shortlisted]
                    )
                    if selected_candidates and st.button(t("generate_emails")):
                        for candidate in selected_candidates:
                            result = next(r for r in st.session_state.bulk_results if r['candidate_name'] == candidate)
                            email = generate_acceptance_email(
                                result['cv_text'],
                                bulk_job,
                                result['score'],
                                result['strengths'],
                                result['weaknesses']
                            )
                            st.text_area(t("email_for").format(candidate=candidate), email, height=200)
                else:
                    st.info("No candidates with a score >= 70% to shortlist.")

if not st.session_state.authenticated:
    login()
else:
    main_app()
