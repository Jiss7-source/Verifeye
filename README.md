# VerifEYE - Intelligent Expense Auditor

## The Problem
A lot of fake, out-of-policy expenses pass through manual team approvals every day, leaking significant company resources. Auditing takes massive manual effort which companies struggle to keep up with, leading to delayed reimbursements and lack of compliance visibility.

## The Solution
VerifEYE provides an AI-powered compliance engine that uses an intelligent LLM Vision API (Groq Llama 90B Vision) to ingest digital receipts and validate their contextual business purpose directly against custom company policies. A simple traffic-light system combined with an explicit compliance ledger makes detecting and blocking anomalous or prohibited outlays fully automated, giving peace of mind and time back to finance teams.

## Tech Stack
- **Python** (Core application logic)
- **Streamlit** (Frontend interface and state management)
- **Groq API / Llama 3.2 90B Vision** (AI intelligence, reasoning and OCR)
- **SQLite** (Human-in-the-loop expense ledger database)

## Setup Instructions
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Configure APIs:**
   Create a `.streamlit/secrets.toml` or `.env` file in the project root containing your Groq API key:
   ```toml
   # .streamlit/secrets.toml
   GROQ_API_KEY = "your_groq_api_key_here"
   ```
3. **Run the project locally:**
   Start the Streamlit application using the command below:
   ```bash
   streamlit run app.py
   ```
   *The application will open automatically in your default web browser.*
