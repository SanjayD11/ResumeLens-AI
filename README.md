<p align="center">
  <img src="assets/banner.png" alt="ResumeLens AI Banner" width="100%" />
</p>

<h1 align="center">📄 ResumeLens AI</h1>

<p align="center">
  <strong>AI-Powered Resume Analyzer & Optimizer</strong><br/>
  <em>Scan. Score. Strengthen. Land the Interview.</em>
</p>

<p align="center">
  <a href="https://resumelens-ai-zbmgxvbryjqi4ifytqh3kf.streamlit.app/"><img src="https://img.shields.io/badge/🚀_Live_App-Streamlit_Cloud-FF4B4B?style=for-the-badge" alt="Live App" /></a>
  <a href="https://github.com/SanjayD11/resumelens-ai"><img src="https://img.shields.io/badge/Source-GitHub-181717?logo=github&style=for-the-badge" alt="GitHub" /></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white&style=for-the-badge" alt="Python" />
  <img src="https://img.shields.io/badge/Streamlit-1.x-FF4B4B?logo=streamlit&logoColor=white&style=for-the-badge" alt="Streamlit" />
  <img src="https://img.shields.io/badge/Groq_API-LPU_Inference-F55036?logo=groq&logoColor=white&style=for-the-badge" alt="Groq" />
  <img src="https://img.shields.io/badge/LLaMA_3.3-70B-7C3AED?logo=meta&logoColor=white&style=for-the-badge" alt="LLaMA 3.3" />
</p>

---

## 🧿 What is ResumeLens AI?

**ResumeLens AI** is a production-ready web application that uses large language models to deeply analyze resumes, score them against job descriptions, and provide actionable intelligence to improve hiring outcomes.

Upload a resume. Paste a job description. Get instant AI-driven insights — from ATS compatibility scores to a fully rewritten, optimized resume — all within seconds.

> 💡 Built as a real-world SaaS demonstration of LLM-powered document intelligence.

<br/>

## ✨ Features

| Module | Capability |
|---|---|
| **📊 ATS Score Engine** | Calculates an ATS compatibility score (0–100) based on keyword density, formatting, and structure |
| **🎯 Skill Match Analysis** | Compares resume skills against job description requirements and returns a match percentage |
| **📖 Readability Scoring** | Evaluates language clarity, sentence structure, and professional tone |
| **📈 Radar Visualization** | Interactive radar chart breaking down performance across multiple evaluation axes |
| **✍️ AI Resume Rewriter** | Rewrites bullet points with quantified achievements, power verbs, and ATS-friendly keywords |
| **🎤 Interview Prep** | Generates 10 technical + 5 HR questions tailored to the resume and target role |
| **📥 PDF Report Export** | One-click downloadable PDF containing the full analysis, scores, and recommendations |
| **🏆 Overall Grade** | Composite letter grade summarizing resume quality at a glance |

<br/>

## 🧠 AI Architecture

```
┌──────────────────────────────────────────────────┐
│                  User Interface                  │
│              (Streamlit Frontend)                 │
└────────────────────┬─────────────────────────────┘
                     │
          ┌──────────▼──────────┐
          │   PDF Parser Layer  │
          │      (PyPDF2)       │
          └──────────┬──────────┘
                     │
     ┌───────────────▼───────────────┐
     │    Prompt Engineering Layer   │
     │  Structured analysis prompts  │
     │  for each evaluation module   │
     └───────────────┬───────────────┘
                     │
          ┌──────────▼──────────┐
          │     Groq API        │
          │ LLaMA 3.3 (70B)    │
          │ LPU Inference       │
          └──────────┬──────────┘
                     │
     ┌───────────────▼───────────────┐
     │    Response Processing &      │
     │    Visualization Engine       │
     │  (Matplotlib · ReportLab)     │
     └───────────────────────────────┘
```

| Component | Technology |
|---|---|
| **Frontend & Backend** | Streamlit |
| **Language** | Python 3.10+ |
| **LLM Provider** | Groq (LPU Cloud Inference) |
| **Model** | `llama-3.3-70b-versatile` |
| **PDF Parsing** | PyPDF2 |
| **PDF Generation** | ReportLab |
| **Data Visualization** | Matplotlib |
| **Deployment** | Streamlit Community Cloud |

<br/>

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- A free [Groq API key](https://console.groq.com/)

### Installation

```bash
# 1 · Clone the repository
git clone https://github.com/SanjayD11/resumelens-ai.git
cd resumelens-ai

# 2 · Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3 · Install dependencies
pip install -r requirements.txt
```

### 🔐 Environment Setup

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

> You can obtain a free API key from the [Groq Console](https://console.groq.com/).

### Run Locally

```bash
streamlit run main.py
```

The app will launch at `http://localhost:8501`.

<br/>

## 📂 Project Structure

```
resumelens-ai/
├── main.py                  # Application entry point & Streamlit UI
├── requirements.txt         # Python dependencies
├── .env                     # API key (not committed)
├── .gitignore
└── README.md
```

<br/>

## 🎯 Use Cases

| Audience | How They Use It |
|---|---|
| **Job Seekers** | Optimize resumes before applying to beat ATS filters |
| **Students** | Get professional-grade feedback on first resumes |
| **Career Coaches** | Quickly audit client resumes with data-backed insights |
| **Developers** | Reference architecture for LLM-powered SaaS applications |
| **Recruiters** | Understand what makes a resume score high or low |

<br/>

## 📸 Screenshots

> Screenshots of the live application showcasing the analysis dashboard, radar chart, and PDF report.

<!-- Add your screenshots here -->
<!-- ![Dashboard](assets/screenshot_dashboard.png) -->
<!-- ![Radar Chart](assets/screenshot_radar.png) -->
<!-- ![PDF Report](assets/screenshot_report.png) -->

<br/>

## 🛣️ Roadmap

- [x] Core ATS scoring engine
- [x] AI-powered resume rewriting
- [x] Interview question generation
- [x] PDF report export
- [ ] Multi-page resume support
- [ ] LinkedIn profile import
- [ ] Side-by-side resume comparison
- [ ] Batch analysis mode

<br/>

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to open an issue or submit a pull request.

<br/>

---

<p align="center">
  Built with ♥ by <a href="https://github.com/SanjayD11"><strong>Sanjay Dharmarajou</strong></a>
</p>

<p align="center">
  <a href="https://github.com/SanjayD11">GitHub</a> · <a href="https://www.linkedin.com/in/sanjay-d-354776353">LinkedIn</a> · <a href="mailto:sanjayraju5164@gmail.com">Email</a> · <a href="https://sanjayd.vercel.app">Portfolio</a>
</p>
