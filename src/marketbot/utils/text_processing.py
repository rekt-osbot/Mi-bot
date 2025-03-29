"""
Text processing utilities for the Market Intelligence Bot.
"""

import re
import logging
import string
from typing import List, Optional, Dict, Any, Set

logger = logging.getLogger(__name__)

# Key terms for categorizing user queries
MARKET_TERMS = {
    "general": [
        "market", "stock", "equity", "invest", "portfolio", "finance",
        "bazaar", "share", "trading", "mutual fund", "etf", "index"
    ],
    "country_specific": [
        "us", "usa", "american", "india", "indian", "global", "world",
        "sensex", "nifty", "dow", "nasdaq", "s&p", "wall street"
    ],
    "topic_specific": [
        "commodity", "gold", "silver", "oil", "crypto", "bitcoin", 
        "currency", "forex", "dollar", "rupee", "merger", "acquisition",
        "ipo", "listing", "earning", "profit", "revenue", "breaking"
    ],
    "technical_analysis": [
        "technical", "chart", "pattern", "support", "resistance", 
        "trend", "moving average", "macd", "rsi", "indicator"
    ]
}

# Whitelist of user IDs that can always use the bot (VIPs, group admins, etc.)
# These users bypass the admin-only restriction but not the market-related message check
WHITELISTED_USER_IDS = {
    "1186795432",  # Example user ID - replace with actual user IDs
    "1295425639"   # Add more as needed
}

def is_user_whitelisted(user_id: str) -> bool:
    """
    Check if a user is whitelisted to use the bot.
    
    Args:
        user_id: Telegram user ID as a string
        
    Returns:
        True if the user is whitelisted
    """
    return user_id in WHITELISTED_USER_IDS

def clean_text(text: str) -> str:
    """
    Clean text by removing punctuation and extra whitespace.
    
    Args:
        text: Input text to clean
        
    Returns:
        Cleaned text
    """
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def extract_keywords(text: str) -> List[str]:
    """
    Extract meaningful keywords from text.
    
    Args:
        text: Input text to extract keywords from
        
    Returns:
        List of keywords
    """
    # Clean text
    clean = clean_text(text.lower())
    
    # Split into words
    words = clean.split()
    
    # Remove common stopwords
    stopwords = {
        'a', 'an', 'the', 'and', 'or', 'but', 'if', 'because', 'as', 'what',
        'when', 'where', 'how', 'why', 'who', 'which', 'this', 'that', 'these',
        'those', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
        'had', 'do', 'does', 'did', 'can', 'could', 'will', 'would', 'should', 'may',
        'might', 'must', 'shall', 'me', 'my', 'myself', 'you', 'your', 'yourself',
        'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its',
        'itself', 'we', 'us', 'our', 'ours', 'ourselves', 'they', 'them', 'their',
        'theirs', 'themselves', 'on', 'in', 'at', 'by', 'with', 'from', 'to', 'for',
        'of', 'about', 'against', 'between', 'into', 'through', 'during', 'before',
        'after', 'above', 'below', 'up', 'down', 'out', 'off', 'over', 'under',
        'again', 'further', 'then', 'once', 'here', 'there', 'all', 'any', 'both',
        'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
        'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'just', 'don',
        'should', 'now', 'get', 'got', 'i', "i'm", "i'll", "i've", "i'd"
    }
    
    # Hindi stopwords
    hindi_stopwords = {
        'का', 'के', 'की', 'है', 'हैं', 'था', 'थे', 'थी', 'से', 'को', 'पर', 'में',
        'और', 'या', 'एक', 'जो', 'मैं', 'मुझे', 'मेरा', 'मेरी', 'हम', 'हमारा',
        'हमारी', 'आप', 'आपका', 'आपकी', 'वह', 'उसका', 'उसकी', 'वे', 'उनका', 'उनकी',
        'यह', 'ये', 'इसका', 'इसकी', 'अब', 'तब', 'जब', 'क्या', 'कौन', 'किस', 'कहा',
        'कैसे', 'मगर', 'लेकिन', 'फिर', 'भी', 'तो', 'ही', 'तक', 'साथ', 'बाद', 'पहले',
        'क्यों', 'कि', 'हो', 'होना', 'होता', 'होती', 'करना', 'करता', 'करती', 'जा',
        'रहा', 'रही', 'थी', 'थे', 'था', 'उन', 'इन', 'वही', 'कई', 'करें', 'देने',
        'बहुत', 'सकता', 'सकती', 'पास', 'अपना', 'अपनी', 'अपने'
    }
    
    # Combine stopwords
    all_stopwords = stopwords.union(hindi_stopwords)
    
    # Filter out stopwords
    keywords = [word for word in words if word not in all_stopwords and len(word) > 2]
    
    return keywords


def extract_percentage(text: str) -> Optional[float]:
    """
    Extract percentage value from text.
    
    Args:
        text: Input text
        
    Returns:
        Extracted percentage as float or None if not found
    """
    percentage_match = re.search(r'(\d+\.?\d*)(\s?%|\s?percent)', text)
    if percentage_match:
        return float(percentage_match.group(1))
    return None


def truncate_text(text: str, max_length: int = 100, preserve_words: bool = True) -> str:
    """
    Truncate text to a maximum length, preserving whole words.
    
    Args:
        text: Input text
        max_length: Maximum length of the output text
        preserve_words: Whether to preserve whole words
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
        
    if preserve_words:
        # Find a good breaking point
        truncated = text[:max_length]
        last_space = truncated.rfind(' ')
        
        if last_space > max_length * 0.7:  # Only break at space if it's not too short
            return truncated[:last_space] + '...'
    
    return text[:max_length] + '...'


def format_bullet_points(items: List[str], bullet_char: str = '•') -> str:
    """
    Format a list of items as bullet points.
    
    Args:
        items: List of items to format
        bullet_char: Character to use as bullet
        
    Returns:
        Formatted bullet point string
    """
    return '\n'.join([f"{bullet_char} {item}" for item in items])


def format_dict_as_table(data: Dict[str, Any]) -> str:
    """
    Format a dictionary as a simple text table.
    
    Args:
        data: Dictionary to format
        
    Returns:
        Formatted table
    """
    if not data:
        return ""
        
    # Find the longest key for padding
    max_key_length = max(len(str(k)) for k in data.keys())
    
    # Format each line
    lines = []
    for key, value in data.items():
        lines.append(f"{str(key):<{max_key_length}} : {value}")
    
    return '\n'.join(lines)


def categorize_query(text: str) -> str:
    """
    Categorize a user query based on its content.
    
    Args:
        text: User query text
        
    Returns:
        Category: "country_specific", "topic_specific", "technical_analysis", or "general"
    """
    text_lower = text.lower()
    
    # Count term occurrences by category
    category_scores = {}
    for category, terms in MARKET_TERMS.items():
        score = sum(1 for term in terms if term in text_lower)
        category_scores[category] = score
    
    # Check for specific country mentions
    if re.search(r'\b(india|indian|nifty|sensex)\b', text_lower):
        category_scores["country_specific"] += 3
    if re.search(r'\b(us|usa|american|dow|nasdaq|s&p|wall street)\b', text_lower):
        category_scores["country_specific"] += 3
        
    # Check for technical analysis specific terms
    if re.search(r'\b(chart pattern|technical indicator|trading setup|moving average|support and resistance)\b', text_lower):
        category_scores["technical_analysis"] += 3
        
    # Find the category with the highest score
    max_category = "general"
    max_score = 0
    
    for category, score in category_scores.items():
        if score > max_score:
            max_score = score
            max_category = category
            
    return max_category


def clean_query(text: str) -> str:
    """
    Clean a user query by removing unnecessary elements.
    
    Args:
        text: User query text
        
    Returns:
        Cleaned query text
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text


def extract_entities(text: str) -> Dict[str, List[str]]:
    """
    Extract named entities from text.
    
    Args:
        text: Text to extract entities from
        
    Returns:
        Dictionary of entity types and their values
    """
    entities = {
        'countries': [],
        'indices': [],
        'commodities': [],
        'companies': []
    }
    
    # Define patterns for different entity types
    country_pattern = r'\b(us|usa|united states|india|china|japan|europe|uk|britain)\b'
    index_pattern = r'\b(dow|nasdaq|s&p|sensex|nifty|ftse|dax|nikkei)\b'
    commodity_pattern = r'\b(gold|silver|oil|crude|gas|copper|metal)\b'
    
    # Extract countries
    matches = re.findall(country_pattern, text.lower())
    if matches:
        entities['countries'] = list(set(matches))
    
    # Extract indices
    matches = re.findall(index_pattern, text.lower())
    if matches:
        entities['indices'] = list(set(matches))
    
    # Extract commodities
    matches = re.findall(commodity_pattern, text.lower())
    if matches:
        entities['commodities'] = list(set(matches))
    
    return entities


def is_question(text: str) -> bool:
    """
    Determine if text is a question.
    
    Args:
        text: Text to check
        
    Returns:
        True if the text appears to be a question
    """
    # Check for question mark
    if '?' in text:
        return True
        
    # Check for question starters
    question_starters = [
        'what', 'when', 'where', 'who', 'whom', 'which', 'whose',
        'why', 'how', 'is', 'are', 'am', 'was', 'were', 'will', 'do',
        'does', 'did', 'can', 'could', 'should', 'would', 'may', 'might',
        'kya', 'kab', 'kahan', 'kaun', 'kaise', 'kyun', 'kyu', 'kahaan'
    ]
    
    # Clean and get first word
    text_lower = text.lower().strip()
    if text_lower.split()[0] in question_starters:
        return True
        
    return False 