"""
Unit tests for the FinancialSiteProvider class.
"""

import unittest
from unittest.mock import patch, MagicMock

from marketbot.news_providers.financial_site import FinancialSiteProvider
from marketbot.config.settings import FINANCIAL_NEWS_SOURCES

class TestFinancialSiteProvider(unittest.TestCase):
    """Test suite for the FinancialSiteProvider class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a test provider with simpler selectors for testing
        self.provider = FinancialSiteProvider(
            site_name="TestSite",
            urls=["https://example.com/finance"],
            article_selector="article",
            title_selector="h2",
            link_selector="a",
            time_selector=".published-time",
            max_articles=5
        )
        
        # HTML sample for testing
        self.sample_html = """
        <html>
          <body>
            <article>
              <h2><a href="/news/article1">Market reaches new high</a></h2>
              <span class="published-time">2023-10-15 10:30</span>
            </article>
            <article>
              <h2><a href="https://example.com/news/article2">Banking stocks rise</a></h2>
              <span class="published-time">2023-10-15 09:45</span>
            </article>
            <div class="not-article">
              <h2><a href="/news/not-article">Should be ignored</a></h2>
            </div>
          </body>
        </html>
        """
    
    @patch('requests.get')
    def test_fetch_news(self, mock_get):
        """Test fetching news articles from a financial site."""
        # Configure mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = self.sample_html
        mock_response.content = self.sample_html.encode('utf-8')
        mock_get.return_value = mock_response
        
        # Call the method
        articles = self.provider.fetch_news()
        
        # Assertions
        self.assertEqual(len(articles), 2)
        self.assertEqual(articles[0]['title'], "Market reaches new high")
        self.assertEqual(articles[0]['source'], {"name": "TestSite"})
        self.assertEqual(articles[1]['title'], "Banking stocks rise")
        
        # Check URL handling (relative vs absolute)
        self.assertEqual(articles[0]['url'], "https://example.com/news/article1")
        self.assertEqual(articles[1]['url'], "https://example.com/news/article2")
        
        mock_get.assert_called_once_with(
            "https://example.com/finance",
            headers=unittest.mock.ANY,
            timeout=unittest.mock.ANY
        )
    
    @patch('requests.get')
    def test_fetch_news_error_handling(self, mock_get):
        """Test error handling during news fetching."""
        # Configure mock for HTTP error
        mock_get.side_effect = Exception("Connection error")
        
        # Call the method
        articles = self.provider.fetch_news()
        
        # Assertions
        self.assertEqual(articles, [])
        mock_get.assert_called_once()
    
    def test_extract_title_and_link(self):
        """Test extracting title and link from article elements."""
        # Create a mock BeautifulSoup element
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(self.sample_html, "html.parser")
        articles = soup.select("article")
        
        # Test relative URL
        title, link = self.provider._extract_title_and_link(
            articles[0], 
            self.provider.title_selector, 
            self.provider.link_selector, 
            "https://example.com"
        )
        self.assertEqual(title, "Market reaches new high")
        self.assertEqual(link, "https://example.com/news/article1")
        
        # Test absolute URL
        title, link = self.provider._extract_title_and_link(
            articles[1], 
            self.provider.title_selector, 
            self.provider.link_selector, 
            "https://example.com"
        )
        self.assertEqual(title, "Banking stocks rise")
        self.assertEqual(link, "https://example.com/news/article2")
    
    def test_factory_methods(self):
        """Test the factory methods for creating pre-configured providers."""
        # MoneyControl provider
        moneycontrol = FinancialSiteProvider.moneycontrol()
        self.assertEqual(moneycontrol.site_name, "MoneyControl")
        self.assertEqual(moneycontrol.max_articles, 10)
        self.assertIn(FINANCIAL_NEWS_SOURCES["moneycontrol"]["urls"][0], moneycontrol.urls)
        
        # Financial Express provider
        financial_express = FinancialSiteProvider.financial_express()
        self.assertEqual(financial_express.site_name, "Financial Express")
        self.assertEqual(financial_express.max_articles, 10)
        self.assertIn(FINANCIAL_NEWS_SOURCES["financial_express"]["urls"][0], financial_express.urls)
        
        # Economic Times provider
        economic_times = FinancialSiteProvider.economic_times()
        self.assertEqual(economic_times.site_name, "Economic Times")
        self.assertEqual(economic_times.max_articles, 10)
        self.assertIn(FINANCIAL_NEWS_SOURCES["economic_times"]["urls"][0], economic_times.urls)
    
    @patch('requests.get')
    def test_normalize_article(self, mock_get):
        """Test article normalization."""
        # Configure mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = self.sample_html
        mock_response.content = self.sample_html.encode('utf-8')
        mock_get.return_value = mock_response
        
        # Fetch news to get normalized articles
        articles = self.provider.fetch_news()
        
        # Assertions on normalized articles
        self.assertGreater(len(articles), 0)
        self.assertIn('title', articles[0])
        self.assertIn('url', articles[0])
        self.assertIn('source', articles[0])
        self.assertIn('publishedAt', articles[0])
        self.assertIn('time', articles[0])
        
        self.assertEqual(articles[0]['source'], {"name": "TestSite"})

if __name__ == '__main__':
    unittest.main() 