"""
Unit tests for the NewsService class.
"""

import unittest
from unittest.mock import patch, MagicMock

from marketbot.services.news_service import NewsService
from marketbot.news_providers.google_news import GoogleNewsProvider
from marketbot.news_providers.financial_site import FinancialSiteProvider

class TestNewsService(unittest.TestCase):
    """Test suite for the NewsService class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.news_service = NewsService()
        
        # Sample news articles for testing
        self.sample_articles = [
            {
                'title': 'Sensex rises 500 points on positive global cues',
                'url': 'https://example.com/article1',
                'source': 'SampleSource1',
                'publishedAt': '2023-10-15T10:30:00Z',
                'time': '3 hours ago'
            },
            {
                'title': 'Nifty crosses 20,000 mark for the first time',
                'url': 'https://example.com/article2',
                'source': 'SampleSource2',
                'publishedAt': '2023-10-15T09:15:00Z',
                'time': '4 hours ago'
            },
            {
                'title': 'Banking stocks lead market rally as Sensex gains',
                'url': 'https://example.com/article3',
                'source': 'SampleSource3',
                'publishedAt': '2023-10-15T08:45:00Z',
                'time': '5 hours ago'
            }
        ]
    
    @patch.object(GoogleNewsProvider, 'fetch_news')
    @patch.object(FinancialSiteProvider, 'fetch_news')
    def test_fetch_news_from_all_sources(self, mock_financial_fetch, mock_google_fetch):
        """Test fetching news from all sources."""
        # Configure mocks
        mock_google_fetch.return_value = self.sample_articles[:1]
        
        # Mock each financial site provider
        mock_financial_fetch.side_effect = [
            self.sample_articles[1:2],  # MoneyControl
            self.sample_articles[2:],   # Financial Express
            []                          # Economic Times (empty)
        ]
        
        # Call the method
        results = self.news_service.fetch_news_from_all_sources()
        
        # Assertions
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]['title'], self.sample_articles[0]['title'])
        mock_google_fetch.assert_called_once()
        self.assertEqual(mock_financial_fetch.call_count, 3)
    
    def test_remove_duplicates(self):
        """Test duplicate removal from news items."""
        duplicate_articles = [
            {
                'title': 'Sensex rises 500 points on positive global cues',
                'url': 'https://example.com/article1',
                'source': 'Source1'
            },
            {
                'title': 'Sensex rises 500 points due to positive global cues',  # Similar title
                'url': 'https://example.com/article1-duplicate',
                'source': 'Source2'
            },
            {
                'title': 'Completely different article title',
                'url': 'https://example.com/article3',
                'source': 'Source3'
            }
        ]
        
        # Call the method
        unique_articles = self.news_service._remove_duplicates(duplicate_articles)
        
        # Assertions
        self.assertEqual(len(unique_articles), 2)
        self.assertIn(duplicate_articles[0], unique_articles)
        self.assertIn(duplicate_articles[2], unique_articles)
    
    def test_titles_are_similar(self):
        """Test title similarity detection."""
        # Similar titles
        title1 = "Sensex rises 500 points on positive global cues"
        title2 = "Sensex rises 500 points due to positive global factors"
        
        # Different titles
        title3 = "Nifty declines 200 points on weak global markets"
        
        # Assertions
        self.assertTrue(self.news_service._titles_are_similar(title1, title2))
        self.assertFalse(self.news_service._titles_are_similar(title1, title3))
    
    @patch.object(NewsService, 'fetch_news_from_all_sources')
    @patch('marketbot.services.content_analyzer.ContentAnalyzer.format_news_with_insights')
    def test_get_market_news(self, mock_format, mock_fetch):
        """Test getting market news with insights."""
        # Configure mocks
        mock_fetch.return_value = self.sample_articles
        mock_format.return_value = "Formatted news with insights"
        
        # Call the method with a query
        result = self.news_service.get_market_news(query="test query", max_articles=2)
        
        # Assertions
        self.assertEqual(len(result['news_items']), 2)  # Limited to 2 articles
        self.assertEqual(result['formatted_message'], "Formatted news with insights")
        self.assertEqual(result['count'], 2)
        mock_fetch.assert_called_once_with("test query")
        mock_format.assert_called_once()
    
    @patch.object(NewsService, 'get_market_news')
    def test_get_topic_news(self, mock_get_market_news):
        """Test getting news for a specific topic."""
        # Configure mock
        mock_get_market_news.return_value = {
            "news_items": self.sample_articles,
            "formatted_message": "Topic specific news",
            "count": 3
        }
        
        # Call the method
        result = self.news_service.get_topic_news("earnings")
        
        # Assertions
        self.assertEqual(result["formatted_message"], "Topic specific news")
        mock_get_market_news.assert_called_once()
    
    @patch.object(NewsService, 'get_market_news')
    def test_get_topic_news_unknown_topic(self, mock_get_market_news):
        """Test getting news for an unknown topic."""
        # Call the method with an unknown topic
        result = self.news_service.get_topic_news("unknown_topic")
        
        # Assertions
        self.assertEqual(result["count"], 0)
        self.assertIn("No predefined search query", result["formatted_message"])
        mock_get_market_news.assert_not_called()
    
    @patch.object(NewsService, 'get_market_news')
    def test_get_technical_analysis(self, mock_get_market_news):
        """Test getting technical analysis news."""
        # Configure mock
        mock_get_market_news.return_value = {
            "news_items": self.sample_articles[:2],
            "formatted_message": "Technical analysis news",
            "count": 2
        }
        
        # Call the method
        result = self.news_service.get_technical_analysis()
        
        # Assertions
        self.assertEqual(result["formatted_message"], "Technical analysis news")
        mock_get_market_news.assert_called_once_with(
            query="Indian market technical analysis chart pattern support resistance",
            max_articles=7
        )

if __name__ == '__main__':
    unittest.main() 