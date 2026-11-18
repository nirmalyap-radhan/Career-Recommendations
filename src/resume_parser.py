"""
Module: resume_parser.py
Description: Production-ready PDF resume parser using PyMuPDF (fitz) with coordinate-aware
text sorting, automated experience duration calculation, education degree classification,
and ATS action-verb density measurement.
"""

import os
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import fitz  # PyMuPDF
from src.text_preprocessing import clean_text
from src.skill_extraction import extract_skills

EMAIL_REGEX = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
PHONE_REGEX = r'(?:(?:\+?\d{1,3}[\s-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4})'
LINKEDIN_REGEX = r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/(?:in|profile)\/[a-zA-Z0-9_-]+'
GITHUB_REGEX = r'(?:https?:\/\/)?(?:www\.)?github\.com\/[a-zA-Z0-9_-]+'

SECTION_PATTERNS = {
    "summary": re.compile(r'^\s*(?:professional\s+summary|summary|profile|about\s+me|objective)\s*$', re.IGNORECASE),
    "skills": re.compile(r'^\s*(?:technical\s+skills|skills|technologies|core\s+competencies|tools\s*&\s*technologies)\s*$', re.IGNORECASE),
    "experience": re.compile(r'^\s*(?:work\s+experience|experience|employment\s+history|professional\s+experience|internships?)\s*$', re.IGNORECASE),
    "education": re.compile(r'^\s*(?:education|academic\s+background|qualifications|academic\s+qualifications)\s*$', re.IGNORECASE),
    "projects": re.compile(r'^\s*(?:projects|academic\s+projects|personal\s+projects|key\s+projects)\s*$', re.IGNORECASE),
    "certifications": re.compile(r'^\s*(?:certifications?|licenses?|credentials|awards?|certifications?\s*&\s*interests?)\s*$', re.IGNORECASE),
    "interests": re.compile(r'^\s*(?:interests?|hobbies|extracurricular\s+activities)\s*$', re.IGNORECASE),
}

DEGREE_PATTERNS = [
    (r'\b(ph\.?d|doctor\s+of\s+philosophy|doctorate)\b', "Ph.D. / Doctorate"),
    (r'\b(m\.?s|master\s+of\s+science|m\.?tech|mba|master\s+of\s+arts|m\.?a)\b', "Master's Degree"),
    (r'\b(b\.?s|bachelor\s+of\s+science|b\.?tech|b\.?e|bachelor\s+of\s+engineering|b\.?a|bachelor\s+of\s+arts)\b', "Bachelor's Degree"),
    (r'\b(associate\s+degree|diploma)\b', "Associate / Diploma")
]

ACTION_VERBS = {
    "architected", "engineered", "developed", "deployed", "implemented", "optimized",
    "spearheaded", "designed", "streamlined", "automated", "orchestrated", "refactored",
    "formulated", "scaled", "migrated", "accelerated", "trained", "integrated", "benchmarked"
}

CURRENT_YEAR = 2026

class ResumeParser:
    """Production parser for extracting structured intelligence from PDF resumes."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self._validate_file()

    def _validate_file(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Resume file not found at: {self.file_path}")
        if not self.file_path.lower().endswith(".pdf"):
            raise ValueError(f"Invalid format: '{self.file_path}'. Only PDF resumes are supported.")
        if os.path.getsize(self.file_path) == 0:
            raise ValueError("The provided PDF file is empty (0 bytes).")

    def extract_text_from_pdf(self) -> str:
        """
        Extracts text blocks with coordinate sorting to preserve reading order
        even in modern multi-column resume layouts.
        """
        try:
            doc = fitz.open(self.file_path)
            full_text = []
            for page in doc:
                # Extract text blocks: (x0, y0, x1, y1, "text", block_no, block_type)
                blocks = page.get_text("blocks")
                # Sort primarily by vertical Y coordinate, then by horizontal X coordinate
                blocks.sort(key=lambda b: (round(b[1] / 10) * 10, b[0]))
                for b in blocks:
                    block_txt = b[4].strip()
                    if block_txt:
                        full_text.append(block_txt)
            doc.close()

            combined = "\n".join(full_text)
            if not combined.strip():
                raise ValueError("Could not extract readable text from PDF. It may be an image-only scan.")
            return combined
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise RuntimeError(f"Error reading PDF with PyMuPDF: {str(e)}")

    def extract_contact_info(self, text: str) -> Dict[str, Any]:
        emails = re.findall(EMAIL_REGEX, text)
        phones = re.findall(PHONE_REGEX, text)
        linkedin = re.findall(LINKEDIN_REGEX, text)
        github = re.findall(GITHUB_REGEX, text)

        return {
            "email": emails[0] if emails else None,
            "phone": phones[0] if phones else None,
            "linkedin": linkedin[0] if linkedin else None,
            "github": github[0] if github else None,
        }

    def extract_name(self, text: str) -> str:
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        for line in lines[:6]:
            if re.search(r'@|\+|http|linkedin|github', line, re.IGNORECASE):
                continue
            words = line.split()
            if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w.isalpha()):
                return line
        return lines[0] if lines else "Candidate"

    def estimate_experience_years(self, text: str) -> float:
        """
        Parses employment date spans (e.g. '2021 - Present', '2019 - 2023')
        and calculates total estimated work experience in years.
        """
        year_ranges = re.findall(r'(\b20\d{2}\b)\s*(?:-|–|to)\s*(\b20\d{2}\b|present|current)', text, re.IGNORECASE)
        total_months = 0
        seen_spans = set()

        for start_str, end_str in year_ranges:
            try:
                start_yr = int(start_str)
                if end_str.lower() in ["present", "current"]:
                    end_yr = CURRENT_YEAR
                else:
                    end_yr = int(end_str)

                if 1990 <= start_yr <= CURRENT_YEAR and start_yr <= end_yr <= CURRENT_YEAR:
                    span_key = (start_yr, end_yr)
                    if span_key not in seen_spans:
                        seen_spans.add(span_key)
                        total_months += (end_yr - start_yr) * 12
            except Exception:
                continue

        years = total_months / 12.0
        # If no explicit ranges found, default to 1.5 yrs baseline
        return round(years, 1) if years > 0 else 1.5

    def detect_highest_degree(self, text: str) -> str:
        """Classifies highest academic degree detected."""
        for pattern, degree_name in DEGREE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return degree_name
        return "Bachelor's / Professional Degree"

    def measure_action_verb_density(self, text: str) -> Dict[str, Any]:
        """Evaluates resume impact through action verb usage."""
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        found_verbs = [w for w in words if w in ACTION_VERBS]
        unique_verbs = sorted(list(set(found_verbs)))
        score = min(100, int((len(unique_verbs) / 10.0) * 100))
        return {
            "action_verb_score": score,
            "unique_verbs_count": len(unique_verbs),
            "verbs_used": unique_verbs[:10]
        }

    def segment_sections(self, text: str) -> Dict[str, str]:
        lines = text.split("\n")
        sections: Dict[str, List[str]] = {
            "header": [], "summary": [], "skills": [],
            "experience": [], "education": [], "projects": [],
            "certifications": [], "interests": [], "other": []
        }
        current_section = "header"

        for line in lines:
            trimmed = line.strip()
            if not trimmed:
                continue
            matched_sec = None
            for sec_name, pattern in SECTION_PATTERNS.items():
                if pattern.match(trimmed):
                    matched_sec = sec_name
                    break
            if matched_sec:
                current_section = matched_sec
            else:
                sections[current_section].append(trimmed)

        return {k: "\n".join(v).strip() for k, v in sections.items() if v}

    def parse(self) -> Dict[str, Any]:
        raw_text = self.extract_text_from_pdf()
        cleaned = clean_text(raw_text)
        contact = self.extract_contact_info(raw_text)
        name = self.extract_name(raw_text)
        sections = self.segment_sections(raw_text)
        skills_info = extract_skills(raw_text)
        exp_years = self.estimate_experience_years(raw_text)
        degree = self.detect_highest_degree(raw_text)
        verb_metrics = self.measure_action_verb_density(raw_text)

        return {
            "file_name": os.path.basename(self.file_path),
            "file_path": os.path.abspath(self.file_path),
            "name": name,
            "contact": contact,
            "sections": sections,
            "skills": skills_info["all_skills"],
            "skills_by_category": skills_info["by_category"],
            "skill_frequencies": skills_info.get("frequencies", {}),
            "total_skills_count": skills_info["total_count"],
            "estimated_experience_years": exp_years,
            "highest_degree": degree,
            "action_verb_metrics": verb_metrics,
            "raw_text": raw_text,
            "cleaned_text": cleaned,
        }

def parse_resume(file_path: str) -> Dict[str, Any]:
    parser = ResumeParser(file_path)
    return parser.parse()
