"""
Module: ai_suggestions.py
Description: Multi-provider Generative AI Assistant supporting Groq, Google Gemini,
Mistral, NVIDIA NIM, and OpenAI, alongside an offline smart heuristic fallback engine.
"""

import os
import json
from typing import Dict, Any, List, Optional
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

AI_PROVIDER = os.getenv("AI_PROVIDER", "groq").strip().lower()

# Groq API
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b").strip()

# Mistral API
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "").strip()
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-small-latest").strip()

# NVIDIA NIM API
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "").strip()
NVIDIA_MODEL = os.getenv("NVIDIA_MODEL", "google/gemma-3-12b-it").strip()

# Google Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest").strip()

# OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()

def get_active_provider() -> str:
    """Returns the primary active provider or resolves first available."""
    if AI_PROVIDER == "groq" and GROQ_API_KEY:
        return "groq"
    elif AI_PROVIDER == "gemini" and GEMINI_API_KEY:
        return "gemini"
    elif AI_PROVIDER == "mistral" and MISTRAL_API_KEY:
        return "mistral"
    elif AI_PROVIDER == "nvidia" and NVIDIA_API_KEY:
        return "nvidia"
    elif AI_PROVIDER == "openai" and OPENAI_API_KEY:
        return "openai"
    elif GROQ_API_KEY:
        return "groq"
    elif GEMINI_API_KEY:
        return "gemini"
    elif MISTRAL_API_KEY:
        return "mistral"
    elif NVIDIA_API_KEY:
        return "nvidia"
    elif OPENAI_API_KEY:
        return "openai"
    return "offline_smart_engine"

def call_groq_api(prompt: str, system_instruction: str = "") -> Optional[str]:
    """Invokes Groq Cloud API for ultra-fast inference."""
    if not GROQ_API_KEY:
        return None
    url = "https://api.groq.com/openai/v1/chat/completions"
    messages = []
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": 0.4,
        "max_tokens": 1024
    }
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=12)
        if resp.status_code == 200:
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception:
        pass
    return None

def call_mistral_api(prompt: str, system_instruction: str = "") -> Optional[str]:
    """Invokes Mistral AI API."""
    if not MISTRAL_API_KEY:
        return None
    url = "https://api.mistral.ai/v1/chat/completions"
    messages = []
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": MISTRAL_MODEL,
        "messages": messages,
        "temperature": 0.4,
        "max_tokens": 1024
    }
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=12)
        if resp.status_code == 200:
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception:
        pass
    return None

def call_nvidia_api(prompt: str, system_instruction: str = "") -> Optional[str]:
    """Invokes NVIDIA NIM API."""
    if not NVIDIA_API_KEY:
        return None
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    messages = []
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": NVIDIA_MODEL,
        "messages": messages,
        "temperature": 0.4,
        "max_tokens": 1024
    }
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json"
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=12)
        if resp.status_code == 200:
            data = resp.json()
            choices = data.get("choices", [])
            if choices and "message" in choices[0]:
                return choices[0]["message"].get("content", "").strip()
    except Exception:
        pass
    return None

def call_gemini_api(prompt: str, system_instruction: str = "") -> Optional[str]:
    """Invokes Google Gemini REST API."""
    if not GEMINI_API_KEY:
        return None
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    full_text = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
    payload = {
        "contents": [{"parts": [{"text": full_text}]}],
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 1024}
    }
    headers = {"Content-Type": "application/json"}
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "").strip()
    except Exception:
        pass
    return None

def call_openai_api(prompt: str, system_instruction: str = "") -> Optional[str]:
    """Invokes OpenAI Chat Completion API."""
    if not OPENAI_API_KEY:
        return None
    try:
        import openai
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.4,
            max_tokens=1024
        )
        return response.choices[0].message.content.strip()
    except Exception:
        pass
    return None

def generate_ai_response(prompt: str, system_instruction: str = "") -> Optional[str]:
    """
    Tries the configured primary provider first, cascading through available
    providers before falling back to the smart offline heuristic engine.
    """
    provider = get_active_provider()
    
    # Priority cascade order
    providers_to_try = [provider]
    for p in ["groq", "gemini", "nvidia", "mistral", "openai"]:
        if p not in providers_to_try:
            providers_to_try.append(p)

    for p in providers_to_try:
        res = None
        if p == "groq":
            res = call_groq_api(prompt, system_instruction)
        elif p == "gemini":
            res = call_gemini_api(prompt, system_instruction)
        elif p == "mistral":
            res = call_mistral_api(prompt, system_instruction)
        elif p == "nvidia":
            res = call_nvidia_api(prompt, system_instruction)
        elif p == "openai":
            res = call_openai_api(prompt, system_instruction)
            
        if res:
            return res

    return None

# =========================================================================
# SMART HEURISTIC FALLBACK ENGINES (FOR OFFLINE / DISCONNECTED USE)
# =========================================================================

def _offline_summary(candidate: Dict[str, Any], target_role: str) -> str:
    skills = candidate.get("skills", [])
    top_skills = [s.title() for s in skills[:6]]
    top_str = ", ".join(top_skills) if top_skills else "Python, Machine Learning, and Data Systems"

    return (
        f"Dynamic and detail-oriented {target_role} with proven hands-on expertise in {top_str}. "
        f"Demonstrated track record of designing robust technical solutions, optimizing data pipelines, "
        f"and implementing modern software engineering best practices. Adept at cross-functional "
        f"collaboration and continuous innovation to solve complex algorithmic and business challenges."
    )

def _offline_project_rewrite(raw_desc: str, target_role: str, tech_stack: str) -> str:
    clean_lines = [line.strip().lstrip("-*• ") for line in raw_desc.split("\n") if line.strip()]
    if not clean_lines:
        clean_lines = ["Engineered end-to-end technical solution solving domain requirements."]

    first_line = clean_lines[0]
    tech_note = f" using {tech_stack}" if tech_stack else ""

    rewritten_bullets = [
        f"Architected and implemented high-performance system for {first_line.lower()}{tech_note}, adhering to modular code structure.",
        f"Streamlined data processing and validation pipelines, reducing computational latency and enhancing overall throughput.",
        f"Engineered robust unit and integration testing workflows, ensuring reliable edge-case handling and system stability."
    ]
    return "\n".join([f"• {b}" for b in rewritten_bullets])

def _offline_learning_roadmap(missing_skills: List[str], target_role: str, duration_weeks: int = 8) -> str:
    if not missing_skills:
        return (
            f"### Specialized 4-Week Mastery Track for {target_role}\n"
            f"- **Week 1-2:** Advanced System Design, Low-Latency Architecture & Distributed Systems.\n"
            f"- **Week 3:** Production Monitoring, Observability & CI/CD Pipelines.\n"
            f"- **Week 4:** Technical Mock Interviews, Behavioral STAR Scenarios & Portfolio Showcase."
        )

    weeks_per_skill = max(1, duration_weeks // len(missing_skills[:4]))
    roadmap = [f"### Personalized {duration_weeks}-Week Career Upskilling Roadmap: {target_role}\n"]

    current_week = 1
    for skill in missing_skills[:4]:
        end_week = min(duration_weeks, current_week + weeks_per_skill - 1)
        period = f"Week {current_week}" if end_week == current_week else f"Weeks {current_week}-{end_week}"
        roadmap.append(
            f"#### {period}: Mastery of {skill.upper()}\n"
            f"- **Core Concepts:** Learn foundational syntax, architectural patterns, and practical paradigms for {skill}.\n"
            f"- **Hands-On Project:** Build a focused showcase module utilizing {skill} integrated into a GitHub repository.\n"
            f"- **Verification:** Write unit tests and document key trade-offs in a concise technical README.\n"
        )
        current_week = end_week + 1

    if current_week <= duration_weeks:
        roadmap.append(
            f"#### Weeks {current_week}-{duration_weeks}: Capstone Project & Portfolio Integration\n"
            f"- Integrate {', '.join(missing_skills[:4])} into an end-to-end deployed portfolio application.\n"
            f"- Prepare architectural talking points and code explanations for technical recruiter interviews."
        )

    return "\n".join(roadmap)

# =========================================================================
# PUBLIC GENERATIVE AI INTERFACES
# =========================================================================

def generate_professional_summary(candidate: Dict[str, Any], target_role: Optional[str] = None) -> str:
    """Generates an impactful, ATS-optimized professional summary."""
    role = target_role or "AI/ML & Software Specialist"
    skills = candidate.get("skills", [])

    sys_prompt = "You are an expert executive resume writer and career strategist."
    user_prompt = (
        f"Create a concise, high-impact 3-4 sentence professional summary for a candidate targeting the role of '{role}'.\n"
        f"Candidate Name: {candidate.get('name', 'Candidate')}\n"
        f"Technical Skills: {', '.join(skills[:15])}\n"
        f"Extracted Sections:\n{candidate.get('sections', {}).get('experience', '')[:400]}\n"
        f"Guidelines: Highlight technical strengths, problem-solving ability, and business impact. Do NOT make up false degrees or fictional company names."
    )

    res = generate_ai_response(user_prompt, sys_prompt)
    if res:
        return res
    return _offline_summary(candidate, role)

def rewrite_project_description(raw_desc: str, target_role: Optional[str] = None, tech_stack: Optional[str] = None) -> str:
    """Rewrites a project bullet point or paragraph using the STAR method without fabricating achievements."""
    role = target_role or "Target Role"
    sys_prompt = "You are a professional technical resume editor."
    user_prompt = (
        f"Rewrite the following project description into 3 polished, impact-driven bullet points formatted using the STAR method (Situation, Task, Action, Result).\n"
        f"Target Role: {role}\n"
        f"Tech Stack: {tech_stack or 'Relevant Technologies'}\n"
        f"Original Description: {raw_desc}\n"
        f"STRICT RULES:\n"
        f"1. Do NOT invent fake revenue numbers, awards, or false achievements.\n"
        f"2. Use strong active verbs (e.g., Architected, Optimized, Deployed, Implemented).\n"
        f"3. Emphasize software craftsmanship, performance, and best practices."
    )

    res = generate_ai_response(user_prompt, sys_prompt)
    if res:
        return res
    return _offline_project_rewrite(raw_desc, role, tech_stack or "")

def create_learning_roadmap(missing_skills: List[str], target_role: str, duration_weeks: int = 8) -> str:
    """Generates a structured week-by-week learning roadmap for identified skill gaps."""
    sys_prompt = "You are a senior technical mentor and engineering lead."
    user_prompt = (
        f"Create a detailed, actionable {duration_weeks}-week technical learning roadmap for an engineer aiming to become a '{target_role}'.\n"
        f"Identified Skill Gaps to master: {', '.join(missing_skills)}\n"
        f"Include for each stage: Core concepts, recommended hands-on project ideas, and verification milestones."
    )

    res = generate_ai_response(user_prompt, sys_prompt)
    if res:
        return res
    return _offline_learning_roadmap(missing_skills, target_role, duration_weeks)

def answer_career_question(candidate: Dict[str, Any], question: str, target_role: Optional[str] = None) -> str:
    """Answers candidate career questions incorporating their parsed profile as grounding context."""
    role = target_role or "Desired Tech Role"
    skills = candidate.get("skills", [])

    sys_prompt = (
        "You are an intelligent, supportive, and realistic AI Career Guidance Counselor. "
        "Ground your advice specifically in the candidate's verified skills, experience, and target role."
    )
    user_prompt = (
        f"Candidate Name: {candidate.get('name', 'Candidate')}\n"
        f"Identified Skills: {', '.join(skills[:20])}\n"
        f"Target Role: {role}\n"
        f"Candidate Question: {question}\n\n"
        f"Provide a thoughtful, practical, and highly actionable response."
    )

    res = generate_ai_response(user_prompt, sys_prompt)
    if res:
        return res

    q_low = question.lower()
    if "interview" in q_low:
        return (
            f"For interview preparation targeting {role}:\n"
            f"1. **Core Technical Competencies:** Expect in-depth questions on your core skills ({', '.join(skills[:4])}).\n"
            f"2. **System Architecture:** Be ready to draw end-to-end architectures, explaining scaling, caching, and data flows.\n"
            f"3. **Behavioral Questions:** Structure answers with the STAR technique (Situation, Task, Action, Result)."
        )
    elif "salary" in q_low or "compensation" in q_low:
        return (
            f"For {role} roles, market compensation typically ranges between $95,000 and $150,000+ depending on "
            f"location, company tier, and depth of technical mastery in high-demand skills like {', '.join(skills[:3])}."
        )
    elif "project" in q_low:
        return (
            f"To boost your candidacy for {role}, build a public GitHub project highlighting:\n"
            f"- Production-quality API inference with Docker containerization.\n"
            f"- Clean automated tests and CI/CD workflows.\n"
            f"- Well-documented README with architecture diagrams and performance benchmarks."
        )
    else:
        return (
            f"Based on your profile as a candidate with strong capabilities in {', '.join(skills[:5])}, "
            f"advancing toward {role} requires focusing on productionizing models, mastering cloud infrastructure, "
            f"and continuously articulating the business impact of your technical implementations."
        )
