"""
Text processing utilities for the Market Intelligence Bot.
"""

import re
from typing import Set

# Common stopwords to ignore in text processing
STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at",
    "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for",
    "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's",
    "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm",
    "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't",
    "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours",
    "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't",
    "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too",
    "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't",
    "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's",
    "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself",
    "yourselves"
}

# Financial-specific stopwords that may not be useful for relevance matching
FINANCIAL_STOPWORDS: Set[str] = {
    "market", "stock", "share", "price", "report", "says", "said", "today", "day", "week", "month", "year",
    "trading", "investor", "investment", "finance", "financial", "economy", "economic", "business", "news",
    "update", "latest", "breaking", "report", "analysis", "quarter", "earnings", "revenue", "profit", "loss"
}

def clean_text(text: str) -> str:
    """
    Clean text by removing special characters, extra whitespace, and normalizing.
    
    Args:
        text: Input text to clean
        
    Returns:
        Cleaned text string
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove special characters except letters, numbers and basic punctuation
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    
    # Replace multiple spaces, tabs, newlines with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text

def extract_keywords(text: str, exclude_stopwords: bool = True) -> list:
    """
    Extract important keywords from text.
    
    Args:
        text: Input text to extract keywords from
        exclude_stopwords: Whether to exclude stopwords
        
    Returns:
        List of keywords
    """
    # Clean the text
    cleaned_text = clean_text(text)
    
    # Split into words
    words = cleaned_text.split()
    
    # Filter out stopwords if requested
    if exclude_stopwords:
        words = [word for word in words if word.lower() not in STOPWORDS and len(word) > 2]
    
    return words

def contains_keywords(text: str, keywords: list) -> bool:
    """
    Check if text contains any of the provided keywords.
    
    Args:
        text: Text to check
        keywords: List of keywords to look for
        
    Returns:
        True if any keyword is found, False otherwise
    """
    cleaned_text = clean_text(text).lower()
    
    return any(keyword.lower() in cleaned_text for keyword in keywords)

def extract_numbers(text: str) -> list:
    """
    Extract numeric values from text.
    
    Args:
        text: Input text
        
    Returns:
        List of numbers found in the text
    """
    # Find all numbers (including decimal and percentages)
    numbers = re.findall(r'[-+]?\d*\.?\d+%?', text)
    return numbers 