#!/usr/bin/env python3
"""
Generate sample PDF resumes for testing the Career Guidance and Resume Intelligence System.
Uses fpdf2 with modern API.
"""
import os
from fpdf import FPDF
from fpdf.enums import XPos, YPos

class ResumePDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def build_pdf(filename, name, contact, summary, education, skills, experience, projects, certs):
    pdf = ResumePDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Name
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(24, 43, 73)
    pdf.cell(0, 8, name, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    
    # Contact
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 5, contact, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(2)
    
    # Divider
    pdf.set_draw_color(30, 90, 160)
    pdf.set_line_width(0.6)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(3)
    
    def section_header(title):
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(24, 43, 73)
        pdf.cell(0, 6, title.upper(), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_draw_color(180, 190, 205)
        pdf.set_line_width(0.3)
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(2)

    # Summary
    if summary:
        section_header("Professional Summary")
        pdf.set_font("Helvetica", "", 9.5)
        pdf.set_text_color(40, 40, 40)
        pdf.multi_cell(0, 4.5, summary, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(2)

    # Skills
    if skills:
        section_header("Technical Skills")
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(40, 40, 40)
        for cat, sk_list in skills.items():
            line_txt = f"{cat}: {', '.join(sk_list)}"
            pdf.multi_cell(0, 4.5, line_txt, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(2)

    # Experience
    if experience:
        section_header("Work Experience")
        for job in experience:
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(20, 20, 20)
            pdf.cell(120, 5, f"{job['title']} - {job['company']}")
            pdf.set_font("Helvetica", "I", 9)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 5, job["dates"], new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")
            
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(40, 40, 40)
            for bullet in job["bullets"]:
                pdf.multi_cell(0, 4.5, f"  -  {bullet}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(1.5)

    # Projects
    if projects:
        section_header("Projects")
        for proj in projects:
            pdf.set_font("Helvetica", "B", 9.5)
            pdf.set_text_color(20, 20, 20)
            if "tech" in proj:
                pdf.cell(110, 5, proj["title"])
                pdf.set_font("Helvetica", "I", 8.5)
                pdf.set_text_color(90, 90, 90)
                pdf.cell(0, 5, f"Tech: {proj['tech']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")
            else:
                pdf.cell(0, 5, proj["title"], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(40, 40, 40)
            pdf.multi_cell(0, 4.5, f"  {proj['desc']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(1.5)

    # Education
    if education:
        section_header("Education")
        for edu in education:
            pdf.set_font("Helvetica", "B", 9.5)
            pdf.set_text_color(20, 20, 20)
            pdf.cell(120, 5, f"{edu['degree']} | {edu['institution']}")
            pdf.set_font("Helvetica", "I", 9)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 5, edu["year"], new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")
            if "details" in edu:
                pdf.set_font("Helvetica", "", 8.5)
                pdf.set_text_color(60, 60, 60)
                pdf.multi_cell(0, 4.5, f"  {edu['details']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(1.5)

    # Certifications
    if certs:
        section_header("Certifications & Interests")
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(40, 40, 40)
        for c in certs:
            pdf.multi_cell(0, 4.5, f"  -  {c}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    pdf.output(filename)
    print(f"Generated resume: {filename}")

def main():
    # 1. Alex Morgan - AI/ML Engineer
    build_pdf(
        "sample_data/sample_resumes/alex_morgan_ai_ml_engineer.pdf",
        name="Alex Morgan",
        contact="Email: alex.morgan@email.com | Phone: +1-555-019-2834 | LinkedIn: linkedin.com/in/alexmorgan-ai | GitHub: github.com/alexmorgan-ai",
        summary="Results-oriented Machine Learning Engineer with 3+ years of experience designing scalable deep learning pipelines, natural language processing models, and production MLOps systems. Proficient in PyTorch, Scikit-Learn, Docker, and AWS cloud deployment.",
        skills={
            "Programming Languages": ["Python", "SQL", "C++", "Bash"],
            "ML / Deep Learning": ["PyTorch", "TensorFlow", "Scikit-Learn", "Keras", "HuggingFace Transformers", "OpenCV"],
            "NLP & GenAI": ["BERT", "spaCy", "NLTK", "LangChain", "Vector Databases", "Prompt Engineering"],
            "Data & MLOps": ["Pandas", "NumPy", "Docker", "MLflow", "Git", "DVC", "FastAPI", "Kubernetes"],
            "Cloud & Tools": ["AWS (EC2, S3, SageMaker)", "PostgreSQL", "Linux", "CI/CD", "Jupyter"]
        },
        experience=[
            {
                "title": "Machine Learning Engineer",
                "company": "Cognitive Solutions Inc.",
                "dates": "2023 - Present",
                "bullets": [
                    "Engineered end-to-end customer intent classification pipeline using PyTorch and HuggingFace BERT, reducing classification error by 24%.",
                    "Deployed real-time inference microservices using FastAPI and Docker on AWS SageMaker, processing over 1.2M daily API requests with sub-50ms latency.",
                    "Implemented MLOps experiment tracking and automated retraining triggers using MLflow and GitHub Actions."
                ]
            },
            {
                "title": "Junior Data Scientist",
                "company": "DataSphere Labs",
                "dates": "2021 - 2023",
                "bullets": [
                    "Developed predictive customer churn and lifetime value models using Scikit-Learn and XGBoost, improving retention campaigns by 18%.",
                    "Conducted feature engineering and exploratory data analysis across 500k+ customer transactions with Pandas and SQL."
                ]
            }
        ],
        projects=[
            {
                "title": "Autonomous Resume Intelligence & Skill Gap Analyzer",
                "tech": "Python, NLP, Scikit-Learn, TF-IDF, PyMuPDF, Streamlit",
                "desc": "Built an intelligent NLP resume parser that extracts candidate qualifications and matches technical profiles against 20+ career roles with 92% cosine similarity accuracy."
            },
            {
                "title": "Real-time Object Detection Pipeline",
                "tech": "PyTorch, OpenCV, YOLOv8, Docker",
                "desc": "Designed a deep learning computer vision model for manufacturing defect identification running at 45 FPS on edge GPU hardware."
            }
        ],
        education=[
            {
                "degree": "B.S. in Computer Science (Specialization in AI & Machine Learning)",
                "institution": "University of California, Berkeley",
                "year": "2017 - 2021",
                "details": "GPA: 3.82/4.0 | Dean's Honor List | Relevant Coursework: Deep Neural Networks, Natural Language Processing, Linear Algebra"
            }
        ],
        certs=[
            "AWS Certified Machine Learning - Specialty (2024)",
            "DeepLearning.AI Deep Learning Specialization (Coursera, 2022)",
            "Interests: Open Source AI, Autonomous Robotics, Generative Audio Models"
        ]
    )

    # 2. Sarah Chen - Data Scientist
    build_pdf(
        "sample_data/sample_resumes/sarah_chen_data_scientist.pdf",
        name="Sarah Chen",
        contact="Email: sarah.chen@analyticsmail.com | Phone: +1-555-082-1923 | LinkedIn: linkedin.com/in/sarahchen-ds | Portfolio: sarahchen-data.dev",
        summary="Data Scientist with expertise in predictive modeling, statistical hypothesis testing, and business intelligence. Skilled in transforming messy multi-terabyte datasets into actionable executive insights with Python, SQL, and Tableau.",
        skills={
            "Core Analytics": ["Python", "R", "SQL", "Statistics", "Hypothesis Testing", "A/B Testing", "Econometrics"],
            "Data & ML": ["Pandas", "NumPy", "Scikit-Learn", "Matplotlib", "Seaborn", "Statsmodels", "XGBoost"],
            "BI & Data Warehousing": ["Tableau", "Power BI", "Snowflake", "BigQuery", "PostgreSQL", "Excel"],
            "Tools": ["Git", "Jupyter", "Linux", "Airflow", "Docker"]
        },
        experience=[
            {
                "title": "Data Scientist",
                "company": "Vanguard Retail Analytics",
                "dates": "2022 - Present",
                "bullets": [
                    "Formulated multivariate regression and time-series forecasting models predicting quarterly inventory demand across 140 regional stores with 94% accuracy.",
                    "Designed and analyzed 35+ controlled A/B experiments to evaluate digital checkout conversion rates, driving a $2.4M ARR increase.",
                    "Created self-service executive dashboards in Tableau used weekly by 60+ business decision makers."
                ]
            }
        ],
        projects=[
            {
                "title": "Customer Segmentation & Churn Risk Predictor",
                "tech": "Python, K-Means Clustering, Random Forest, Scikit-Learn",
                "desc": "Clustered 200,000 active retail accounts based on RFM metrics to detect high-value customers vulnerable to churn."
            }
        ],
        education=[
            {
                "degree": "M.S. in Applied Statistics & Data Analytics",
                "institution": "Columbia University",
                "year": "2020 - 2022",
                "details": "GPA: 3.90/4.0 | Capstone in High-Dimensional Data Modeling"
            },
            {
                "degree": "B.A. in Mathematics & Economics",
                "institution": "New York University",
                "year": "2016 - 2020",
                "details": "Magna Cum Laude"
            }
        ],
        certs=[
            "Tableau Desktop Certified Associate (2023)",
            "Google Professional Data Engineer Certification (2024)",
            "Interests: Causal Inference, Algorithmic Fairness, Marathon Running"
        ]
    )

    # 3. David Kim - Full Stack Developer
    build_pdf(
        "sample_data/sample_resumes/david_kim_software_engineer.pdf",
        name="David Kim",
        contact="Email: david.kim@webdevpro.io | Phone: +1-555-731-9920 | GitHub: github.com/davidkim-dev | Portfolio: davidkim.me",
        summary="Versatile Full Stack Software Engineer specializing in modern JavaScript/TypeScript architectures, React user interfaces, and Node.js microservices. Dedicated to building accessible, high-performance web applications with clean code principles.",
        skills={
            "Frontend": ["JavaScript", "TypeScript", "React", "Next.js", "HTML5", "CSS3", "Tailwind CSS", "Redux"],
            "Backend": ["Node.js", "Express", "RESTful APIs", "GraphQL", "Python", "Flask"],
            "Databases": ["PostgreSQL", "MongoDB", "Redis", "SQL"],
            "DevOps & Quality": ["Docker", "Git", "GitHub Actions", "Jest", "Cypress", "AWS"]
        },
        experience=[
            {
                "title": "Full Stack Developer",
                "company": "Nexus Web Solutions",
                "dates": "2022 - Present",
                "bullets": [
                    "Engineered responsive React web application serving 80,000 monthly active users with sub-1.5s initial page loads.",
                    "Designed RESTful backend microservices in Node.js and Express with PostgreSQL, integrating Stripe payment processing and OAuth2 authentication.",
                    "Maintained 90%+ unit and end-to-end test coverage with Jest and Cypress within automated GitHub Actions CI/CD pipelines."
                ]
            }
        ],
        projects=[
            {
                "title": "TaskFlow - Collaborative Project Management SaaS",
                "tech": "React, TypeScript, Node.js, PostgreSQL, Docker",
                "desc": "Built an interactive Kanban board application with real-time websocket synchronization, drag-and-drop mechanics, and role-based access control."
            }
        ],
        education=[
            {
                "degree": "B.S. in Software Engineering",
                "institution": "University of Washington",
                "year": "2018 - 2022",
                "details": "Graduated with Honors | President of Web Development Club"
            }
        ],
        certs=[
            "Meta Certified Front-End Developer (2023)",
            "AWS Certified Developer - Associate (2024)",
            "Interests: Web Performance Optimization, Open-Source UI Libraries, Mountain Biking"
        ]
    )

    # 4. Priya Patel - Cloud & DevOps Engineer
    build_pdf(
        "sample_data/sample_resumes/priya_patel_cloud_devops.pdf",
        name="Priya Patel",
        contact="Email: priya.patel@cloudops.net | Phone: +1-555-442-1089 | LinkedIn: linkedin.com/in/priyapatel-devops | GitHub: github.com/priyapatel-ops",
        summary="Certified Cloud & DevOps Engineer with 3+ years experience automating multi-region AWS cloud infrastructure, containerized deployments with Kubernetes, and robust CI/CD pipelines using Terraform and GitHub Actions.",
        skills={
            "Cloud Platforms": ["AWS", "Azure", "GCP"],
            "Containers & Orchestration": ["Docker", "Kubernetes", "Helm", "EKS"],
            "IaC & Automation": ["Terraform", "Ansible", "Bash", "Python", "Linux"],
            "CI/CD & Observability": ["GitHub Actions", "Jenkins", "Prometheus", "Grafana", "Git"]
        },
        experience=[
            {
                "title": "DevOps Engineer",
                "company": "Stratus Cloud Systems",
                "dates": "2023 - Present",
                "bullets": [
                    "Architected and provisioned AWS multi-region infrastructure using modular Terraform templates, reducing provisioning lead time from 3 days to 25 minutes.",
                    "Migrated 18 monolithic services into containerized microservices hosted on Amazon EKS (Kubernetes), achieving 99.98% system uptime.",
                    "Engineered CI/CD automation in GitHub Actions that cut build and deployment times by 45% while enforcing automated security scans."
                ]
            }
        ],
        projects=[
            {
                "title": "Zero-Downtime EKS GitOps Delivery Pipeline",
                "tech": "Kubernetes, ArgoCD, Terraform, Helm, AWS EKS",
                "desc": "Implemented a declarative GitOps deployment workflow using ArgoCD and Helm charts, handling automated canary rollouts and instant rollback triggers."
            }
        ],
        education=[
            {
                "degree": "B.Tech in Information Technology",
                "institution": "National Institute of Technology",
                "year": "2019 - 2023",
                "details": "First Class with Distinction | Network Systems and Distributed Computing"
            }
        ],
        certs=[
            "AWS Certified Solutions Architect - Associate (2023)",
            "Certified Kubernetes Administrator (CKA) (2024)",
            "HashiCorp Certified: Terraform Associate (2024)",
            "Interests: Cloud Security, Linux Kernel Internals, Hiking"
        ]
    )

if __name__ == "__main__":
    main()
