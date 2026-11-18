# Model Evaluation & Benchmark Performance Report
**AI-Powered Career Guidance and Resume Intelligence System**  
AI/ML with Python Training Program • Major Project

---
## 1. Executive Summary & Benchmark Metrics

| Metric | Value | Target Benchmark | Status |
| :--- | :---: | :---: | :---: |
| **Top-1 Recommendation Accuracy** | **100.0%** | > 85.0% | PASS |
| **Top-3 Recommendation Accuracy** | **100.0%** | > 95.0% | PASS |
| **Mean Reciprocal Rank (MRR)** | **1.000** | > 0.850 | PASS |
| **Key Skills Extraction Recall** | **95.0%** | > 90.0% | PASS |
| **Avg. PDF Parsing Latency** | **65.58 ms** | < 150 ms | PASS |
| **Avg. Recommendation Latency** | **3.17 ms** | < 100 ms | PASS |

---
## 2. Methodology & Test Harness
- **Vectorization Scheme:** TF-IDF with sublinear term frequency scaling and unigram + bigram n-gram extraction (1, 2).
- **Similarity Function:** Cosine Similarity matrix calculation complemented by Jaccard / Overlap coefficient on domain-specific technical skills.
- **Evaluation Dataset:** Realistically synthesized candidate resumes across major software, data, cloud, and AI engineering disciplines.

---
## 3. Detailed Case-by-Case Breakdown

### Candidate: Alex Morgan
- **Expected Ground Truth Role:** Machine Learning Engineer
- **Predicted Top Role:** Machine Learning Engineer (Match: 82.9%)
- **Role Rank:** 1
- **Key Skills Extraction Recall:** 100.0% (Total Skills Found: 42)
- **Parsing Latency:** 75.38 ms
- **Top-3 Recommended Career Paths:**
  - Machine Learning Engineer: 82.9%
  - Natural Language Processing (NLP) Engineer: 72.9%
  - Data Scientist: 58.9%

### Candidate: Sarah Chen
- **Expected Ground Truth Role:** Data Scientist
- **Predicted Top Role:** Data Scientist (Match: 64.5%)
- **Role Rank:** 1
- **Key Skills Extraction Recall:** 100.0% (Total Skills Found: 28)
- **Parsing Latency:** 61.53 ms
- **Top-3 Recommended Career Paths:**
  - Data Scientist: 64.5%
  - Data Analyst: 56.9%
  - Business Intelligence (BI) Developer: 50.1%

### Candidate: David Kim
- **Expected Ground Truth Role:** Full Stack Developer
- **Predicted Top Role:** Full Stack Developer (Match: 81.6%)
- **Role Rank:** 1
- **Key Skills Extraction Recall:** 100.0% (Total Skills Found: 28)
- **Parsing Latency:** 62.51 ms
- **Top-3 Recommended Career Paths:**
  - Full Stack Developer: 81.6%
  - Frontend Developer: 52.1%
  - Backend Software Engineer: 47.7%

### Candidate: Priya Patel
- **Expected Ground Truth Role:** Cloud & DevOps Engineer
- **Predicted Top Role:** Cloud & DevOps Engineer (Match: 74.3%)
- **Role Rank:** 1
- **Key Skills Extraction Recall:** 80.0% (Total Skills Found: 21)
- **Parsing Latency:** 62.9 ms
- **Top-3 Recommended Career Paths:**
  - Cloud & DevOps Engineer: 74.3%
  - Platform Engineer: 59.0%
  - Site Reliability Engineer (SRE): 51.7%
