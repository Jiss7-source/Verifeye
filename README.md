# VerifEYE — Expense Auditor

## The Problem
Manual expense auditing is slow, error-prone, and susceptible to fraud or policy violations. Finance teams spend countless hours verifying receipts against complex corporate policies, leading to delayed reimbursements and operational friction.

## The Solution
VerifEYE is an AI-powered compliance engine that automates receipt auditing. By leveraging advanced Vision language models, it instantly extracts receipt data, cross-references it against customizable corporate policies, and routes claims through a human-in-the-loop dashboard with automated traffic-light verdicts (Approved, Flagged, Rejected) and fraud signal detection.

## Tech Stack
- **Programming Language**: Python
- **Framework**: Streamlit
- **Database**: SQLite
- **APIs & Models**: Groq Llama Models (Vision & Text)
- **Utilities**: PyMuPDF (PDF Parsing)

## Setup Instructions

### 1. Clone the repository and install dependencies
```bash
pip install streamlit python-dotenv groq pymupdf
```

### 2. Environment Variables
Create a `.env` file in the root of the project to securely store your API keys or put it in `.streamlit/secrets.toml`:
```env
GROQ_API_KEY="your-groq-api-key-here"
```

### 3. Run the project locally
Launch the app via Streamlit:
```bash
streamlit run app.py
```
Open the provided local URL (typically http://localhost:8501) in your browser.
