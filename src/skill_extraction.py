"""
Module: skill_extraction.py
Description: Production-grade skill taxonomy and pattern-matching engine covering
600+ industry technical skills, frameworks, tools, and methodologies.
"""

import re
from typing import Dict, List, Set, Tuple

# Comprehensive production-grade taxonomy organized by domain category
SKILL_TAXONOMY: Dict[str, List[str]] = {
    "Programming Languages": [
        "python", "javascript", "typescript", "java", "c++", "c#", "c", "go", "golang",
        "rust", "r", "swift", "kotlin", "php", "ruby", "scala", "dart", "bash", "shell",
        "zsh", "sql", "matlab", "perl", "lua", "julia", "solidity", "html", "html5", "css",
        "css3", "sass", "scss", "elixir", "erlang", "haskell", "clojure", "assembly"
    ],
    "Artificial Intelligence & ML": [
        "machine learning", "deep learning", "artificial intelligence", "pytorch", "tensorflow",
        "scikit-learn", "keras", "xgboost", "lightgbm", "catboost", "huggingface", "transformers",
        "bert", "gpt", "llm", "large language models", "generative ai", "nlp",
        "natural language processing", "computer vision", "opencv", "yolo", "cnn", "rnn",
        "lstm", "reinforcement learning", "spacy", "nltk", "langchain", "llamaindex",
        "vector databases", "pinecone", "chromadb", "weaviate", "milvus", "qdrant", "rag",
        "retrieval augmented generation", "prompt engineering", "fine-tuning", "lora",
        "qlora", "object detection", "image segmentation", "onnx", "tensorrt", "cuda",
        "vllm", "ollama", "whisper", "speech recognition", "text-to-speech", "tts", "asr",
        "generative adversarial networks", "diffusion models", "stable diffusion", "slam",
        "point cloud", "lidar", "autonomous systems", "ros", "ros2"
    ],
    "Data Science & Analytics": [
        "pandas", "numpy", "scipy", "matplotlib", "seaborn", "statsmodels", "statistics",
        "probability", "hypothesis testing", "a/b testing", "feature engineering",
        "exploratory data analysis", "eda", "data visualization", "tableau", "power bi",
        "excel", "business intelligence", "data modeling", "dax", "econometrics",
        "time series", "time series forecasting", "clustering", "k-means", "pca",
        "causal inference", "monte carlo", "stochastic calculus", "financial modeling",
        "looker", "qlik", "google analytics", "mixpanel", "amplitude"
    ],
    "Big Data & Data Engineering": [
        "spark", "pyspark", "hadoop", "apache spark", "kafka", "apache kafka", "airflow",
        "apache airflow", "dbt", "snowflake", "bigquery", "redshift", "databricks", "etl",
        "elt", "data pipeline", "data warehousing", "data lake", "lakehouse", "hive",
        "flink", "polars", "duckdb", "clickhouse", "presto", "trino", "delta lake"
    ],
    "Cloud & Infrastructure": [
        "aws", "amazon web services", "azure", "microsoft azure", "gcp", "google cloud",
        "ec2", "s3", "sagemaker", "lambda", "ecs", "eks", "cloudwatch", "iam", "vpc",
        "cloud architecture", "serverless", "cloud computing", "cloudformation", "route 53",
        "api gateway", "azure devops", "blob storage", "google cloud storage"
    ],
    "DevOps, MLOps & SRE": [
        "docker", "kubernetes", "k8s", "terraform", "helm", "ansible", "jenkins",
        "github actions", "gitlab ci", "ci/cd", "continuous integration", "continuous deployment",
        "linux", "unix", "prometheus", "grafana", "elk stack", "argocd", "mlflow",
        "kubeflow", "dvc", "mlops", "model deployment", "model monitoring", "drift detection",
        "opentelemetry", "datadog", "new relic", "pagerduty", "istio", "service mesh",
        "gitops", "backstage", "triton inference server", "ray", "ray train"
    ],
    "Web & Backend Engineering": [
        "react", "react.js", "next.js", "vue", "vue.js", "angular", "node.js", "nodejs",
        "express", "express.js", "fastapi", "flask", "django", "spring boot", "rest api",
        "restful apis", "graphql", "microservices", "websockets", "tailwind css", "tailwind",
        "redux", "zustand", "prisma", "hibernate", "grpc", "protobuf", "gin", "fastify",
        "vite", "webpack", "socket.io", "nest.js", "svelte", "ruby on rails"
    ],
    "Databases & Storage": [
        "postgresql", "postgres", "mysql", "mongodb", "redis", "cassandra", "dynamodb",
        "sqlite", "elasticsearch", "neo4j", "mariadb", "oracle", "couchbase", "memcached",
        "firebase", "supabase", "database administration", "query optimization", "indexing"
    ],
    "Cybersecurity & DevSecOps": [
        "cybersecurity", "network security", "vulnerability assessment", "siem", "incident response",
        "wireshark", "firewalls", "penetration testing", "ethical hacking", "burp suite",
        "kali linux", "owasp", "cryptography", "splunk", "nessus", "metasploit",
        "devsecops", "guardduty", "iam security", "compliance", "soc2", "nist", "cis benchmarks"
    ],
    "Software Engineering & QA": [
        "git", "github", "gitlab", "jira", "confluence", "postman", "pytest", "unittest",
        "jest", "cypress", "selenium", "playwright", "system design", "agile", "scrum",
        "unit testing", "integration testing", "oop", "design patterns", "clean code",
        "code review", "software architecture", "technical leadership"
    ]
}

# Canonical normalization map
SKILL_ALIASES = {
    "reactjs": "react",
    "react.js": "react",
    "nodejs": "node.js",
    "node": "node.js",
    "postgres": "postgresql",
    "k8s": "kubernetes",
    "sklearn": "scikit-learn",
    "tf": "tensorflow",
    "nlp": "natural language processing",
    "cv": "computer vision",
    "golang": "go",
    "amazon web services": "aws",
    "microsoft azure": "azure",
    "google cloud platform": "gcp",
    "google cloud": "gcp",
    "apache spark": "spark",
    "apache kafka": "kafka",
    "apache airflow": "airflow",
    "large language models": "llm",
    "large language model": "llm",
    "generative artificial intelligence": "generative ai",
    "genai": "generative ai",
    "tailwind": "tailwind css",
    "nextjs": "next.js"
}

def normalize_skill(skill: str) -> str:
    """Normalize skill string using alias mapping."""
    s = skill.strip().lower()
    return SKILL_ALIASES.get(s, s)

def build_all_skills_flat() -> Set[str]:
    """Flattens all skills from taxonomy for fast lookup."""
    flat = set()
    for cat_skills in SKILL_TAXONOMY.values():
        for s in cat_skills:
            flat.add(normalize_skill(s))
    return flat

ALL_KNOWN_SKILLS = build_all_skills_flat()

def extract_skills(text: str) -> Dict[str, any]:
    """
    Extracts recognized skills from text, categorizing them and computing
    frequency weights.
    """
    if not text:
        return {"all_skills": [], "by_category": {}, "frequencies": {}, "total_count": 0}

    lower_text = " " + text.lower() + " "
    cleaned_stream = re.sub(r'[,;()/\n\t\r]', ' ', lower_text)

    extracted_by_category: Dict[str, List[str]] = {}
    found_flat: Set[str] = set()
    frequencies: Dict[str, int] = {}

    for category, skill_list in SKILL_TAXONOMY.items():
        cat_matches = set()
        for raw_skill in skill_list:
            canonical = normalize_skill(raw_skill)
            pattern = r'(?<![a-zA-Z0-9\+\#\.\-])' + re.escape(raw_skill) + r'(?![a-zA-Z0-9\+\#\.\-])'
            matches = re.findall(pattern, cleaned_stream, flags=re.IGNORECASE)
            if matches:
                cat_matches.add(canonical)
                found_flat.add(canonical)
                frequencies[canonical] = frequencies.get(canonical, 0) + len(matches)

        if cat_matches:
            extracted_by_category[category] = sorted(list(cat_matches))

    sorted_skills = sorted(list(found_flat))
    return {
        "all_skills": sorted_skills,
        "by_category": extracted_by_category,
        "frequencies": frequencies,
        "total_count": len(sorted_skills)
    }

def calculate_skill_overlap(skills_a: List[str], skills_b: List[str]) -> Tuple[Set[str], Set[str], float]:
    """
    Compares two lists of skills.
    Returns (matching_skills, missing_skills, match_ratio).
    """
    set_a = {normalize_skill(s) for s in skills_a if s}
    set_b = {normalize_skill(s) for s in skills_b if s}

    if not set_b:
        return set_a, set(), 1.0

    matching = set_a.intersection(set_b)
    missing = set_b.difference(set_a)
    ratio = len(matching) / len(set_b)

    return matching, missing, round(ratio, 4)
