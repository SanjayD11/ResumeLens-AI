📄 ResumeLens-AI

AI-Powered Resume Analyzer (Powered by LLaMA 3)

ResumeLens-AI is an intelligent resume analysis application built using Python and Streamlit, designed to help users evaluate and improve their resumes.
The system extracts content from PDF resumes and uses LLaMA 3 via Ollama to provide structured insights, strengths, and improvement suggestions.

🔥 Note: This project is powered by LLaMA 3

🚀 Features

📂 Upload resume in PDF format

🧠 AI-based resume analysis using LLaMA 3

📊 Strengths & weaknesses detection

✍️ Skill and content improvement suggestions

🧾 Clean and interactive Streamlit UI

📄 PDF parsing and processing

🖨️ Resume report generation (PDF)

🛠️ Tech Stack
Category	Technology
Language	Python
UI	Streamlit
AI Model	LLaMA 3 (via Ollama)
PDF Processing	PyPDF2
PDF Generation	ReportLab
Environment	Virtualenv
⚙️ Setup & Installation : 

1️⃣ Clone the Repository
git clone https://github.com/YOUR_USERNAME/ResumeLens-AI.git
cd ResumeLens-AI/PythonScripts/Project02

2️⃣ Create & Activate Virtual Environment
python -m venv venv


Windows

.\venv\Scripts\Activate


macOS / Linux

source venv/bin/activate

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Install Ollama & LLaMA 3

Download and install Ollama:

https://ollama.com


Pull the LLaMA 3 model:

ollama pull llama3


Ensure Ollama is running in the background.

5️⃣ Run the Application
streamlit run main.py

📌 Project Structure
Project02/
│── main.py
│── logo.png
│── .gitignore
│── venv/   (ignored)
│── assets/

🔐 Model Disclosure : 

✔ Powered exclusively by LLaMA 3
✔ Runs locally using Ollama
✔ No external APIs
✔ No OpenAI / GPT usage

🎯 Use Cases : 

Students improving resumes

Job seekers preparing for interviews

Resume screening & evaluation practice

AI + NLP academic projects

📈 Resume Value :

Demonstrates real AI integration

Uses local LLMs (LLaMA 3) — highly valued

Practical Streamlit deployment

Clean software architecture

🤝 Contributing :

Pull requests are welcome.
For major changes, please open an issue first.

🙌 Acknowledgements :

Meta AI — LLaMA 3

Ollama

Streamlit Community
