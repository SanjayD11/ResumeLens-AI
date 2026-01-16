import streamlit as st
import PyPDF2
import io
import re
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from groq import Groq

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="ResumeLens AI – AI Resume Analysis",
    page_icon="📄",
    layout="centered"
)

st.title("ResumeLens AI")
st.markdown(
    "<p style='font-size:18px; color:#6c757d;'>Smarter, AI-powered resume analysis for better hiring outcomes.</p>",
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])
job_description = st.text_area("Paste the job description you are targeting (recommended for accurate scoring)", height=150)
analyze = st.button("Analyze Resume")

# ---------------- FUNCTIONS ----------------
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"
    return text

def extract_text_from_file(file):
    if file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(file.read()))
    return file.read().decode("utf-8")

def calculate_ats_score(text):
    score = 0
    words = text.split()
    word_count = len(words)
    text_lower = text.lower()

    if 500 <= word_count <= 800:
        score += 30
    elif 300 <= word_count < 500 or 800 < word_count <= 1000:
        score += 20
    else:
        score += 5

    sections = {"experience":10, "skills":10, "education":8, "projects":6, "summary":6}
    for s, p in sections.items():
        if s in text_lower:
            score += p

    verbs = ["developed","built","designed","implemented","optimized","led","improved","automated"]
    score += min(sum(v in text_lower for v in verbs) * 2, 15)

    bullets = sum(1 for l in text.split("\n") if l.strip().startswith(("-", "•")))
    score += 15 if bullets >= 12 else 8 if bullets >= 6 else 0

    return min(score, 100)

def calculate_skill_match(text, jd):
    if not jd:
        return None, []
    resume_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", text.lower()))
    jd_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", jd.lower()))
    matched = resume_words & jd_words
    return round(len(matched) / len(jd_words) * 100, 1), sorted(matched)[:10]

def calculate_readability(text):
    sentences = [s for s in re.split(r"[.!?]", text) if s.strip()]
    words = re.findall(r"\b\w+\b", text)
    if not sentences or not words:
        return 0
    score = 100 - ((len(words)/len(sentences))*1.5) - ((len([w for w in words if len(w)>12])/len(words))*100)
    return max(min(round(score),100),30)

def generate_pdf(ats, skill, readability, keywords, feedback):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    w, h = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, h-50, "ResumeLens AI – Resume Analysis Report")

    c.setFont("Helvetica", 12)
    y = h-90
    c.drawString(50, y, f"ATS Score: {ats}/100"); y -= 20
    c.drawString(50, y, f"Skill Match: {skill if skill is not None else 'N/A'}%"); y -= 20
    c.drawString(50, y, f"Readability: {readability}/100"); y -= 30

    if keywords:
        c.drawString(50, y, "Matched Keywords: " + ", ".join(keywords)); y -= 30

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "AI Feedback:"); y -= 20
    c.setFont("Helvetica", 11)

    for line in feedback.split("\n"):
        if y < 50:
            c.showPage()
            y = h - 50
        c.drawString(50, y, line[:90])
        y -= 14

    c.save()
    buffer.seek(0)
    return buffer

# ---------------- MAIN LOGIC ----------------
if analyze and uploaded_file:
    try:
        resume_text = extract_text_from_file(uploaded_file)
        if not resume_text.strip():
            st.error("No readable content found.")
            st.stop()

        ats = calculate_ats_score(resume_text)
        skill, keywords = calculate_skill_match(resume_text, job_description)
        readability = calculate_readability(resume_text)

        st.markdown("## 📌 Resume Evaluation Metrics")
        st.progress(ats/100); st.write(f"**ATS Score:** {ats}/100")
        st.progress((skill or 0)/100); st.write(f"**Skill Match:** {skill if skill else 'N/A'}%")
        st.progress(readability/100); st.write(f"**Readability:** {readability}/100")
        if keywords:
            st.write("**Matched Keywords:**", ", ".join(keywords))
        st.divider()

        # ---------------- GROQ AI ----------------
        GROQ_API_KEY = "YOUR_API_KEY_HERE"
        client = Groq(api_key=GROQ_API_KEY)
        MODEL_NAME = "llama-3.3-70b-versatile"  # <-- this WORKS 100% with your key

        prompt = f"""
You are a professional resume reviewer.
Analyze the following resume thoroughly and provide structured feedback:

Resume Content:
{resume_text}

Job Description:
{job_description if job_description else 'Not provided'}
"""

        try:
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2000
            )
            ai_feedback = completion.choices[0].message.content.strip()
            st.markdown("### 📊 AI Feedback")
            st.markdown(ai_feedback)
        except Exception as e:
            st.error(f"AI feedback could not be generated: {str(e)}")
            ai_feedback = "AI feedback not available."

        # PDF download
        pdf = generate_pdf(ats, skill, readability, keywords, ai_feedback)
        st.download_button("📥 Download PDF Report", pdf, "resume_report.pdf", "application/pdf")

    except Exception as e:
        st.error(str(e))

# ---------------- FOOTER ----------------
st.markdown(
    """
    <div style="text-align:center; font-size:13px; color:#6c757d; margin-top:40px;">
    ⚡ Powered by Groq AI • Using llama-3.3-70b-versatile • Made with ❤️ by
    <a href="https://github.com/SanjayD11" target="_blank">Sanjay Dharmarajou</a>
    </div>
    """,
    unsafe_allow_html=True
)
