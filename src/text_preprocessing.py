"""
Module: text_preprocessing.py
Description: Natural Language Processing text cleaning, tokenization,
stopword removal, and normalization pipeline.
"""

import re
import string
from typing import List, Set

# Built-in robust English stopwords fallback if NLTK stopwords are unavailable
FALLBACK_STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
    "but", "by", "can", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does",
    "doesn't", "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had",
    "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
    "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd",
    "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself",
    "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off",
    "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over",
    "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so",
    "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've",
    "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't",
    "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when",
    "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's",
    "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your",
    "yours", "yourself", "yourselves"
}

def get_stopwords() -> Set[str]:
    """Retrieve NLTK stopwords if available, otherwise return fallback stopwords."""
    try:
        from nltk.corpus import stopwords
        return set(stopwords.words("english"))
    except Exception:
        return FALLBACK_STOPWORDS

STOPWORDS = get_stopwords()

def clean_text(text: str) -> str:
    """
    Cleans raw text by removing URLs, non-ascii characters, extra whitespace,
    and standardizing newlines.
    """
    if not text:
        return ""
    
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
    # Remove email addresses from generic text stream (kept in contact parsing)
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', ' ', text)
    # Remove phone numbers
    text = re.sub(r'\+?\d[\d\s\-().]{8,}\d', ' ', text)
    # Replace unicode dashes, bullets, quotes with standard chars
    text = text.replace('\u2022', ' ').replace('\u2013', '-').replace('\u2014', '-')
    text = text.replace('\u201c', '"').replace('\u201d', '"').replace('\u2018', "'").replace('\u2019', "'")
    # Replace non-word / non-punctuation chars
    text = re.sub(r'[^\w\s\-\+\#\.\/]', ' ', text)
    # Collapse multiple whitespaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def tokenize(text: str, remove_stop: bool = True, min_len: int = 2) -> List[str]:
    """
    Tokenizes text into words, preserving programming terms like c++, c#, .net.
    Optionally filters stopwords and short tokens.
    """
    cleaned = clean_text(text).lower()
    # Tokenizer pattern preserving C++, C#, .NET, Node.js etc.
    tokens = re.findall(r'[a-zA-Z0-9\+\#\.\-]+', cleaned)
    
    # Strip boundary punctuation but preserve C++, C#, etc.
    filtered_tokens = []
    for token in tokens:
        # Strip trailing dots or dashes
        t = token.strip('.-_')
        if not t:
            continue
        if len(t) < min_len:
            continue
        if remove_stop and t in STOPWORDS:
            continue
        filtered_tokens.append(t)
        
    return filtered_tokens

def extract_ngrams(tokens: List[str], n: int = 2) -> List[str]:
    """Extract n-grams from a list of tokens."""
    if len(tokens) < n:
        return []
    return [" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]

def preprocess_for_tfidf(text: str) -> str:
    """Preprocess text specifically for TF-IDF vectorizer representation."""
    tokens = tokenize(text, remove_stop=True)
    return " ".join(tokens)
