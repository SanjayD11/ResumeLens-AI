import streamlit as st
import PyPDF2
import io
import re
import os
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
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
    "<p style='font-size:18px; color:#6c757d;'>Smarter, AI-powered resume analysis & optimization platform.</p>",
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])
job_description = st.text_area(
    "Paste the job description you are targeting (recommended for accurate scoring)",
    height=150
)

col1, col2, col3 = st.columns(3)
with col1:
    analyze = st.button("📊 Analyze Resume")
with col2:
    rewrite = st.button("✨ Generate Optimized Resume")
with col3:
    generate_questions = st.button("🎤 Generate Interview Questions")

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
        return None, [], []

    resume_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", text.lower()))
    jd_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", jd.lower()))

    matched = resume_words & jd_words
    missing = jd_words - resume_words

    return (
        round(len(matched) / len(jd_words) * 100, 1),
        sorted(matched)[:10],
        sorted(missing)[:10]
    )

def calculate_readability(text):
    sentences = [s for s in re.split(r"[.!?]", text) if s.strip()]
    words = re.findall(r"\b\w+\b", text)
    if not sentences or not words:
        return 0
    score = 100 - ((len(words)/len(sentences))*1.5) - ((len([w for w in words if len(w)>12])/len(words))*100)
    return max(min(round(score),100),30)

def get_grade(score):
    if score >= 85:
        return "A+"
    elif score >= 70:
        return "A"
    elif score >= 55:
        return "B"
    else:
        return "C"

def plot_radar(ats, skill, readability):
    categories = ['ATS', 'Skill Match', 'Readability']
    values = [ats, skill if skill else 0, readability]
    values += values[:1]

    angles = [n / float(len(categories)) * 2 * math.pi for n in range(len(categories))]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(4,4), subplot_kw=dict(polar=True))
    fig.patch.set_alpha(0)  # Transparent background
    ax.plot(angles, values)
    ax.fill(angles, values, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    ax.set_yticklabels([])
    ax.set_title("Resume Score Breakdown", size=11)

    st.pyplot(fig)

# ---------------- MAIN LOGIC ----------------

if (analyze or rewrite or generate_questions) and uploaded_file:

    resume_text = extract_text_from_file(uploaded_file)

    if not resume_text.strip():
        st.error("No readable content found.")
        st.stop()

    ats = calculate_ats_score(resume_text)
    skill, keywords, missing_keywords = calculate_skill_match(resume_text, job_description)
    readability = calculate_readability(resume_text)

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        st.error("Server configuration error.")
        st.stop()

    client = Groq(api_key=GROQ_API_KEY)

# ---------------- ANALYZE MODE ----------------

    if analyze:
        st.markdown("## 📌 Resume Evaluation Metrics")
        st.progress(ats/100); st.write(f"**ATS Score:** {ats}/100")
        st.progress((skill or 0)/100); st.write(f"**Skill Match:** {skill if skill else 'N/A'}%")
        st.progress(readability/100); st.write(f"**Readability:** {readability}/100")

        st.success(f"🏆 Overall Resume Grade: {get_grade(ats)}")

        plot_radar(ats, skill, readability)

        if keywords:
            st.success("Matched Keywords")
            st.write(", ".join(keywords))

        if missing_keywords:
            st.error("Missing Important Keywords")
            st.write(", ".join(missing_keywords))

        st.divider()

        prompt = f"""
You are a professional resume reviewer.

Analyze the following resume thoroughly and provide structured feedback.

Resume:
{resume_text}

Job Description:
{job_description if job_description else 'Not provided'}
"""

        with st.spinner("🤖 AI is analyzing your resume..."):
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2000
            )

        ai_feedback = completion.choices[0].message.content.strip()
        st.markdown("### 📊 AI Feedback")
        st.markdown(ai_feedback)

# ---------------- REWRITE MODE ----------------

    if rewrite:
        st.markdown("## ✨ Optimized Resume Version")

        rewrite_prompt = f"""
You are an expert ATS resume optimizer.

Rewrite the resume to better match the job description.
- Improve bullet points using strong action verbs
- Add measurable achievements
- Optimize keywords
- Keep it concise and professional

Resume:
{resume_text}

Job Description:
{job_description}
"""

        with st.spinner("✍️ Optimizing your resume..."):
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": rewrite_prompt}],
                temperature=0.4,
                max_tokens=2000
            )

        optimized_resume = completion.choices[0].message.content.strip()
        st.markdown(optimized_resume)

# ---------------- INTERVIEW QUESTIONS MODE ----------------

    if generate_questions:
        st.markdown("## 🎤 Interview Questions Based on Your Resume")

        interview_prompt = f"""
Generate 10 technical and 5 HR interview questions 
based on this resume and job description.

Resume:
{resume_text}

Job Description:
{job_description if job_description else 'Not provided'}
"""

        with st.spinner("🎤 Generating interview questions..."):
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": interview_prompt}],
                temperature=0.5,
                max_tokens=2000
            )

        questions = completion.choices[0].message.content.strip()
        st.markdown(questions)

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
