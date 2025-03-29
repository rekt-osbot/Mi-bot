"""
Tests for the news functionality of the Market Intelligence Bot.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
from typing import List, Dict, Any

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

from marketbot.news_providers.base import NewsProvider
from marketbot.news_providers.google_news import GoogleNewsProvider
from marketbot.news_providers.financial_site import FinancialSiteProvider
from marketbot.services.content_analyzer import ContentAnalyzer
from marketbot.services.news_service import NewsService

class MockNewsProvider(NewsProvider):
    """Mock news provider for testing."""
    
    def __init__(self, mock_data=None):
        self.mock_data = mock_data or []
    
    def fetch_news(self, query=None) -> List[Dict[str, Any]]:
        """Return mock news data."""
        return self.mock_data

class TestNewsProvider(unittest.TestCase):
    """Test the base NewsProvider class."""
    
    def test_normalize_article(self):
        """Test article normalization."""
        provider = MockNewsProvider()
        
        # Test with minimum data
        article = {"title": "Test Title", "url": "https://example.com/test"}
        normalized = provider.normalize_article(article)
        
        self.assertEqual(normalized["title"], "Test Title")
        self.assertEqual(normalized["url"], "https://example.com/test")
        self.assertIn("source", normalized)
        self.assertIn("name", normalized["source"])
        self.assertIn("publishedAt", normalized)
        self.assertIn("time", normalized)
        
        # Test with more data
        article = {
            "title": "Test Title", 
            "url": "https://example.com/test",
            "source": {"name": "Test Source"},
            "publishedAt": "2023-01-01T12:00:00Z",
            "time": "1 day ago"
        }
        normalized = provider.normalize_article(article)
        
        self.assertEqual(normalized["title"], "Test Title")
        self.assertEqual(normalized["url"], "https://example.com/test")
        self.assertEqual(normalized["source"]["name"], "Test Source")
        self.assertEqual(normalized["publishedAt"], "2023-01-01T12:00:00Z")
        self.assertEqual(normalized["time"], "1 day ago")

class TestContentAnalyzer(unittest.TestCase):
    """Test the ContentAnalyzer class."""
    
    def setUp(self):
        """Set up test data."""
        self.analyzer = ContentAnalyzer()
        
        self.test_articles = [
            {
                "title": "Nifty rises 2% on positive market sentiment",
                "url": "https://example.com/article1",
                "source": {"name": "Test News"},
                "publishedAt": "2023-01-01T12:00:00Z",
                "time": "1 hour ago"
            },
            {
                "title": "Banking sector under pressure as rates increase",
                "url": "https://example.com/article2",
                "source": {"name": "Test News"},
                "publishedAt": "2023-01-01T11:00:00Z",
                "time": "2 hours ago"
            },
            {
                "title": "Tech stocks showing mixed performance",
                "url": "https://example.com/article3",
                "source": {"name": "Test News"},
                "publishedAt": "2023-01-01T10:00:00Z",
                "time": "3 hours ago"
            }
        ]
    
    @patch('marketbot.services.content_analyzer.requests.get')
    def test_extract_article_content(self, mock_get):
        """Test article content extraction."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = """
        <html>
            <body>
                <article>
                    <p>This is a test paragraph.</p>
                    <p>This is another test paragraph with more content to ensure it's long enough.</p>
                </article>
            </body>
        </html>
        """
        mock_get.return_value = mock_response
        
        content = self.analyzer.extract_article_content("https://example.com/test")
        self.assertIsNotNone(content)
        self.assertIn("test paragraph", content)
    
    def test_generate_market_insight(self):
        """Test market insight generation."""
        text = "Nifty rises by 2% due to positive global cues and strong economic data."
        insight = self.analyzer.generate_market_insight(text, positive=True)
        
        self.assertIsNotNone(insight)
        self.assertIn("Nifty", insight)
        self.assertIn("due to positive global cues", insight)
    
    def test_generate_sector_insight(self):
        """Test sector insight generation."""
        text = "Banking sector stocks are under pressure due to rising interest rates."
        insight = self.analyzer.generate_sector_insight(text, "banking")
        
        self.assertIsNotNone(insight)
        self.assertIn("Banking", insight)
        self.assertIn("under pressure", insight)
    
    def test_get_market_insights(self):
        """Test market insights generation."""
        insights = self.analyzer.get_market_insights(self.test_articles)
        
        self.assertIsInstance(insights, list)
        self.assertTrue(len(insights) > 0)
    
    def test_format_news_with_insights(self):
        """Test news formatting with insights."""
        formatted_news = self.analyzer.format_news_with_insights(self.test_articles)
        
        self.assertIsInstance(formatted_news, str)
        self.assertIn("MARKET INTELLIGENCE REPORT", formatted_news)
        self.assertIn("LATEST NEWS", formatted_news)

class TestNewsService(unittest.TestCase):
    """Test the NewsService class."""
    
    @patch('marketbot.services.news_service.GoogleNewsProvider')
    @patch('marketbot.services.news_service.FinancialSiteProvider')
    def setUp(self, mock_financial_provider, mock_google_provider):
        """Set up test data and mocks."""
        # Mock Google News provider
        self.mock_google_news = MagicMock()
        self.mock_google_news.fetch_news.return_value = [
            {
                "title": "Google News Article 1",
                "url": "https://example.com/gnews1",
                "source": {"name": "Google News"},
                "publishedAt": "2023-01-01T12:00:00Z",
                "time": "1 hour ago"
            }
        ]
        mock_google_provider.return_value = self.mock_google_news
        
        # Mock Financial Site providers
        self.mock_moneycontrol = MagicMock()
        self.mock_moneycontrol.fetch_news.return_value = [
            {
                "title": "MoneyControl Article 1",
                "url": "https://example.com/mc1",
                "source": {"name": "MoneyControl"},
                "publishedAt": "2023-01-01T11:00:00Z",
                "time": "2 hours ago"
            }
        ]
        
        self.mock_financial_express = MagicMock()
        self.mock_financial_express.fetch_news.return_value = [
            {
                "title": "Financial Express Article 1",
                "url": "https://example.com/fe1",
                "source": {"name": "Financial Express"},
                "publishedAt": "2023-01-01T10:00:00Z",
                "time": "3 hours ago"
            }
        ]
        
        self.mock_economic_times = MagicMock()
        self.mock_economic_times.fetch_news.return_value = [
            {
                "title": "Economic Times Article 1",
                "url": "https://example.com/et1",
                "source": {"name": "Economic Times"},
                "publishedAt": "2023-01-01T09:00:00Z",
                "time": "4 hours ago"
            }
        ]
        
        # Set up return values for the FinancialSiteProvider class methods
        mock_financial_provider.moneycontrol.return_value = self.mock_moneycontrol
        mock_financial_provider.financial_express.return_value = self.mock_financial_express
        mock_financial_provider.economic_times.return_value = self.mock_economic_times
        
        # Mock ContentAnalyzer
        self.mock_content_analyzer = MagicMock()
        self.mock_content_analyzer.format_news_with_insights.return_value = "Formatted news with insights"
        
        # Initialize NewsService with mocks
        self.news_service = NewsService()
        self.news_service.content_analyzer = self.mock_content_analyzer
    
    def test_fetch_news_from_all_sources(self):
        """Test fetching news from all sources."""
        news_items = self.news_service.fetch_news_from_all_sources()
        
        # Verify Google News provider was called
        self.mock_google_news.fetch_news.assert_called_once()
        
        # Verify all financial site providers were called
        self.mock_moneycontrol.fetch_news.assert_called_once()
        self.mock_financial_express.fetch_news.assert_called_once()
        self.mock_economic_times.fetch_news.assert_called_once()
        
        # Verify we got news items back
        self.assertIsInstance(news_items, list)
        self.assertTrue(len(news_items) > 0)
    
    def test_get_market_news(self):
        """Test getting market news with insights."""
        news_data = self.news_service.get_market_news()
        
        # Verify format_news_with_insights was called
        self.mock_content_analyzer.format_news_with_insights.assert_called_once()
        
        # Verify the returned data structure
        self.assertIn("news_items", news_data)
        self.assertIn("formatted_message", news_data)
        self.assertIn("count", news_data)
        self.assertIn("processing_time", news_data)
        
        # Verify the formatted message
        self.assertEqual(news_data["formatted_message"], "Formatted news with insights")
    
    def test_get_topic_news(self):
        """Test getting topic-specific news."""
        # Test with a valid topic
        news_data = self.news_service.get_topic_news("india")
        
        # Verify fetch_news_from_all_sources was called with a query
        self.mock_google_news.fetch_news.assert_called()
        
        # Verify the returned data structure
        self.assertIn("news_items", news_data)
        self.assertIn("formatted_message", news_data)
        
        # Test with an invalid topic
        news_data = self.news_service.get_topic_news("invalid_topic")
        
        # Verify the returned data structure for invalid topic
        self.assertEqual(news_data["count"], 0)
        self.assertIn("No predefined search query", news_data["formatted_message"])

if __name__ == "__main__":
    unittest.main() 