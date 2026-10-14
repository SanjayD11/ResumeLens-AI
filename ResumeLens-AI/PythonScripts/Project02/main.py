import os
import io
import re
import math
import html
from pathlib import Path

import streamlit as st
import PyPDF2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from groq import Groq

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    ListFlowable, ListItem, KeepTogether
)


# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="ResumeLens AI | Resume Analyzer",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ---------------- THEME / LAYOUT ----------------
# Keep the interface readable in Streamlit light and dark themes.
# Avoid forcing a page-wide background or text color; Streamlit's theme
# should control those. Explicitly style controls and headings for contrast.

st.markdown(
    """
    <style>
    .block-container {
        max-width: 900px;
        padding-top: 1.6rem;
        padding-bottom: 2.2rem;
    }

    .rl-brand {
        margin: 0 0 1rem 0;
        padding: 0;
    }

    .rl-subtitle {
        margin: 0.55rem 0 1.3rem 0;
        font-size: 0.98rem;
        line-height: 1.6;
        color: var(--text-color);
        opacity: 0.78;
    }

    .rl-section-title {
        font-size: 1.05rem;
        font-weight: 650;
        margin: 0 0 0.25rem 0;
    }

    .rl-help {
        font-size: 0.85rem;
        margin: 0 0 0.65rem 0;
        opacity: 0.75;
    }

    div[data-testid="stFileUploader"] {
        border: 1px solid var(--secondary-background-color);
        border-radius: 12px;
        padding: 0.65rem 0.75rem;
    }

    div[data-testid="stTextArea"] textarea {
        border-radius: 10px;
        line-height: 1.55;
    }

    div.stButton > button,
    div.stDownloadButton > button {
        min-height: 44px;
        border-radius: 9px;
        font-weight: 600;
        white-space: normal;
        height: auto;
        padding: 0.55rem 0.65rem;
    }

    div.stButton > button[kind="primary"] {
        background: #5146D8;
        border-color: #5146D8;
        color: #FFFFFF !important;
    }

    div.stButton > button[kind="primary"]:hover {
        background: #4338CA;
        border-color: #4338CA;
        color: #FFFFFF !important;
    }

    div.stButton > button[kind="secondary"],
    div.stDownloadButton > button {
        color: var(--text-color) !important;
    }

    div.stButton > button p,
    div.stDownloadButton > button p {
        color: inherit !important;
    }

    .rl-footer {
        border-top: 1px solid var(--secondary-background-color);
        margin-top: 2.2rem;
        padding-top: 1rem;
        text-align: center;
        font-size: 0.8rem;
        opacity: 0.78;
        line-height: 1.8;
    }

    .rl-footer a {
        color: #8177FF;
        text-decoration: none;
        font-weight: 600;
    }

    @media (max-width: 640px) {
        .block-container {
            padding: 1rem 0.8rem 1.5rem;
        }
        .rl-subtitle {
            font-size: 0.9rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------- BRAND HEADER ----------------

logo_path = Path(__file__).resolve().parent / "resumelens-brand.png"

if logo_path.is_file():
    # Center a reasonably sized logo without adding an artificial image frame.
    logo_col_left, logo_col, logo_col_right = st.columns([1, 2, 1])
    with logo_col:
        st.image(str(logo_path), use_container_width=True)
else:
    st.markdown("## ResumeLens AI")

st.markdown(
    """
    <div class="rl-subtitle">
        Analyze your resume, identify skill gaps, improve your content,
        and prepare for interviews with AI-powered insights.
    </div>
    """,
    unsafe_allow_html=True,
)
st.divider()


# ---------------- INPUTS ----------------

st.markdown('<div class="rl-section-title">Upload your resume</div>', unsafe_allow_html=True)
st.markdown('<div class="rl-help">PDF or TXT format</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Choose a resume file",
    type=["pdf", "txt"],
    label_visibility="collapsed",
)

st.markdown('<div class="rl-section-title">Target job description</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="rl-help">Optional, but recommended for a more relevant skill-match analysis.</div>',
    unsafe_allow_html=True,
)

job_description = st.text_area(
    "Job description",
    height=145,
    placeholder="Paste the target job description here...",
    label_visibility="collapsed",
)

st.write("")

col1, col2, col3 = st.columns(3, gap="small")
with col1:
    analyze = st.button("Analyze Resume", type="primary", use_container_width=True)
with col2:
    rewrite = st.button("Optimize Resume", use_container_width=True)
with col3:
    generate_questions = st.button("Interview Questions", use_container_width=True)


# ---------------- TEXT EXTRACTION ----------------

def extract_text_from_pdf(file_obj):
    reader = PyPDF2.PdfReader(file_obj)
    pages = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            pages.append(page_text)
    return "\n".join(pages)


def extract_text_from_file(file_obj):
    file_obj.seek(0)
    if file_obj.name.lower().endswith(".pdf"):
        return extract_text_from_pdf(io.BytesIO(file_obj.read()))
    return file_obj.read().decode("utf-8", errors="replace")


# ---------------- SCORING ----------------

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
        "developed", "built", "designed", "implemented",
        "optimized", "led", "improved", "automated",
    ]
    score += min(sum(verb in text_lower for verb in verbs) * 2, 15)

    bullets = sum(
        1 for line in text.splitlines()
        if line.strip().startswith(("-", "•", "*"))
    )
    score += 15 if bullets >= 12 else 8 if bullets >= 6 else 0
    return min(score, 100)


def calculate_skill_match(text, jd):
    if not jd.strip():
        return None, [], []

    resume_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", text.lower()))
    jd_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", jd.lower()))
    if not jd_words:
        return None, [], []

    matched = resume_words & jd_words
    missing = jd_words - resume_words
    return (
        round(len(matched) / len(jd_words) * 100, 1),
        sorted(matched)[:10],
        sorted(missing)[:10],
    )


def calculate_readability(text):
    sentences = [s for s in re.split(r"[.!?]", text) if s.strip()]
    words = re.findall(r"\b\w+\b", text)
    if not sentences or not words:
        return 0
    long_words = sum(1 for word in words if len(word) > 12)
    score = 100 - (len(words) / len(sentences) * 1.5) - (long_words / len(words) * 100)
    return max(min(round(score), 100), 30)


def get_grade(score):
    if score >= 85:
        return "A+"
    if score >= 70:
        return "A"
    if score >= 55:
        return "B"
    return "C"


# ---------------- CHART ----------------

def plot_radar(ats, skill, readability):
    categories = ["ATS Score", "Skill Match", "Readability"]
    values = [ats, skill if skill is not None else 0, readability]
    values += values[:1]
    angles = [n / float(len(categories)) * 2 * math.pi for n in range(len(categories))]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(5, 4.4), subplot_kw={"polar": True})
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")
    ax.plot(angles, values, linewidth=2, color="#7167E8")
    ax.fill(angles, values, alpha=0.18, color="#7167E8")
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=9)
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels([])
    ax.grid(alpha=0.25)
    ax.spines["polar"].set_alpha(0.25)
    ax.set_title("Resume Score Breakdown", fontsize=12, fontweight="bold", pad=20)
    fig.tight_layout()
    st.pyplot(fig, use_container_width=False)
    plt.close(fig)


# ---------------- MODEL ----------------

MODEL_NAME = "openai/gpt-oss-120b"


def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("AI service is not configured. Add GROQ_API_KEY to your Streamlit Secrets.")
        st.stop()
    return Groq(api_key=api_key)


def clean_model_output(content):
    """Normalize common HTML/Markdown artifacts returned by the model."""
    if not content:
        return ""

    text = str(content)

    # Convert common HTML line-break/block tags before removing remaining tags.
    text = re.sub(r"(?i)<\s*br\s*/?\s*>", "\n", text)
    text = re.sub(r"(?i)</\s*(p|div|h[1-6]|li|tr)\s*>", "\n", text)
    text = re.sub(r"(?i)<\s*li(?:\s+[^>]*)?>", "\n• ", text)
    text = re.sub(r"(?i)<\s*tr(?:\s+[^>]*)?>", "\n", text)
    text = re.sub(r"(?i)</\s*(td|th)\s*>", " | ", text)

    # Remove remaining HTML tags, then decode entities such as &amp; and &lt;.
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)

    # Handle escaped HTML fragments emitted literally by some model responses.
    text = re.sub(r"(?i)&lt;\s*br\s*/?\s*&gt;", "\n", text)
    text = re.sub(r"(?i)\\<\s*br\s*/?\s*\\>", "\n", text)
    text = re.sub(r"(?i)\\u003cbr\\u003e", "\n", text)

    # Remove leading/trailing whitespace and excessive blank lines.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n[ \t]*\n[ \t]*\n+", "\n\n", text)
    return text.strip()


def generate_ai_response(client, prompt, temperature=0.3):
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are ResumeLens AI, a professional resume reviewer. "
                    "Return clean Markdown only, not HTML or XML. Do not use HTML tags, "
                    "including br, div, p, or table tags. Use Markdown headings, bullets, "
                    "and simple tables only when necessary. Be accurate and actionable. "
                    "Never invent qualifications, experience, metrics, or achievements."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        max_completion_tokens=3000,
    )
    return clean_model_output(response.choices[0].message.content)


# ---------------- PDF TEXT NORMALIZATION ----------------

def normalize_pdf_text(value):
    """
    ReportLab's built-in Helvetica fonts do not support every Unicode glyph.
    Replace common problematic characters with safe equivalents to prevent
    black square glyphs in exported PDFs.
    """
    replacements = {
        "\u2022": "-",       # bullet
        "\u25aa": "-",       # small square bullet
        "\u25cf": "-",       # black circle
        "\u2011": "-",       # non-breaking hyphen
        "\u2010": "-",       # hyphen
        "\u2012": "-",       # figure dash
        "\u2013": "-",       # en dash
        "\u2014": "-",       # em dash
        "\u2212": "-",       # minus
        "\u2018": "'",       # left single quote
        "\u2019": "'",       # right single quote
        "\u201c": '"',       # left double quote
        "\u201d": '"',       # right double quote
        "\u2026": "...",     # ellipsis
        "\u00a0": " ",       # non-breaking space
        "\u200b": "",        # zero-width space
        "\u200c": "",
        "\u200d": "",
        "\ufeff": "",
        "\u2192": "->",
        "\u2190": "<-",
        "\u2264": "<=",
        "\u2265": ">=",
        "\u2248": "~",
        "\u00d7": "x",
        "\u2713": "[OK]",
        "\u2714": "[OK]",
        "\u2717": "[X]",
        "\u2764": "<3",
        "\u26a1": "",
        "\U0001f4ca": "",
        "\U0001f4c4": "",
        "\U0001f3a4": "",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)

    # Keep only characters supported by the built-in PDF fonts.
    value = value.encode("latin-1", errors="replace").decode("latin-1")
    value = re.sub(r"[ \t]+", " ", value)
    return value


# ---------------- PDF EXPORT ----------------

def markdown_to_pdf_bytes(markdown_text, title="ResumeLens AI Report"):
    """Render generated Markdown into a readable, paginated PDF."""
    markdown_text = normalize_pdf_text(markdown_text)

    # Convert Markdown tables into readable text rows rather than rendering
    # very wide, malformed tables that can contain continuation bullets.
    # This is especially useful for model output where bullets accidentally
    # spill into extra table rows.
    raw_lines = markdown_text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    converted_lines = []
    in_table = False
    for raw in raw_lines:
        stripped = raw.strip()
        if stripped.startswith("|") and "|" in stripped[1:]:
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            if all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells):
                continue
            if not in_table:
                converted_lines.append("")
                in_table = True
            if cells and cells[0] in ("#", "No.", "Number"):
                continue
            converted_lines.append(" - " + " | ".join(cell for cell in cells if cell))
        else:
            if in_table:
                converted_lines.append("")
                in_table = False
            converted_lines.append(raw)
    markdown_text = "\n".join(converted_lines)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.68 * inch,
        leftMargin=0.68 * inch,
        topMargin=0.68 * inch,
        bottomMargin=0.68 * inch,
        title=title,
        author="ResumeLens AI",
    )

    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            "RLTitle", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=19, leading=24, textColor=colors.HexColor("#20284A"),
            alignment=TA_LEFT, spaceAfter=12,
        ),
        "h1": ParagraphStyle(
            "RLH1", parent=base["Heading1"], fontName="Helvetica-Bold",
            fontSize=16, leading=20, textColor=colors.HexColor("#20284A"),
            spaceBefore=12, spaceAfter=7, keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "RLH2", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=13, leading=17, textColor=colors.HexColor("#5146D8"),
            spaceBefore=10, spaceAfter=5, keepWithNext=True,
        ),
        "h3": ParagraphStyle(
            "RLH3", parent=base["Heading3"], fontName="Helvetica-Bold",
            fontSize=11, leading=14, textColor=colors.HexColor("#303A58"),
            spaceBefore=8, spaceAfter=4, keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "RLBody", parent=base["BodyText"], fontName="Helvetica",
            fontSize=9.5, leading=14, textColor=colors.HexColor("#273248"),
            spaceAfter=6, alignment=TA_LEFT,
        ),
        "bullet": ParagraphStyle(
            "RLBullet", parent=base["BodyText"], fontName="Helvetica",
            fontSize=9.5, leading=13.5, textColor=colors.HexColor("#273248"),
            leftIndent=12, firstLineIndent=0, spaceAfter=3,
        ),
        "small": ParagraphStyle(
            "RLSmall", parent=base["BodyText"], fontName="Helvetica",
            fontSize=8, leading=10, textColor=colors.HexColor("#64748B"),
        ),
    }

    def escape_reportlab(text):
        # Normalize unsupported Unicode before escaping XML for ReportLab.
        text = normalize_pdf_text(text)
        text = html.unescape(text)
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        # Support basic Markdown emphasis and inline code after escaping.
        text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
        text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", text)
        text = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', text)
        return text

    story = [Paragraph(escape_reportlab(title), styles["title"])]

    lines = markdown_text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    paragraph_lines = []
    bullet_items = []
    table_rows = []

    def flush_paragraph():
        nonlocal paragraph_lines
        if paragraph_lines:
            joined = " ".join(part.strip() for part in paragraph_lines).strip()
            if joined:
                story.append(Paragraph(escape_reportlab(joined), styles["body"]))
            paragraph_lines = []

    def flush_bullets():
        nonlocal bullet_items
        if bullet_items:
            items = [
                ListItem(Paragraph(escape_reportlab(item), styles["bullet"]), leftIndent=12)
                for item in bullet_items
            ]
            story.append(ListFlowable(
                items, bulletType="bullet", start="circle",
                leftIndent=16, bulletFontName="Helvetica", bulletFontSize=7,
                spaceAfter=7,
            ))
            bullet_items = []

    def flush_table():
        nonlocal table_rows
        if not table_rows:
            return
        data = []
        for row in table_rows:
            cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-{3,}:?", c.replace(" ", "")) for c in cells):
                continue
            data.append([
                Paragraph(escape_reportlab(cell), styles["small"])
                for cell in cells
            ])
        if data:
            col_count = max(len(row) for row in data)
            normalized = [row + [""] * (col_count - len(row)) for row in data]
            usable_width = letter[0] - doc.leftMargin - doc.rightMargin
            table = Table(
                normalized,
                colWidths=[usable_width / col_count] * col_count,
                repeatRows=1,
                hAlign="LEFT",
            )
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EEF0FF")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#20284A")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D9DEEA")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.extend([Spacer(1, 4), table, Spacer(1, 8)])
        table_rows = []

    for raw_line in lines:
        line = raw_line.strip()

        if not line:
            flush_paragraph()
            flush_bullets()
            flush_table()
            story.append(Spacer(1, 3))
            continue

        if line.startswith("|") and "|" in line[1:]:
            flush_paragraph()
            flush_bullets()
            table_rows.append(line)
            continue
        else:
            flush_table()

        heading = re.match(r"^(#{1,3})\s+(.+)$", line)
        if heading:
            flush_paragraph()
            flush_bullets()
            level = len(heading.group(1))
            style = styles[f"h{level}"]
            story.append(Paragraph(escape_reportlab(heading.group(2)), style))
            continue

        if re.match(r"^[-*_]{3,}$", line):
            flush_paragraph()
            flush_bullets()
            story.append(Spacer(1, 6))
            continue

        bullet = re.match(r"^(?:[-*•]|\d+[.)])\s+(.+)$", line)
        if bullet:
            flush_paragraph()
            bullet_items.append(bullet.group(1))
            continue

        flush_bullets()
        paragraph_lines.append(line)

    flush_paragraph()
    flush_bullets()
    flush_table()

    def add_page_number(canvas_obj, doc_obj):
        canvas_obj.saveState()
        canvas_obj.setFont("Helvetica", 8)
        canvas_obj.setFillColor(colors.HexColor("#64748B"))
        canvas_obj.drawString(doc_obj.leftMargin, 0.38 * inch, "Generated by ResumeLens AI")
        canvas_obj.drawRightString(letter[0] - doc_obj.rightMargin, 0.38 * inch, f"Page {doc_obj.page}")
        canvas_obj.restoreState()

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    buffer.seek(0)
    return buffer.getvalue()


def show_pdf_download(content, filename, label, title):
    pdf_data = markdown_to_pdf_bytes(content, title=title)
    st.download_button(
        label=label,
        data=pdf_data,
        file_name=filename,
        mime="application/pdf",
        use_container_width=True,
    )


# ---------------- MAIN WORKFLOW ----------------

if analyze or rewrite or generate_questions:
    if not uploaded_file:
        st.warning("Please upload your resume before continuing.")
        st.stop()

    try:
        resume_text = extract_text_from_file(uploaded_file)
    except Exception:
        st.error("Unable to read this file. Please upload a valid PDF or TXT resume.")
        st.stop()

    if not resume_text.strip():
        st.error(
            "No readable text was found. Scanned image-only PDFs may need OCR "
            "before they can be analyzed."
        )
        st.stop()

    ats = calculate_ats_score(resume_text)
    skill, keywords, missing_keywords = calculate_skill_match(resume_text, job_description)
    readability = calculate_readability(resume_text)
    client = get_groq_client()

    # ---------------- ANALYSIS ----------------
    if analyze:
        st.divider()
        st.header("Resume Evaluation")

        m1, m2, m3 = st.columns(3)
        m1.metric("ATS Score", f"{ats}/100")
        m2.metric("Skill Match", f"{skill}%" if skill is not None else "N/A")
        m3.metric("Readability", f"{readability}/100")

        st.progress(ats / 100)
        st.success(f"Overall Resume Grade: {get_grade(ats)}")

        if skill is None:
            st.info("Add a job description to calculate a skill-match score.")

        st.subheader("Score Breakdown")
        plot_radar(ats, skill, readability)

        if keywords:
            st.subheader("Matched Keywords")
            st.write(", ".join(keywords))

        if missing_keywords:
            st.subheader("Potentially Missing Keywords")
            st.write(", ".join(missing_keywords))

        prompt = f"""
Review the resume as a professional career advisor.

Use Markdown only. Do not return HTML tags or encoded HTML.
Include:
1. Overall assessment
2. Key strengths
3. Areas to improve
4. Specific, truthful bullet-point improvements
5. ATS formatting suggestions
6. Three prioritized next steps

Do not invent qualifications, experience, numbers, or achievements.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description.strip() or "Not provided"}
"""
        try:
            with st.spinner("Analyzing your resume..."):
                feedback = generate_ai_response(client, prompt)
            st.subheader("AI Resume Feedback")
            st.markdown(feedback)
            show_pdf_download(
                feedback,
                "resume_analysis_report.pdf",
                "Download Analysis Report (PDF)",
                "Resume Analysis Report",
            )
        except Exception as exc:
            st.error("Analysis could not be completed. Check model access and try again.")
            st.caption(str(exc))

    # ---------------- RESUME OPTIMIZATION ----------------
    if rewrite:
        st.divider()
        st.header("Optimized Resume")

        prompt = f"""
Rewrite the resume into a polished, ATS-friendly resume.
Return clean Markdown only, not HTML.

Requirements:
- Use clear headings and concise bullet points.
- Improve action verbs and professional wording.
- Tailor it to the target job description when provided.
- Preserve all factual details from the original.
- Never invent employers, dates, qualifications, metrics, or achievements.
- Use placeholders such as [add verified result] when information is missing.
- Return only the complete revised resume, without a lengthy introduction.

ORIGINAL RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description.strip() or "Not provided"}
"""
        try:
            with st.spinner("Optimizing your resume..."):
                optimized_resume = generate_ai_response(client, prompt, temperature=0.4)
            st.markdown(optimized_resume)
            show_pdf_download(
                optimized_resume,
                "optimized_resume.pdf",
                "Download Optimized Resume (PDF)",
                "Optimized Resume",
            )
        except Exception as exc:
            st.error("Resume optimization failed. Check model access and try again.")
            st.caption(str(exc))

    # ---------------- INTERVIEW PREPARATION ----------------
    if generate_questions:
        st.divider()
        st.header("Interview Preparation")

        prompt = f"""
Generate 15 interview questions based on the resume and target role:
- 10 technical or role-specific questions
- 5 HR and behavioral questions

Use clean Markdown only. Do not return HTML, encoded HTML, or Markdown tables.
Format every question as a numbered heading or numbered list item.
Under each question, use separate short bullet points for:
- What the interviewer evaluates
- Suggested answer points
Keep each question and its answer points together as a normal list, never as a table.
Base questions on the candidate's actual resume; do not assume unlisted experience.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description.strip() or "Not provided"}
"""
        try:
            with st.spinner("Preparing interview questions..."):
                questions = generate_ai_response(client, prompt, temperature=0.5)
            st.markdown(questions)
            show_pdf_download(
                questions,
                "interview_questions.pdf",
                "Download Interview Questions (PDF)",
                "Interview Preparation Questions",
            )
        except Exception as exc:
            st.error("Interview question generation failed. Check model access and try again.")
            st.caption(str(exc))


# ---------------- FOOTER ----------------

st.markdown(
    """
    <div class="rl-footer">
        Powered by Groq AI | GPT-OSS 120B<br>
        Made with love by
        <a href="https://github.com/SanjayD11" target="_blank"
           rel="noopener noreferrer">Sanjay Dharmarajou</a>
    </div>
    """,
    unsafe_allow_html=True,
)
