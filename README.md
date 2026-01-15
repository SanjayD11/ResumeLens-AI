📄 ResumeLens-AI :


AI-Powered Resume Analyzer (LLaMA 3)
ResumeLens-AI is a Python-based web application that analyzes resumes in PDF format and provides AI-driven insights to improve resume quality.
The application uses LLaMA 3 via Ollama for all language processing and runs entirely locally without external APIs.

⚙️ Model Disclosure :
- Uses LLaMA 3 exclusively
- Runs locally via Ollama
- No OpenAI / GPT models
- No cloud-based APIs

✨ Features :
- Upload and analyze resumes in PDF format
- AI-generated strengths and improvement suggestions
- Skill and content evaluation
- Interactive Streamlit-based UI
- Resume analysis report generation

🛠️ Technology Stack :
- Programming Language: Python
- Frontend: Streamlit
- Large Language Model: LLaMA 3 (via Ollama)
- PDF Processing: PyPDF2
- PDF Generation: ReportLab
- Environment: Virtual Environment (venv)

🚀 Installation & Setup :
- Clone the Repository
- Create and Activate Virtual Environment
python -m venv venv
- Windows
.\venv\Scripts\Activate
- macOS / Linux
source venv/bin/activate
- Install Dependencies
pip install -r requirements.txt



🧠 LLaMA 3 Setup (Required) :
- Install Ollama → https://ollama.com
- Pull the LLaMA 3 model:
ollama pull llama3
- Ensure Ollama is running in the background before starting the app

▶️ Run the Application :
streamlit run main.py



📂 Project Structure :

Project02/
├── main.py
└── venv/   (ignored)



🎯 Use Cases :

- Resume evaluation for students and job seekers
- AI-assisted resume improvement
- Demonstration of LLM-powered NLP applications

👨‍💻 Author :
- Developed by Sanjay
