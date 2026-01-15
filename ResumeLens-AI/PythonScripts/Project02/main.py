import streamlit as st
import PyPDF2
import io
import ollama
import re
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="ResumeLens AI – AI Resume Analysis",
    page_icon="logo.png",
    layout="centered"
)

# ---------------- HEADER ----------------
st.title("ResumeLens AI")
st.markdown(
    "<p style='font-size:18px; color:#6c757d;'>"
    "Smarter, AI-powered resume analysis for better hiring outcomes."
    "</p>",
    unsafe_allow_html=True
)

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader(
    "Upload your resume (PDF or TXT)",
    type=["pdf", "txt"]
)

# ---------------- JOB DESCRIPTION INPUT ----------------
job_description = st.text_area(
    "Paste the job description you are targeting (recommended for accurate scoring)",
    height=150
)

analyze = st.button("Analyze Resume")

# ---------------- FUNCTIONS ----------------
def extract_text_from_pdf(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"
    return text

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    else:
        return uploaded_file.read().decode("utf-8")

def calculate_ats_score(text):
    score = 0
    text_lower = text.lower()
    words = text.split()
    word_count = len(words)

    # Resume length (30 points)
    if 500 <= word_count <= 800:
        score += 30
    elif 300 <= word_count < 500 or 800 < word_count <= 1000:
        score += 20
    else:
        score += 5

    # Section presence (40 points)
    sections = {"experience":10, "skills":10, "education":8, "projects":6, "summary":6}
    for section, points in sections.items():
        if section in text_lower:
            score += points

    # Impact verbs (15 points)
    impact_verbs = ["developed","built","designed","implemented","optimized","led","improved","automated"]
    verb_hits = sum(1 for v in impact_verbs if v in text_lower)
    score += min(verb_hits*2, 15)

    # Bullet points (15 points)
    bullet_lines = sum(1 for line in text.split("\n") if line.strip().startswith(("-", "•")))
    if bullet_lines >= 12:
        score += 15
    elif bullet_lines >= 6:
        score += 8

    return min(score, 100)

def calculate_skill_match(text, job_description):
    if not job_description:
        return None, []
    resume_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", text.lower()))
    jd_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", job_description.lower()))
    matched = resume_words.intersection(jd_words)
    if not jd_words: return 0, []
    return round(len(matched)/len(jd_words)*100,1), sorted(list(matched))[:10]

def calculate_readability(text):
    sentences = [s for s in re.split(r"[.!?]", text) if len(s.strip())>0]
    words = re.findall(r"\b\w+\b", text)
    if not sentences or not words: return 0
    avg_sentence_length = len(words)/len(sentences)
    complex_words = [w for w in words if len(w)>12]
    complex_ratio = len(complex_words)/len(words)
    score = 100 - (avg_sentence_length*1.5) - (complex_ratio*100)
    return max(min(round(score),100),30)

def generate_pdf(file_content, ats, skill, readability, matched_skills, ai_feedback):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height-50, "ResumeLens AI – Resume Analysis Report")

    c.setFont("Helvetica", 12)
    y = height-90
    c.drawString(50, y, f"ATS Score: {ats}/100")
    y -= 20
    c.drawString(50, y, f"Skill Match: {skill}%" if skill is not None else "Skill Match: N/A")
    y -= 20
    c.drawString(50, y, f"Readability: {readability}/100")
    y -= 20
    if matched_skills:
        c.drawString(50, y, "Matched Keywords: " + ", ".join(matched_skills))
        y -= 20

    y -= 20
    c.drawString(50, y, "⚠️ AI-powered detailed feedback is available locally.")
    y -= 20

    if ai_feedback:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "AI Feedback (truncated):")
        y -= 20
        text = ai_feedback[:1000] + "..." if len(ai_feedback) > 1000 else ai_feedback
        for line in text.split("\n"):
            if y<50:
                c.showPage()
                y = height-50
            c.drawString(50, y, line[:90])
            y -= 15

    c.save()
    buffer.seek(0)
    return buffer

# ---------------- MAIN LOGIC ----------------
if analyze and uploaded_file:
    try:
        file_content = extract_text_from_file(uploaded_file)
        if not file_content.strip():
            st.error("File does not have any readable content.")
            st.stop()

        # Metrics
        ats_score = calculate_ats_score(file_content)
        skill_match, matched_skills = calculate_skill_match(file_content, job_description)
        readability_score = calculate_readability(file_content)

        # Display Metrics with progress bars
        st.markdown("## 📌 Resume Evaluation Metrics")
        st.progress(ats_score/100)
        st.write(f"**ATS Score:** {ats_score}/100")
        st.progress(skill_match/100 if skill_match is not None else 0)
        st.write(f"**Skill Match:** {skill_match}%" if skill_match is not None else "N/A")
        st.progress(readability_score/100)
        st.write(f"**Readability:** {readability_score}/100")

        if matched_skills:
            st.markdown("**Matched Keywords (from Job Description):**")
            st.write(", ".join(matched_skills))

        st.divider()
        st.info("⚠️ AI-powered detailed feedback is available locally. Metrics above are fully functional online.")

        # ---- AI Feedback via Ollama (local only) ----
        ai_feedback = ""
        try:
            prompt = f"""
You are an expert resume reviewer with years of experience in HR and recruitment.

Please analyze the following resume and provide constructive feedback focusing on:
1. Content clarity and impact
2. Skills presentation
3. Experience description
4. Specific improvements for the job description provided

Resume Content:
{file_content}

Provide clear, structured feedback with actionable recommendations.
"""
            response = ollama.chat(
                model="llama3",
                messages=[
                    {"role": "system", "content": "You are a professional resume reviewer."},
                    {"role": "user", "content": prompt}
                ]
            )
            ai_feedback = response["message"]["content"]
            st.markdown("### 📊 AI Feedback")
            st.markdown(ai_feedback)
        except Exception:
            st.warning("⚠️ AI-powered detailed feedback could not be generated online. Runs locally via Ollama.")

        # PDF download
        pdf_buffer = generate_pdf(file_content, ats_score, skill_match, readability_score, matched_skills, ai_feedback)
        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_buffer,
            file_name="resume_report.pdf",
            mime="application/pdf"
        )

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# ---------------- FOOTER ----------------
st.markdown(
    """
    <style>
    .app-footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #ffffff;
        color: #6c757d;
        text-align: center;
        padding: 8px 0;
        font-size: 13px;
        border-top: 1px solid #e6e6e6;
        z-index: 100;
    }
    .app-footer a {
        color: #0d6efd;
        text-decoration: none;
        font-weight: 600;
    }
    .app-footer a:hover {
        text-decoration: underline;
    }
    </style>
    <div class="app-footer">
        ⚡ Powered by <strong>LLaMA 3</strong> &nbsp;•&nbsp;
        Made with 💗 by
        <a href="https://github.com/SanjayD11" target="_blank">Sanjay Dharmarajou</a>
    </div>
    """,
    unsafe_allow_html=True
)
