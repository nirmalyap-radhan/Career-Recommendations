"""
Module: job_matching.py
Description: Production ATS Resume Matching & Multi-Candidate Screening System.
Includes 4-pillar ATS scoring (Skills, Experience, Education, Impact), detailed
skill-gap audits, and batch candidate ranking.
"""

import os
import re
from typing import Dict, Any, List, Set, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.text_preprocessing import clean_text, preprocess_for_tfidf
from src.skill_extraction import extract_skills, calculate_skill_overlap

class JobMatcher:
    """Enterprise ATS Matcher and Skill-Gap Diagnostic Engine."""

    def __init__(self, candidate_profile: Dict[str, Any]):
        self.candidate = candidate_profile

    def match(self, jd_text: str, jd_title: str = "Target Position") -> Dict[str, Any]:
        """
        Evaluates candidate against JD using 4 core ATS criteria:
        1. Skills Overlap (40%)
        2. Semantic TF-IDF Similarity (25%)
        3. Experience & Seniority Match (20%)
        4. Action Verb & Impact Density (15%)
        """
        if not jd_text or not jd_text.strip():
            raise ValueError("Job description cannot be empty.")

        # 1. Skills Extraction & Overlap
        jd_skills_info = extract_skills(jd_text)
        jd_skills = jd_skills_info["all_skills"]
        cand_skills = self.candidate.get("skills", [])
        matching_skills, missing_skills, skill_ratio = calculate_skill_overlap(cand_skills, jd_skills)

        # 2. Semantic TF-IDF Similarity
        clean_cand = preprocess_for_tfidf(self.candidate.get("cleaned_text", ""))
        clean_jd = preprocess_for_tfidf(jd_text)
        vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
        try:
            tfidf_matrix = vectorizer.fit_transform([clean_cand, clean_jd])
            cos_sim = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])
        except Exception:
            cos_sim = 0.0

        # 3. Experience Alignment
        req_exp_match = re.search(r'(\d+)\+?\s*(?:to\s*\d+)?\s*(?:years?|yrs?)', jd_text, re.IGNORECASE)
        jd_min_exp = float(req_exp_match.group(1)) if req_exp_match else 2.0
        cand_exp = float(self.candidate.get("estimated_experience_years", 2.0))
        if cand_exp >= jd_min_exp:
            exp_score = 1.0
        else:
            exp_score = max(0.4, cand_exp / max(1.0, jd_min_exp))

        # 4. Impact & Action Verb Score
        verb_metrics = self.candidate.get("action_verb_metrics", {})
        verb_score = float(verb_metrics.get("action_verb_score", 60)) / 100.0

        # Weighted Composite ATS Score (0 - 100)
        ats_score = (
            (0.40 * skill_ratio) +
            (0.25 * cos_sim) +
            (0.20 * exp_score) +
            (0.15 * verb_score)
        ) * 100.0
        final_score = round(min(100.0, max(0.0, ats_score)), 1)

        # Readiness classification
        if final_score >= 80:
            readiness = "Top Candidate (Ready for Recruiter Submission)"
            verdict_color = "green"
            rec_action = "Strong profile. Tailor top bullet points to match JD terminology."
        elif final_score >= 65:
            readiness = "Competitive Contender (Minor Gaps to Address)"
            verdict_color = "yellow"
            rec_action = "Good foundation. Integrate missing keywords and quantify project impact."
        elif final_score >= 45:
            readiness = "Moderate Match (Targeted Upskilling Needed)"
            verdict_color = "magenta"
            rec_action = "Demonstrate required frameworks through portfolio projects."
        else:
            readiness = "Low Alignment (Significant Pivot Required)"
            verdict_color = "red"
            rec_action = "Major gap in core technical prerequisites. Consider foundational study."

        return {
            "candidate_name": self.candidate.get("name", "Candidate"),
            "target_role": jd_title,
            "overall_match_percentage": final_score,
            "pillar_breakdown": {
                "skill_alignment_score": round(skill_ratio * 100, 1),
                "semantic_similarity_score": round(cos_sim * 100, 1),
                "experience_fit_score": round(exp_score * 100, 1),
                "action_verb_impact_score": round(verb_score * 100, 1),
            },
            "experience_comparison": {
                "candidate_exp_years": cand_exp,
                "jd_expected_min_years": jd_min_exp
            },
            "readiness_level": readiness,
            "verdict_color": verdict_color,
            "recommended_action": rec_action,
            "total_jd_skills_found": len(jd_skills),
            "total_matching_skills": len(matching_skills),
            "total_missing_skills": len(missing_skills),
            "matching_skills": sorted(list(matching_skills)),
            "missing_skills": sorted(list(missing_skills)),
        }

    def generate_report(self, match_result: Dict[str, Any], save_path: Optional[str] = None) -> str:
        name = match_result["candidate_name"]
        role = match_result["target_role"]
        score = match_result["overall_match_percentage"]
        pillars = match_result["pillar_breakdown"]
        matching = match_result["matching_skills"]
        missing = match_result["missing_skills"]

        md = [
            f"# Enterprise ATS Resume Match & Skill-Gap Report",
            f"**Candidate:** {name} | **Target Role:** {role} | **Date:** November 2026",
            f"**Overall ATS Compatibility Index:** **{score}%** — *{match_result['readiness_level']}*",
            f"",
            f"---",
            f"## 1. Multi-Pillar ATS Performance Scorecard",
            f"| Scoring Pillar | Weight | Candidate Score | Status |",
            f"| :--- | :---: | :---: | :---: |",
            f"| **Technical Skills Overlap** | 40% | **{pillars['skill_alignment_score']}%** | {'PASS' if pillars['skill_alignment_score'] >= 60 else 'GAP'} |",
            f"| **Semantic Content Relevance** | 25% | **{pillars['semantic_similarity_score']}%** | {'PASS' if pillars['semantic_similarity_score'] >= 30 else 'NEUTRAL'} |",
            f"| **Experience & Seniority Fit** | 20% | **{pillars['experience_fit_score']}%** | {'PASS' if pillars['experience_fit_score'] >= 80 else 'REVIEW'} |",
            f"| **Action-Verb Impact Density** | 15% | **{pillars['action_verb_impact_score']}%** | {'HIGH' if pillars['action_verb_impact_score'] >= 50 else 'LOW'} |",
            f"",
            f"---",
            f"## 2. Technical Competency Breakdown",
            f"### Verified Matching Skills ({len(matching)})",
            ", ".join([f"`{s}`" for s in matching]) if matching else "No direct matching keywords.",
            f"",
            f"### Identified Skill Gaps ({len(missing)})",
            "The following high-priority skills appear in the job description but are absent or unverified in your resume:" if missing else "All extracted requirements are met!",
        ]

        for s in missing:
            md.append(f"- **{s}** (Recommended to incorporate into projects or certifications)")

        md.extend([
            f"",
            f"---",
            f"## 3. Immediate Action Plan to Reach 90%+ ATS Score",
            f"1. **Strategic Keyword Insertion:** If you have worked with {', '.join(missing[:3]) if missing else 'emerging tools'}, explicitly include them in bullet points.",
            f"2. **Quantify Outcomes:** Frame accomplishments with metrics (e.g., latency reduction, cost savings, user scale).",
            f"3. **Format Alignment:** Ensure headers follow standard ATS naming conventions (Summary, Experience, Education, Skills).",
        ])

        report_txt = "\n".join(md)
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(report_txt)

        return report_txt

def batch_screen_resumes(resume_paths: List[str], jd_text: str, role_title: str = "Position") -> List[Dict[str, Any]]:
    """
    Recruiter Mode: Evaluates and ranks multiple candidate resumes against a single job description.
    """
    from src.resume_parser import parse_resume
    ranked_candidates = []

    for path in resume_paths:
        try:
            cand = parse_resume(path)
            matcher = JobMatcher(cand)
            res = matcher.match(jd_text, jd_title=role_title)
            res["resume_path"] = path
            res["highest_degree"] = cand.get("highest_degree")
            ranked_candidates.append(res)
        except Exception as e:
            continue

    ranked_candidates.sort(key=lambda x: x["overall_match_percentage"], reverse=True)
    return ranked_candidates
