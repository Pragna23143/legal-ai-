# LexiClear AI: Generative AI for Demystifying Legal Documents

An enterprise-grade Generative AI application engineered to decode and demystify complex, dense legal agreements, non-disclosure contracts, terms of service, employment contracts, and commercial leases.

Built with **Python**, **FastAPI**, **Google Gemini API (`gemini-3.8-flash`)**, **PyMuPDF**, **HTML5/CSS3/JavaScript**, and **BM25 Context-Aware RAG**.

---

## 🎯 Problem Solved
Dense legal jargon, ambiguous boilerplate, and one-sided clauses often conceal severe financial penalties, strict operational notice traps, aggressive intellectual property forfeiture, and asymmetric indemnification liabilities. Laypersons, freelancers, and business executives frequently execute these agreements without comprehending their true exposure.

**LexiClear AI** bridges this gap by providing:
1. **Plain-English Summarization & Layperson Translation**: Converts convoluted legalese into clean, executive summaries with "TL;DR", "Who is Involved", "Core Rights Granted", and "What You Give Up".
2. **Forensic Penalty & Strict Obligation Extraction**: Pinpoints liquidated damages, late fee interest accruals, notice deadlines, unilateral fee shifting, and auto-renewal traps.
3. **Compliance & Risk Audit (Red-Amber-Green)**: Evaluates agreements with an overall Risk Score (1-100), itemized regulatory checklists (GDPR, CCPA, restrictive covenants), and suggested negotiation redlines with 1-click copying.
4. **Context-Aware RAG Legal Assistant**: Chat directly with your contract. The AI retrieves top-relevance token chunks, cites source pages, and quotes verbatim text.

---

## 🛠️ Tech Stack & Architecture

- **Backend**: Python 3.10+, FastAPI, Uvicorn, Pydantic v2
- **PDF Extraction & Chunking**: PyMuPDF (`fitz`), Sliding-Window Overlapping Token Chunker
- **Generative AI & LLM**: Google Gemini API (`google-genai` SDK, `gemini-3.8-flash` / `gemini-flash-latest`)
- **Information Retrieval (RAG)**: BM25 / TF-IDF Hybrid Lexical and Semantic Relevance Retriever
- **Frontend**: HTML5, Modern CSS3 (Glassmorphic dark/slate tech theme, responsive layout, risk meters, animated gauges), Vanilla ES6+ JavaScript (zero build step required)
- **PDF Generation**: ReportLab (for rendering realistic multi-page test contracts)

---

## 🚀 Quick Start Guide

### 1. Prerequisites
Ensure you have Python 3.10+ installed.

### 2. Install Dependencies
```bash
cd legal-ai-demystifier
pip install -r requirements.txt
```

### 3. Set your Gemini API Key (Optional)
You can set your Gemini API key in an environment variable or create a `.env` file:
```bash
# Windows PowerShell
$env:GEMINI_API_KEY="your-gemini-api-key"

# Windows CMD
set GEMINI_API_KEY=your-gemini-api-key

# Or create a .env file:
# GEMINI_API_KEY=your-gemini-api-key
```
> **Note**: If no API key is provided, the app runs in **Offline Simulated Intelligence Mode**, allowing complete testing and demonstrations out of the box! You can also enter your API key dynamically through the UI.

### 4. Run the Application
```bash
# Using the Windows batch runner:
run.bat

# Or using PowerShell:
.\run.ps1

# Or directly with Uvicorn:
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 5. Open in Web Browser
Navigate to:
```
http://127.0.0.1:8000
```

---

## 📑 Preloaded Sample Contracts
The application comes preloaded with 4 realistic, high-liability enterprise agreements:
1. **Enterprise Cloud SaaS Master Services Agreement**: Sneaky 90-day auto-renewal with 25% price surge, customer data AI training rights, unilateral customer indemnification, and $75,000 liquidated damages.
2. **Executive Employment & Non-Compete Agreement**: 24-month worldwide non-compete, comprehensive side-project IP assignment, and $100,000 liquidated damages.
3. **Triple-Net (NNN) Commercial Real Estate Lease**: Unconditional pass-through expenses without audit rights, 18% annual late interest, and forfeiture of $66,000 security deposit.
4. **Unilateral Non-Disclosure Agreement (NDA)**: Disguised as mutual, perpetual confidentiality survival, $50,000 liquidated damages, and unilateral attorney fee shifting.

---

## 🔌 API Endpoints Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/upload` | Upload PDF file, extract pages and chunks via PyMuPDF |
| `POST` | `/api/ingest-text` | Ingest raw or pasted text contract |
| `POST` | `/api/analyze/summary` | Generate plain-English executive summary |
| `POST` | `/api/analyze/risks` | Extract strict penalties, obligations, and unilateral clauses |
| `POST` | `/api/analyze/compliance` | Conduct risk audit, compute 1-100 risk score, and generate redlines |
| `POST` | `/api/chat` | Context-aware RAG question-answering with citations |
| `GET` | `/api/samples` | List all preloaded sample agreements |
| `POST` | `/api/samples/load/{id}` | Load a specific sample contract into the active session |
| `GET` | `/api/samples/download/{id}`| Download sample PDF file |
| `GET` | `/api/download-zip` | Download complete project source code ZIP |
| `POST` | `/api/settings/key` | Update Gemini API key dynamically |
| `GET` | `/api/status` | System health and API key status |

---

## 📦 Download Project ZIP
You can bundle and download the entire application in two ways:
1. Click the **"Download Project ZIP"** button directly in the web UI header.
2. Run the packaging script:
   ```bash
   python generate_zip.py
   ```
   This generates `legal-ai-demystifier.zip` ready for submission or deployment.
