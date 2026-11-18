"""
Module: career_recommendation.py
Description: Production Content-Based Career Recommendation Engine utilizing
TF-IDF Vectorization, Cosine Similarity, Skill Overlap, and Experience Eligibility Matching.
"""

import os
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.text_preprocessing import clean_text, preprocess_for_tfidf
from src.skill_extraction import extract_skills, calculate_skill_overlap

DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "sample_data", "job_roles_dataset.csv")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
VECTORIZER_FILE = os.path.join(MODELS_DIR, "career_tfidf_vectorizer.joblib")
ROLES_DB_FILE = os.path.join(MODELS_DIR, "job_roles_matrix.joblib")

class CareerRecommender:
    """Production recommendation system mapping candidate profile to the best-fit career roles."""

    def __init__(self, dataset_path: str = DATASET_PATH, models_dir: str = MODELS_DIR):
        self.dataset_path = dataset_path
        self.models_dir = models_dir
        self.df_roles: Optional[pd.DataFrame] = None
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.role_tfidf_matrix = None

        os.makedirs(self.models_dir, exist_ok=True)
        self.train_and_save_model()

    def _load_data(self) -> pd.DataFrame:
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"Job roles dataset not found at: {self.dataset_path}")
        df = pd.read_csv(self.dataset_path)
        # Combine rich multi-field representation for NLP vectorization
        df["combined_features"] = df.apply(
            lambda row: f"{row['role_name']} {row['role_name']} {row['category']} {row.get('subcategory', '')} "
                        f"{str(row['required_skills']).replace(',', ' ')} "
                        f"{str(row['required_skills']).replace(',', ' ')} "
                        f"{str(row.get('secondary_skills', '')).replace(',', ' ')} "
                        f"{str(row.get('tools_and_frameworks', '')).replace(',', ' ')} "
                        f"{row['job_description']}",
            axis=1
        )
        df["preprocessed_features"] = df["combined_features"].apply(preprocess_for_tfidf)
        return df

    def train_and_save_model(self):
        """Fits TF-IDF vectorizer on dataset and caches artifacts."""
        self.df_roles = self._load_data()
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)
        self.role_tfidf_matrix = self.vectorizer.fit_transform(self.df_roles["preprocessed_features"])

        joblib.dump(self.vectorizer, VECTORIZER_FILE)
        joblib.dump((self.df_roles, self.role_tfidf_matrix), ROLES_DB_FILE)

    def get_categories(self) -> List[str]:
        """Returns all distinct career categories in dataset."""
        if self.df_roles is None:
            self.train_and_save_model()
        return sorted(list(self.df_roles["category"].unique()))

    def recommend(
        self,
        candidate_profile: Dict[str, Any],
        top_k: int = 5,
        category_filter: Optional[str] = None,
        min_experience_cap: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Computes composite career alignment scores combining:
        - 45% Required skills overlap
        - 20% Secondary & framework skills overlap
        - 25% TF-IDF Cosine semantic similarity
        - 10% Seniority/Experience eligibility matching
        """
        if self.df_roles is None or self.vectorizer is None:
            self.train_and_save_model()

        candidate_skills = set(candidate_profile.get("skills", []))
        candidate_text = candidate_profile.get("cleaned_text", "")
        cand_exp = candidate_profile.get("estimated_experience_years", 2.0)

        skills_boost = " ".join(candidate_skills) + " " + " ".join(candidate_skills)
        combined_candidate_text = preprocess_for_tfidf(f"{skills_boost} {candidate_text}")

        candidate_vec = self.vectorizer.transform([combined_candidate_text])
        tfidf_similarities = cosine_similarity(candidate_vec, self.role_tfidf_matrix).flatten()

        recommendations = []

        for idx, row in self.df_roles.iterrows():
            # Category filter
            if category_filter and category_filter != "All":
                if row["category"].lower() != category_filter.lower():
                    continue

            req_skills = [s.strip().lower() for s in str(row["required_skills"]).split(",") if s.strip()]
            sec_skills = [s.strip().lower() for s in str(row.get("secondary_skills", "")).split(",") if s.strip()]
            tools = [s.strip().lower() for s in str(row.get("tools_and_frameworks", "")).split(",") if s.strip()]
            all_target_skills = req_skills + sec_skills + tools

            matching_req, missing_req, req_ratio = calculate_skill_overlap(list(candidate_skills), req_skills)
            matching_all, _, all_ratio = calculate_skill_overlap(list(candidate_skills), all_target_skills)

            tfidf_score = float(tfidf_similarities[idx])

            # Experience alignment score (1.0 if candidate meets or exceeds min exp, scaled down if deficit)
            role_min_exp = float(row.get("min_experience_years", 1.0))
            if min_experience_cap is not None and role_min_exp > min_experience_cap:
                continue

            if cand_exp >= role_min_exp:
                exp_fit = 1.0
            else:
                exp_fit = max(0.4, cand_exp / max(1.0, role_min_exp))

            composite_score = (0.45 * req_ratio) + (0.20 * all_ratio) + (0.25 * tfidf_score) + (0.10 * exp_fit)
            match_percentage = round(min(1.0, max(0.0, composite_score)) * 100, 1)

            recommendations.append({
                "role_id": int(row["role_id"]),
                "role_name": row["role_name"],
                "category": row["category"],
                "subcategory": row.get("subcategory", ""),
                "match_percentage": match_percentage,
                "tfidf_similarity": round(tfidf_score * 100, 1),
                "required_skill_match_pct": round(req_ratio * 100, 1),
                "matched_skills": sorted(list(matching_req)),
                "missing_skills": sorted(list(missing_req)),
                "min_experience_years": role_min_exp,
                "experience_level": row["experience_level"],
                "education_level": row["education_level"],
                "market_demand": row.get("market_demand", "High"),
                "avg_salary_range": row["avg_salary_range"],
                "job_description": row["job_description"],
            })

        recommendations.sort(key=lambda x: x["match_percentage"], reverse=True)
        return recommendations[:top_k]

    def search_roles(self, query: str) -> List[Dict[str, Any]]:
        """Quick keyword search across roles catalog."""
        if self.df_roles is None:
            self.train_and_save_model()
        q = query.lower().strip()
        matches = []
        for _, row in self.df_roles.iterrows():
            if q in row["role_name"].lower() or q in row["category"].lower() or q in str(row["required_skills"]).lower():
                matches.append(row.to_dict())
        return matches
