"""
Module: web_app.py
Description: Production FastAPI Backend powering the Executive UI for
CareerPulse AI Studio.
Fully dynamic: supports custom resume uploads, active candidate pool,
real-time recruiter screening, and interactive 40+ roles exploration.
"""

import os
import glob
import base64
import tempfile
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from pydantic import BaseModel

from src.resume_parser import parse_resume
from src.career_recommendation import CareerRecommender
from src.job_matching import JobMatcher
from src.ai_suggestions import (
    generate_professional_summary,
    rewrite_project_description,
    create_learning_roadmap,
    answer_career_question,
    get_active_provider
)

app = FastAPI(title="CareerPulse AI Studio", version="2.5.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

recommender = CareerRecommender()

SAMPLE_RESUMES = {
    "alex_morgan": {
        "label": "Alex Morgan",
        "role": "Machine Learning Engineer",
        "file": "sample_data/sample_resumes/alex_morgan_ai_ml_engineer.pdf"
    },
    "sarah_chen": {
        "label": "Sarah Chen",
        "role": "Data Scientist",
        "file": "sample_data/sample_resumes/sarah_chen_data_scientist.pdf"
    },
    "david_kim": {
        "label": "David Kim",
        "role": "Full Stack Developer",
        "file": "sample_data/sample_resumes/david_kim_software_engineer.pdf"
    },
    "priya_patel": {
        "label": "Priya Patel",
        "role": "Cloud & DevOps Engineer",
        "file": "sample_data/sample_resumes/priya_patel_cloud_devops.pdf"
    }
}

SAMPLE_JDS = {
    "ml_engineer": {
        "title": "Machine Learning Engineer (Apex AI)",
        "file": "sample_data/job_descriptions/ml_engineer_jd.txt"
    },
    "data_scientist": {
        "title": "Senior Data Scientist (InsightMetrics)",
        "file": "sample_data/job_descriptions/data_scientist_jd.txt"
    },
    "cloud_devops": {
        "title": "Cloud & DevOps Engineer (CloudScale)",
        "file": "sample_data/job_descriptions/cloud_devops_jd.txt"
    },
    "fullstack": {
        "title": "Full Stack Software Engineer (Nova Web)",
        "file": "sample_data/job_descriptions/fullstack_jd.txt"
    }
}

# Dynamic session storage
SESSION_CANDIDATE: Dict[str, Any] = {}
CANDIDATE_POOL: List[Dict[str, Any]] = []

def enrich_candidate(cand: Dict[str, Any]) -> Dict[str, Any]:
    if not cand:
        return cand
    if "contact" in cand and isinstance(cand["contact"], dict):
        cand["email"] = cand["contact"].get("email")
        cand["phone"] = cand["contact"].get("phone")
        cand["linkedin"] = cand["contact"].get("linkedin")
        cand["github"] = cand["contact"].get("github")
    if "action_verb_metrics" in cand and isinstance(cand["action_verb_metrics"], dict):
        cand["action_verb_score"] = cand["action_verb_metrics"].get("action_verb_score", 60)
        cand["action_verbs"] = cand["action_verb_metrics"].get("verbs_used", [])
    if "sections" in cand and isinstance(cand["sections"], dict):
        cand["section_names"] = list(cand["sections"].keys())
    return cand

def init_candidate_pool():
    global CANDIDATE_POOL, SESSION_CANDIDATE
    CANDIDATE_POOL = []
    
    # 1. Load any previously uploaded resumes
    if os.path.exists("uploads"):
        for fname in sorted(os.listdir("uploads")):
            if fname.lower().endswith(".pdf"):
                fpath = os.path.join("uploads", fname)
                try:
                    cand = enrich_candidate(parse_resume(fpath))
                    cand["file_name"] = fname
                    cand["is_sample"] = False
                    CANDIDATE_POOL.append(cand)
                    if not SESSION_CANDIDATE:
                        SESSION_CANDIDATE = cand
                except Exception:
                    pass

    # 2. Load benchmark sample resumes
    for k, v in SAMPLE_RESUMES.items():
        try:
            cand = enrich_candidate(parse_resume(v["file"]))
            cand["is_sample"] = True
            CANDIDATE_POOL.append(cand)
        except Exception:
            pass

    if CANDIDATE_POOL and not SESSION_CANDIDATE:
        SESSION_CANDIDATE = CANDIDATE_POOL[0]

init_candidate_pool()

class MatchRequest(BaseModel):
    jd_text: str
    jd_title: Optional[str] = "Target Role"

class AIRequest(BaseModel):
    target_role: Optional[str] = "Machine Learning Engineer"
    project_desc: Optional[str] = None
    tech_stack: Optional[str] = None
    missing_skills: Optional[List[str]] = None
    question: Optional[str] = None

class ResumeUploadPayload(BaseModel):
    filename: str
    base64_data: str

class RecruiterScreenRequest(BaseModel):
    jd_id: Optional[str] = "ml_engineer"
    custom_jd_text: Optional[str] = None
    custom_jd_title: Optional[str] = None

@app.get("/api/status")
def get_status():
    return {
        "status": "online",
        "provider": get_active_provider(),
        "candidate_loaded": bool(SESSION_CANDIDATE),
        "candidate_name": SESSION_CANDIDATE.get("name", "None"),
        "total_skills": len(SESSION_CANDIDATE.get("skills", [])),
        "total_pool_count": len(CANDIDATE_POOL),
        "total_catalog_roles": len(recommender.df_roles) if recommender.df_roles is not None else 40
    }

@app.get("/api/sample-data")
def get_sample_data():
    jds = []
    for k, v in SAMPLE_JDS.items():
        with open(v["file"], "r", encoding="utf-8") as f:
            text = f.read()
        jds.append({"id": k, "title": v["title"], "text": text})

    categories = ["All"] + recommender.get_categories()
    return {"jds": jds, "categories": categories}

@app.post("/api/upload-resume-json")
def upload_resume_json(payload: ResumeUploadPayload):
    global SESSION_CANDIDATE, CANDIDATE_POOL
    if not payload.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    raw_b64 = payload.base64_data
    if "," in raw_b64:
        raw_b64 = raw_b64.split(",", 1)[1]

    try:
        pdf_bytes = base64.b64decode(raw_b64)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 payload: {e}")

    # Persist copy to uploads/
    os.makedirs("uploads", exist_ok=True)
    saved_target = os.path.join("uploads", payload.filename)
    try:
        with open(saved_target, "wb") as f:
            f.write(pdf_bytes)
        cand = enrich_candidate(parse_resume(saved_target))
    except ValueError as ve:
        if os.path.exists(saved_target):
            os.remove(saved_target)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        if os.path.exists(saved_target):
            os.remove(saved_target)
        raise HTTPException(status_code=400, detail=f"Failed to process PDF resume: {e}")

    cand["file_name"] = payload.filename
    cand["is_sample"] = False
    SESSION_CANDIDATE = cand
    
    # Add or update in recruiter candidate pool
    found = False
    for i, c in enumerate(CANDIDATE_POOL):
        if c.get("name") == cand.get("name") or c.get("file_name") == payload.filename:
            CANDIDATE_POOL[i] = cand
            found = True
            break
    if not found:
        # Place newly uploaded candidate at the very front of the screening pool
        CANDIDATE_POOL.insert(0, cand)

    return SESSION_CANDIDATE

@app.delete("/api/recruiter-pool/remove")
def remove_candidate_from_pool(candidate_name: str):
    global CANDIDATE_POOL
    CANDIDATE_POOL = [c for c in CANDIDATE_POOL if c.get("name") != candidate_name]
    return {"status": "ok", "remaining_count": len(CANDIDATE_POOL)}

@app.post("/api/recruiter-pool/clear-samples")
def clear_sample_candidates():
    global CANDIDATE_POOL
    CANDIDATE_POOL = [c for c in CANDIDATE_POOL if not c.get("is_sample", False)]
    return {"status": "ok", "remaining_count": len(CANDIDATE_POOL)}

@app.get("/api/active-candidate")
def get_active_candidate():
    global SESSION_CANDIDATE
    if not SESSION_CANDIDATE and CANDIDATE_POOL:
        SESSION_CANDIDATE = CANDIDATE_POOL[0]
    return SESSION_CANDIDATE

@app.get("/api/recommendations")
def get_recommendations(category: Optional[str] = "All", top_k: int = 9):
    global SESSION_CANDIDATE
    if not SESSION_CANDIDATE and CANDIDATE_POOL:
        SESSION_CANDIDATE = CANDIDATE_POOL[0]

    recs = recommender.recommend(
        SESSION_CANDIDATE,
        top_k=top_k,
        category_filter=category if category != "All" else None
    )
    for r in recs:
        r["target_role"] = r.get("role_name", "Target Role")
        r["role_name"] = r.get("role_name", r["target_role"])
        r["compatibility_score"] = r.get("match_percentage", 0)
        r["match_percentage"] = r.get("match_percentage", r["compatibility_score"])
        r["role_description"] = r.get("job_description", "")
        r["job_description"] = r.get("job_description", r["role_description"])
        r["salary_band"] = r.get("avg_salary_range", "$100k - $150k")
        r["avg_salary_range"] = r.get("avg_salary_range", r["salary_band"])
        if "required_skills" not in r:
            r["required_skills"] = list(set(r.get("matched_skills", []) + r.get("missing_skills", [])))

    return {"recommendations": recs, "active_category": category}

@app.post("/api/match-job")
def match_job(req: MatchRequest):
    global SESSION_CANDIDATE
    if not SESSION_CANDIDATE and CANDIDATE_POOL:
        SESSION_CANDIDATE = CANDIDATE_POOL[0]

    matcher = JobMatcher(SESSION_CANDIDATE)
    result = matcher.match(req.jd_text, jd_title=req.jd_title or "Target Role")
    return result

@app.post("/api/ai/summary")
def ai_summary(req: AIRequest):
    global SESSION_CANDIDATE
    if not SESSION_CANDIDATE and CANDIDATE_POOL:
        SESSION_CANDIDATE = CANDIDATE_POOL[0]
    summary = generate_professional_summary(SESSION_CANDIDATE, req.target_role)
    return {"summary": summary, "provider": get_active_provider()}

@app.post("/api/ai/rewrite-project")
def ai_rewrite_project(req: AIRequest):
    desc = req.project_desc or "Built an intelligent end-to-end classification system."
    rewritten = rewrite_project_description(desc, req.target_role, req.tech_stack)
    return {"rewritten": rewritten, "provider": get_active_provider()}

@app.post("/api/ai/roadmap")
def ai_roadmap(req: AIRequest):
    gaps = req.missing_skills or ["Kubernetes", "MLflow", "Vector Databases", "Triton"]
    roadmap = create_learning_roadmap(gaps, req.target_role or "Machine Learning Engineer", 8)
    return {"roadmap": roadmap, "provider": get_active_provider()}

@app.post("/api/ai/chat")
def ai_chat(req: AIRequest):
    global SESSION_CANDIDATE
    if not SESSION_CANDIDATE and CANDIDATE_POOL:
        SESSION_CANDIDATE = CANDIDATE_POOL[0]
    q = req.question or "What career advice do you have for my profile?"
    answer = answer_career_question(SESSION_CANDIDATE, q, req.target_role)
    return {"answer": answer, "provider": get_active_provider()}

@app.post("/api/recruiter-screen")
def recruiter_screen(req: Optional[RecruiterScreenRequest] = None):
    """
    Ranks ALL candidates currently in the screening pool (including the uploaded user resume!)
    against the chosen or custom job description.
    """
    if req and req.custom_jd_text and req.custom_jd_text.strip():
        jd_text = req.custom_jd_text
        title = req.custom_jd_title or "Custom Job Opening"
    else:
        jd_key = req.jd_id if req else "ml_engineer"
        info = SAMPLE_JDS.get(jd_key, SAMPLE_JDS["ml_engineer"])
        with open(info["file"], "r", encoding="utf-8") as f:
            jd_text = f.read()
        title = info["title"]

    leaderboard = []
    for cand in CANDIDATE_POOL:
        try:
            matcher = JobMatcher(cand)
            res = matcher.match(jd_text, jd_title=title)
            res["highest_degree"] = cand.get("highest_degree")
            res["estimated_experience_years"] = cand.get("estimated_experience_years")
            res["file_name"] = cand.get("file_name", "resume.pdf")
            res["is_active_user"] = (cand.get("name") == SESSION_CANDIDATE.get("name"))
            leaderboard.append(res)
        except Exception:
            continue

    leaderboard.sort(key=lambda x: x["overall_match_percentage"], reverse=True)
    return {"leaderboard": leaderboard, "job_title": title, "candidate_count": len(leaderboard)}

@app.get("/api/catalog-roles")
def get_catalog_roles(q: Optional[str] = "", category: Optional[str] = "All"):
    """
    Returns live roles from catalog with optional search query and category filtering.
    """
    if recommender.df_roles is None:
        recommender.train_and_save_model()

    df = recommender.df_roles.copy()
    if category and category != "All":
        df = df[df["category"].str.lower() == category.lower()]

    if q and q.strip():
        query = q.lower().strip()
        mask = (
            df["role_name"].str.lower().str.contains(query, na=False) |
            df["category"].str.lower().str.contains(query, na=False) |
            df["required_skills"].str.lower().str.contains(query, na=False) |
            df["job_description"].str.lower().str.contains(query, na=False)
        )
        df = df[mask]

    records = df.to_dict(orient="records")
    return {"roles": records, "total_found": len(records)}

@app.post("/api/catalog-role-match/{role_id}")
def match_catalog_role(role_id: int):
    """
    Real-time matching of active candidate against any specific catalog role.
    """
    global SESSION_CANDIDATE
    if not SESSION_CANDIDATE and CANDIDATE_POOL:
        SESSION_CANDIDATE = CANDIDATE_POOL[0]

    if recommender.df_roles is None:
        recommender.train_and_save_model()

    matching_rows = recommender.df_roles[recommender.df_roles["role_id"] == role_id]
    if matching_rows.empty:
        raise HTTPException(status_code=404, detail="Role ID not found in catalog")

    role_data = matching_rows.iloc[0].to_dict()
    jd_synth = f"{role_data['role_name']}\n{role_data['category']}\nRequired Skills: {role_data['required_skills']}\nSecondary Skills: {role_data.get('secondary_skills', '')}\nTools: {role_data.get('tools_and_frameworks', '')}\n{role_data['job_description']}"

    matcher = JobMatcher(SESSION_CANDIDATE)
    match_result = matcher.match(jd_synth, jd_title=role_data["role_name"])
    match_result["role_data"] = role_data
    return match_result

@app.get("/reports/{filename}")
def serve_report(filename: str):
    fpath = os.path.join(os.path.dirname(__file__), "reports", filename)
    if os.path.exists(fpath):
        return FileResponse(fpath, media_type="application/pdf", filename=filename)
    raise HTTPException(status_code=404, detail="Report file not found")

@app.get("/", response_class=HTMLResponse)
def serve_ui():
    index_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web_app:app", host="0.0.0.0", port=8000, reload=True)
