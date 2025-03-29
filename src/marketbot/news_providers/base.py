"""
Base news provider class.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any

class NewsProvider(ABC):
    """Base class for all news providers."""
    
    @abstractmethod
    def fetch_news(self, query: str = None) -> List[Dict[str, Any]]:
        """
        Fetch news articles.
        
        Args:
            query: Optional search query
            
        Returns:
            List of news article dictionaries
        """
        pass
    
    def normalize_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize article data to a standard format.
        
        Args:
            article: Raw article data
            
        Returns:
            Normalized article dictionary
        """
        # Ensure these fields are always present
        return {
            "title": article.get("title", "No title"),
            "url": article.get("url", ""),
            "source": article.get("source", {"name": "Unknown"}) if isinstance(article.get("source"), dict) else {"name": article.get("source", "Unknown")},
            "publishedAt": article.get("publishedAt", ""),
            "time": article.get("time", "Recent"),
            "content": article.get("content", "")
        } 