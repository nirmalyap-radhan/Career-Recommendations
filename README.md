# AI-Powered Career Guidance and Resume Intelligence System

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![NLP: PyMuPDF & Scikit-Learn](https://img.shields.io/badge/NLP-PyMuPDF%20%7C%20Scikit--Learn-green.svg)]()
[![Generative AI: Groq, Gemini, Mistral, NVIDIA](https://img.shields.io/badge/GenAI-Groq%20%7C%20Gemini%20%7C%20NVIDIA-purple.svg)]()
[![Dataset: 40+ Industry Roles](https://img.shields.io/badge/Dataset-40+%20Roles%20%7C%20600+%20Skills-orange.svg)]()

> **AI/ML with Python Training Program • Major Project**  
> **Batch:** October 2026 Batch  
> **Submission Deadline:** 5 December 2026  
> **Submission Email:** `support@internselite.com`  

---

## 📌 1. Project Overview & Production Highlights

Modern job applicants and talent acquisition teams face major inefficiencies:
- **Applicants:** Face non-transparent ATS algorithms, struggle to quantify skill gaps, and lack tailored guidance.
- **Recruiters & Engineering Managers:** Spend hours manually screening hundreds of diverse PDF resumes.

This project delivers a **production-ready command-line application** powered by Machine Learning, Natural Language Processing, and Generative AI:
1. **Coordinate-Aware PDF Parsing:** Uses PyMuPDF (`fitz`) to accurately parse multi-column resumes, extract employment date spans, calculate years of experience, and detect highest degree attained.
2. **600+ Skill Taxonomy:** Broad coverage of emerging technology (RAG, LangChain, vLLM, MLOps, Triton, K8s, Rust, Solidity, Kafka, Snowflake).
3. **Hybrid Recommendation Engine:** Multi-factor scoring (TF-IDF cosine similarity, skill overlap, and experience eligibility) across 40+ industry job roles.
4. **4-Pillar ATS Scorecard:** Comprehensive audit covering Skills (40%), Semantic Relevance (25%), Seniority Alignment (20%), and Action-Verb Impact (15%).
5. **Recruiter Mode:** Ingests any folder of resumes, batches and ranks all candidates against a job description, and outputs a candidate leaderboard.
6. **Multi-Provider Generative AI:** Integrated with **Groq Cloud**, **Google Gemini**, **Mistral AI**, and **NVIDIA NIM**, with a smart offline heuristic engine for offline use.
7. **Interactive Career Counselor Chatbot:** Context-grounded multi-turn conversational terminal advisor.

---

## 🏗️ 2. Project Directory Structure

```text
Career_Guidance_Resume_Intelligence/
│
├── sample_data/
│   ├── sample_resumes/
│   │   ├── alex_morgan_ai_ml_engineer.pdf
│   │   ├── sarah_chen_data_scientist.pdf
│   │   ├── david_kim_software_engineer.pdf
│   │   └── priya_patel_cloud_devops.pdf
│   ├── job_descriptions/
│   │   ├── ml_engineer_jd.txt
│   │   ├── data_scientist_jd.txt
│   │   ├── cloud_devops_jd.txt
│   │   └── fullstack_jd.txt
│   ├── job_roles_dataset.csv
│   ├── build_kaggle_roles_dataset.py
│   └── generate_sample_resumes.py
│
├── src/
│   ├── __init__.py
│   ├── resume_parser.py
│   ├── text_preprocessing.py
│   ├── skill_extraction.py
│   ├── career_recommendation.py
│   ├── job_matching.py
│   ├── ai_suggestions.py
│   └── chatbot.py
│
├── models/
│   ├── career_tfidf_vectorizer.joblib
│   └── job_roles_matrix.joblib
│
├── reports/
│   ├── model_evaluation_report.md
│   ├── sample_skill_gap_report.md
│   └── Project_Report.pdf
│
├── main.py
├── evaluate_models.py
├── generate_project_report_pdf.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
└── README.md
```

---

## 🚀 3. Quick Start & Execution

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure API Keys (`.env`)
The system supports multiple providers. Edit `.env` to configure your preferred key:
```ini
AI_PROVIDER=groq
GROQ_API_KEY=your_groq_key_here
GROQ_MODEL=qwen/qwen3.8-27b
```
*(If no API key is set, the application automatically uses its built-in smart offline heuristic engine).*

### Option A: Launch the Executive Web UI Studio
```bash
python3 web_app.py
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser to experience the full interactive visual studio:
- **1-Click Candidate Switcher** (Alex Morgan, Sarah Chen, David Kim, Priya Patel) + drag-and-drop custom PDF upload.
- **Visual 600+ Skills Cloud** with live keyword filtering and frequency tags.
- **Dynamic Career Path Radar** with domain filtering across 40+ industry roles.
- **4-Pillar ATS Compatibility Gauges** (Skills 40%, Semantic 25%, Experience 20%, Impact 15%).
- **AI Resume Optimizer Lab**: Professional Summary generator, STAR Project Rewriter, and 8-Week Roadmap visual timeline.
- **Interactive AI Career Counselor Chatbot**: Conversational career Q&A grounded in candidate resume context.
- **Recruiter Screening Studio**: Batch multi-candidate leaderboard ranking.

---

### Option B: Launch the Terminal Application (Project Guideline Standard)
```bash
python3 main.py
```

---

## 🎯 4. Production Application Capabilities

| Option | Feature | Description |
| :---: | :--- | :--- |
| **`[1]`** | **Load & Parse Resume** | Ingest any PDF resume with multi-column text extraction, experience years calculation, and degree identification. |
| **`[2]`** | **Candidate Profile & Skills** | Displays structured contact details, action-verb density score, and verified skills grouped across 10 domains. |
| **`[3]`** | **Career Path Recommender** | Content-based recommendations with domain filtering (AI/ML, Data, Cloud, Software, Security, etc.). |
| **`[4]`** | **4-Pillar ATS Matcher** | Deep diagnostics: Skills Overlap, Semantic Relevance, Experience Fit, Action-Verb Impact. |
| **`[5]`** | **Recruiter Screening Mode** | Batch process and rank an entire folder of candidate resumes against any target job description. |
| **`[6]`** | **Search 40+ Job Catalog** | Search and explore market demand, required skills, and salary bands across 40+ technology career tracks. |
| **`[7]`** | **Generative AI Optimizer** | Live generation of ATS summaries, STAR project rewrites (no hallucinated metrics), and 8-week roadmaps. |
| **`[8]`** | **Career Counselor Chatbot** | Conversational terminal advisor grounded in candidate skills and target career context. |
| **`[9]`** | **Benchmark Evaluation** | Executes the automated test suite and calculates Top-1/Top-3 accuracies and MRR. |

---

## 📊 5. Benchmark Performance

Run the evaluation suite:
```bash
python3 evaluate_models.py
```

### Measured Performance Summary:
- **Top-1 Career Recommendation Accuracy:** `100.0%`
- **Top-3 Career Recommendation Accuracy:** `100.0%`
- **Mean Reciprocal Rank (MRR):** `1.000`
- **Key Technical Skills Recall:** `95.0%`
- **Average PDF Parsing Latency:** `65.58 ms`
- **Average Recommendation Latency:** `3.17 ms`

---

## 📄 6. Project Report (PDF)
A formal academic/technical project report is generated at:
* **[reports/Project_Report.pdf](file:///Users/nirmalyapradhan/Downloads/AIML_PRED/reports/Project_Report.pdf)**
