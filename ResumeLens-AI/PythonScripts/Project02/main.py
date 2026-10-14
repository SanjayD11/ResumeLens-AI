
import os
import io
import re
import math
from pathlib import Path

import streamlit as st
import PyPDF2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from groq import Groq


# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="ResumeLens AI | Resume Analyzer",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ---------------- PROFESSIONAL LIGHT THEME ----------------

st.markdown(
    """
    <style>
    :root {
        --primary: #5146D8;
        --primary-hover: #4338CA;
        --navy: #17213B;
        --muted: #64748B;
        --border: #E2E8F0;
        --surface: #F8FAFC;
    }

    .stApp {
        background: #FFFFFF;
        color: var(--navy);
    }

    .block-container {
        max-width: 900px;
        padding-top: 2rem;
        padding-bottom: 2.5rem;
    }

    h1, h2, h3 {
        color: var(--navy) !important;
        letter-spacing: -0.025em;
    }

    p, label, .stMarkdown {
        color: var(--navy);
    }

    .brand-subtitle {
        color: #64748B;
        font-size: 15px;
        line-height: 1.7;
        margin-top: 8px;
        margin-bottom: 26px;
    }

    .section-heading {
        color: #17213B;
        font-size: 17px;
        font-weight: 650;
        margin-bottom: 4px;
    }

    .section-help {
        color: #64748B;
        font-size: 13px;
        margin-bottom: 12px;
    }

    div[data-testid="stFileUploader"] {
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 12px;
        background: #F8FAFC;
    }

    div[data-testid="stTextArea"] textarea {
        border: 1px solid #DCE3ED;
        border-radius: 10px;
        background: #FFFFFF;
        color: #17213B;
        line-height: 1.6;
    }

    div[data-testid="stTextArea"] textarea:focus {
        border-color: #5146D8;
        box-shadow: 0 0 0 1px #5146D8;
    }

    div.stButton > button {
        min-height: 44px;
        border-radius: 9px;
        border: 1px solid #DCE3ED;
        font-weight: 600;
        font-size: 13px;
        transition: border-color 0.15s ease;
    }

    div.stButton > button:hover {
        border-color: #5146D8;
        color: #5146D8;
    }

    div.stButton > button[kind="primary"] {
        background: #5146D8;
        color: #FFFFFF;
        border: 1px solid #5146D8;
    }

    div.stButton > button[kind="primary"]:hover {
        background: #4338CA;
        color: #FFFFFF;
    }

    div[data-testid="stProgressBar"] > div > div {
        background: #5146D8;
    }

    div[data-testid="stMetric"] {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px;
    }

    hr {
        border-color: #E9EDF4;
    }

    .app-footer {
        border-top: 1px solid #E9EDF4;
        margin-top: 40px;
        padding-top: 18px;
        text-align: center;
        color: #64748B;
        font-size: 12px;
        line-height: 1.8;
    }

    .app-footer a {
        color: #5146D8;
        text-decoration: none;
        font-weight: 600;
    }

    @media (max-width: 640px) {
        .block-container {
            padding: 1.2rem 1rem 2rem;
        }

        .brand-subtitle {
            font-size: 14px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------- BRAND HEADER ----------------

logo_path = Path(__file__).resolve().parent / "resumelens-brand.png"

if logo_path.is_file():
    st.image(str(logo_path), width=320)
else:
    st.markdown("# ResumeLens AI")
    st.caption("AI-powered resume analysis and optimization")

st.markdown(
    """
    <div class="brand-subtitle">
        Analyze your resume, identify skill gaps, improve your content,
        and prepare for interviews with AI-powered insights.
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()


# ---------------- INPUT SECTION ----------------

st.markdown(
    '<div class="section-heading">Upload your resume</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-help">Supported formats: PDF and TXT</div>',
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader(
    "Choose a resume file",
    type=["pdf", "txt"],
    label_visibility="collapsed",
)

st.markdown("")

st.markdown(
    '<div class="section-heading">Target job description</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-help">'
    "Add the job description to get a more relevant skill-match analysis."
    "</div>",
    unsafe_allow_html=True,
)

job_description = st.text_area(
    "Job description",
    height=150,
    placeholder=(
        "Paste the job description here...\n\n"
        "Include the required skills, responsibilities, and qualifications."
    ),
    label_visibility="collapsed",
)

st.markdown("")


# ---------------- ACTION BUTTONS ----------------

col1, col2, col3 = st.columns(3, gap="small")

with col1:
    analyze = st.button(
        "Analyze Resume",
        type="primary",
        use_container_width=True,
    )

with col2:
    rewrite = st.button(
        "Optimize Resume",
        use_container_width=True,
    )

with col3:
    generate_questions = st.button(
        "Interview Questions",
        use_container_width=True,
    )


# ---------------- RESUME PROCESSING ----------------

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    pages = []

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            pages.append(page_text)

    return "\n".join(pages)


def extract_text_from_file(file):
    file.seek(0)

    if file.name.lower().endswith(".pdf"):
        return extract_text_from_pdf(io.BytesIO(file.read()))

    return file.read().decode("utf-8", errors="replace")


# ---------------- ATS SCORE ----------------

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

    sections = {
        "experience": 10,
        "skills": 10,
        "education": 8,
        "projects": 6,
        "summary": 6,
    }

    for section, points in sections.items():
        if section in text_lower:
            score += points

    verbs = [
        "developed",
        "built",
        "designed",
        "implemented",
        "optimized",
        "led",
        "improved",
        "automated",
    ]

    score += min(
        sum(verb in text_lower for verb in verbs) * 2,
        15,
    )

    bullets = sum(
        1
        for line in text.splitlines()
        if line.strip().startswith(("-", "•"))
    )

    if bullets >= 12:
        score += 15
    elif bullets >= 6:
        score += 8

    return min(score, 100)


# ---------------- SKILL MATCH ----------------

def calculate_skill_match(text, jd):
    if not jd.strip():
        return None, [], []

    resume_words = set(
        re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    )

    jd_words = set(
        re.findall(r"\b[a-zA-Z]{3,}\b", jd.lower())
    )

    if not jd_words:
        return None, [], []

    matched = resume_words & jd_words
    missing = jd_words - resume_words

    score = round(len(matched) / len(jd_words) * 100, 1)

    return score, sorted(matched)[:10], sorted(missing)[:10]


# ---------------- READABILITY ----------------

def calculate_readability(text):
    sentences = [
        sentence
        for sentence in re.split(r"[.!?]", text)
        if sentence.strip()
    ]

    words = re.findall(r"\b\w+\b", text)

    if not sentences or not words:
        return 0

    long_words = sum(1 for word in words if len(word) > 12)

    score = (
        100
        - (len(words) / len(sentences) * 1.5)
        - (long_words / len(words) * 100)
    )

    return max(min(round(score), 100), 30)


# ---------------- RESUME GRADE ----------------

def get_grade(score):
    if score >= 85:
        return "A+"
    elif score >= 70:
        return "A"
    elif score >= 55:
        return "B"
    return "C"


# ---------------- RADAR CHART ----------------

def plot_radar(ats, skill, readability):
    categories = ["ATS Score", "Skill Match", "Readability"]
    values = [ats, skill if skill is not None else 0, readability]

    values += values[:1]

    angles = [
        n / float(len(categories)) * 2 * math.pi
        for n in range(len(categories))
    ]
    angles += angles[:1]

    fig, ax = plt.subplots(
        figsize=(5, 4.5),
        subplot_kw={"polar": True},
    )

    # Match the clean light interface.
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    ax.plot(
        angles,
        values,
        color="#5146D8",
        linewidth=2,
    )

    ax.fill(
        angles,
        values,
        color="#5146D8",
        alpha=0.15,
    )

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(
        categories,
        fontsize=10,
        fontweight="medium",
        color="#17213B",
    )

    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels([])
    ax.grid(color="#E2E8F0", linewidth=0.8)

    ax.spines["polar"].set_color("#E2E8F0")

    ax.set_title(
        "Resume Score Breakdown",
        fontsize=12,
        fontweight="bold",
        color="#17213B",
        pad=22,
    )

    plt.tight_layout()
    st.pyplot(fig, use_container_width=False)
    plt.close(fig)


# ---------------- GROQ CLIENT ----------------

MODEL_NAME = "openai/gpt-oss-120b"


def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        st.error(
            "The AI service is not configured. "
            "Please set GROQ_API_KEY in your deployment secrets."
        )
        st.stop()

    return Groq(api_key=api_key)


def generate_ai_response(client, prompt, temperature=0.3):
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are ResumeLens AI, a professional career "
                    "advisor and resume specialist. Give accurate, "
                    "specific, actionable advice. Never invent "
                    "experience, qualifications, or achievements. "
                    "Clearly distinguish suggestions from verified facts."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        max_completion_tokens=3000,
    )

    return response.choices[0].message.content.strip()


# ---------------- MAIN ACTIONS ----------------

if analyze or rewrite or generate_questions:

    if not uploaded_file:
        st.warning("Please upload your resume before continuing.")
        st.stop()

    try:
        resume_text = extract_text_from_file(uploaded_file)
    except Exception as exc:
        st.error(f"Unable to read the uploaded file: {exc}")
        st.stop()

    if not resume_text.strip():
        st.error(
            "No readable text was found. "
            "If this is a scanned PDF, use a text-based PDF or TXT file."
        )
        st.stop()

    ats = calculate_ats_score(resume_text)
    skill, keywords, missing_keywords = calculate_skill_match(
        resume_text,
        job_description,
    )
    readability = calculate_readability(resume_text)

    client = get_groq_client()

    # ---------------- ANALYZE MODE ----------------

    if analyze:
        st.divider()
        st.header("Resume Evaluation")

        metric1, metric2, metric3 = st.columns(3)

        with metric1:
            st.metric("ATS Score", f"{ats}/100")

        with metric2:
            st.metric(
                "Skill Match",
                f"{skill}%" if skill is not None else "N/A",
            )

        with metric3:
            st.metric("Readability", f"{readability}/100")

        st.progress(ats / 100)
        st.success(f"Overall Resume Grade: {get_grade(ats)}")

        if skill is None:
            st.info(
                "Add a target job description to calculate "
                "your skill-match score."
            )

        st.subheader("Score Breakdown")
        plot_radar(ats, skill, readability)

        if keywords:
            st.subheader("Matched Keywords")
            st.write(", ".join(keywords))

        if missing_keywords:
            st.subheader("Potentially Missing Keywords")
            st.write(", ".join(missing_keywords))

        st.divider()
        st.subheader("AI Resume Feedback")

        prompt = f"""
Review the resume below as a professional resume specialist.

Provide:
1. Overall assessment.
2. Key strengths.
3. Specific weaknesses and improvements.
4. Suggestions for stronger, truthful achievement statements.
5. Formatting and ATS-readability recommendations.
6. Prioritized next steps.

Do not invent facts or achievements. Identify any information
the candidate should supply instead of making it up.

RESUME:
{resume_text}

TARGET JOB DESCRIPTION:
{job_description.strip() or "Not provided"}
"""

        try:
            with st.spinner("Analyzing your resume..."):
                feedback = generate_ai_response(client, prompt)

            st.markdown(feedback)

        except Exception as exc:
            st.error(
                "The AI analysis could not be completed. "
                "Please check your Groq model access and try again."
            )
            st.caption(str(exc))

    # ---------------- REWRITE MODE ----------------

    if rewrite:
        st.divider()
        st.header("Optimized Resume")

        rewrite_prompt = f"""
Rewrite the following resume into a polished, ATS-friendly resume.

Requirements:
- Use clear section headings and concise bullet points.
- Improve wording and action verbs.
- Emphasize relevant skills for the target role.
- Preserve all factual details.
- Never invent metrics, job titles, experience, certifications,
  education, or achievements.
- If a metric would improve a bullet, use a placeholder such as
  [add verified result] instead of fabricating a number.
- If no job description is supplied, optimize for general clarity
  and professional presentation.
- Return the complete revised resume in Markdown.
- Do not include a long explanation before the resume.

ORIGINAL RESUME:
{resume_text}

TARGET JOB DESCRIPTION:
{job_description.strip() or "Not provided"}
"""

        try:
            with st.spinner("Optimizing your resume..."):
                optimized_resume = generate_ai_response(
                    client,
                    rewrite_prompt,
                    temperature=0.4,
                )

            st.markdown(optimized_resume)

            st.download_button(
                label="Download Optimized Resume (.md)",
                data=optimized_resume,
                file_name="optimized_resume.md",
                mime="text/markdown",
                use_container_width=True,
            )

        except Exception as exc:
            st.error(
                "Resume optimization failed. "
                "Please check your Groq model access and try again."
            )
            st.caption(str(exc))

    # ---------------- INTERVIEW QUESTIONS ----------------

    if generate_questions:
        st.divider()
        st.header("Interview Preparation")

        interview_prompt = f"""
Generate 15 interview questions based on the resume and target role:
- 10 technical or role-specific questions.
- 5 HR and behavioral questions.

For each question:
- Include a short note about what the interviewer is evaluating.
- For selected questions, suggest key points a strong answer should cover.
- Base questions on the candidate's actual skills and experience.
- Do not assume experience that is not present in the resume.

Organize the response under clear headings.

RESUME:
{resume_text}

TARGET JOB DESCRIPTION:
{job_description.strip() or "Not provided"}
"""

        try:
            with st.spinner("Preparing interview questions..."):
                questions = generate_ai_response(
                    client,
                    interview_prompt,
                    temperature=0.5,
                )

            st.markdown(questions)

            st.download_button(
                label="Download Interview Questions (.md)",
                data=questions,
                file_name="resume_interview_questions.md",
                mime="text/markdown",
                use_container_width=True,
            )

        except Exception as exc:
            st.error(
                "Interview question generation failed. "
                "Please check your Groq model access and try again."
            )
            st.caption(str(exc))


# ---------------- FOOTER ----------------

st.markdown(
    """
    <div class="app-footer">
        Powered by Groq AI · GPT-OSS 120B<br>
        Made with ♥ by
        <a href="https://github.com/SanjayD11"
           target="_blank" rel="noopener noreferrer">
            Sanjay Dharmarajou
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)
