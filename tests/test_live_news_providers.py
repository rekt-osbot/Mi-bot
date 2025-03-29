"""
Live integration tests for news providers.
WARNING: These tests connect to the actual news provider websites.
"""

import unittest
import sys
import os
import logging
from typing import Dict, Any

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

from marketbot.news_providers.google_news import GoogleNewsProvider
from marketbot.news_providers.financial_site import FinancialSiteProvider

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestLiveGoogleNewsProvider(unittest.TestCase):
    """Live integration tests for Google News Provider."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.provider = GoogleNewsProvider()
    
    def test_fetch_news_with_default_query(self):
        """Test fetching news from Google News with default query."""
        articles = self.provider.fetch_news()
        
        # Check if we got any articles
        self.assertIsNotNone(articles)
        self.assertIsInstance(articles, list)
        self.assertGreater(len(articles), 0)
        
        # Check if articles have the expected fields
        for article in articles[:5]:  # Check just the first 5 articles
            self._verify_article_structure(article)
    
    def test_fetch_news_with_custom_query(self):
        """Test fetching news from Google News with a custom query."""
        articles = self.provider.fetch_news(query="stock market")
        
        # Check if we got any articles
        self.assertIsNotNone(articles)
        self.assertIsInstance(articles, list)
        self.assertGreater(len(articles), 0)
        
        # Check if articles have the expected fields
        for article in articles[:5]:  # Check just the first 5 articles
            self._verify_article_structure(article)
    
    def test_fetch_news_with_country(self):
        """Test fetching news from Google News with country parameter."""
        articles = self.provider.fetch_news(country="india")
        
        # Check if we got any articles
        self.assertIsNotNone(articles)
        self.assertIsInstance(articles, list)
        self.assertGreater(len(articles), 0)
        
        # Check if articles have the expected fields
        for article in articles[:5]:  # Check just the first 5 articles
            self._verify_article_structure(article)
    
    def _verify_article_structure(self, article: Dict[str, Any]):
        """Verify that an article has the expected structure."""
        self.assertIn('title', article)
        self.assertIn('url', article)
        self.assertIn('source', article)
        self.assertIn('name', article['source'])
        self.assertIn('publishedAt', article)
        self.assertIn('time', article)
        
        # Check that fields are not empty
        self.assertNotEqual(article['title'], '')
        self.assertNotEqual(article['url'], '')
        self.assertNotEqual(article['source']['name'], '')

class TestLiveMoneyControlProvider(unittest.TestCase):
    """Live integration tests for MoneyControl Provider."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.provider = FinancialSiteProvider.moneycontrol()
    
    def test_fetch_news(self):
        """Test fetching news from MoneyControl."""
        articles = self.provider.fetch_news()
        
        # Check if we got any articles
        self.assertIsNotNone(articles)
        self.assertIsInstance(articles, list)
        
        if len(articles) == 0:
            logger.warning("No articles returned from MoneyControl. This may indicate a problem with the provider or a change in the website structure.")
        
        # Check if articles have the expected fields
        for article in articles[:5]:  # Check just the first 5 articles
            self._verify_article_structure(article)
        
        logger.info(f"MoneyControl returned {len(articles)} articles")
    
    def _verify_article_structure(self, article: Dict[str, Any]):
        """Verify that an article has the expected structure."""
        self.assertIn('title', article)
        self.assertIn('url', article)
        self.assertIn('source', article)
        self.assertIn('name', article['source'])
        
        # Check that fields are not empty
        self.assertNotEqual(article['title'], '')
        self.assertNotEqual(article['url'], '')
        self.assertEqual(article['source']['name'], 'MoneyControl')

class TestLiveFinancialExpressProvider(unittest.TestCase):
    """Live integration tests for Financial Express Provider."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.provider = FinancialSiteProvider.financial_express()
    
    def test_fetch_news(self):
        """Test fetching news from Financial Express."""
        articles = self.provider.fetch_news()
        
        # Check if we got any articles
        self.assertIsNotNone(articles)
        self.assertIsInstance(articles, list)
        
        if len(articles) == 0:
            logger.warning("No articles returned from Financial Express. This may indicate a problem with the provider or a change in the website structure.")
        
        # Check if articles have the expected fields
        for article in articles[:5]:  # Check just the first 5 articles
            self._verify_article_structure(article)
        
        logger.info(f"Financial Express returned {len(articles)} articles")
    
    def _verify_article_structure(self, article: Dict[str, Any]):
        """Verify that an article has the expected structure."""
        self.assertIn('title', article)
        self.assertIn('url', article)
        self.assertIn('source', article)
        self.assertIn('name', article['source'])
        
        # Check that fields are not empty
        self.assertNotEqual(article['title'], '')
        self.assertNotEqual(article['url'], '')
        self.assertEqual(article['source']['name'], 'Financial Express')

class TestLiveEconomicTimesProvider(unittest.TestCase):
    """Live integration tests for Economic Times Provider."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.provider = FinancialSiteProvider.economic_times()
    
    def test_fetch_news(self):
        """Test fetching news from Economic Times."""
        articles = self.provider.fetch_news()
        
        # Check if we got any articles
        self.assertIsNotNone(articles)
        self.assertIsInstance(articles, list)
        
        if len(articles) == 0:
            logger.warning("No articles returned from Economic Times. This may indicate a problem with the provider or a change in the website structure.")
        
        # Check if articles have the expected fields
        for article in articles[:5]:  # Check just the first 5 articles
            self._verify_article_structure(article)
        
        logger.info(f"Economic Times returned {len(articles)} articles")
    
    def _verify_article_structure(self, article: Dict[str, Any]):
        """Verify that an article has the expected structure."""
        self.assertIn('title', article)
        self.assertIn('url', article)
        self.assertIn('source', article)
        self.assertIn('name', article['source'])
        
        # Check that fields are not empty
        self.assertNotEqual(article['title'], '')
        self.assertNotEqual(article['url'], '')
        self.assertEqual(article['source']['name'], 'Economic Times')

class TestLiveYahooFinanceProvider(unittest.TestCase):
    """Live integration tests for Yahoo Finance Provider."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.provider = FinancialSiteProvider.yahoo_finance()
    
    def test_fetch_news(self):
        """Test fetching news from Yahoo Finance."""
        articles = self.provider.fetch_news()
        
        # Check if we got any articles
        self.assertIsNotNone(articles)
        self.assertIsInstance(articles, list)
        
        if len(articles) == 0:
            logger.warning("No articles returned from Yahoo Finance. This may indicate a problem with the provider or a change in the website structure.")
        
        # Check if articles have the expected fields
        for article in articles[:5]:  # Check just the first 5 articles
            self._verify_article_structure(article)
        
        logger.info(f"Yahoo Finance returned {len(articles)} articles")
    
    def _verify_article_structure(self, article: Dict[str, Any]):
        """Verify that an article has the expected structure."""
        self.assertIn('title', article)
        self.assertIn('url', article)
        self.assertIn('source', article)
        self.assertIn('name', article['source'])
        
        # Check that fields are not empty
        self.assertNotEqual(article['title'], '')
        self.assertNotEqual(article['url'], '')
        self.assertEqual(article['source']['name'], 'Yahoo Finance')

class TestLiveCNBCProvider(unittest.TestCase):
    """Live integration tests for CNBC Provider."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.provider = FinancialSiteProvider.cnbc()
    
    def test_fetch_news(self):
        """Test fetching news from CNBC."""
        articles = self.provider.fetch_news()
        
        # Check if we got any articles
        self.assertIsNotNone(articles)
        self.assertIsInstance(articles, list)
        
        if len(articles) == 0:
            logger.warning("No articles returned from CNBC. This may indicate a problem with the provider or a change in the website structure.")
        
        # Check if articles have the expected fields
        for article in articles[:5]:  # Check just the first 5 articles
            self._verify_article_structure(article)
        
        logger.info(f"CNBC returned {len(articles)} articles")
    
    def _verify_article_structure(self, article: Dict[str, Any]):
        """Verify that an article has the expected structure."""
        self.assertIn('title', article)
        self.assertIn('url', article)
        self.assertIn('source', article)
        self.assertIn('name', article['source'])
        
        # Check that fields are not empty
        self.assertNotEqual(article['title'], '')
        self.assertNotEqual(article['url'], '')
        self.assertEqual(article['source']['name'], 'CNBC')

class TestLiveMarketWatchProvider(unittest.TestCase):
    """Live integration tests for MarketWatch Provider."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.provider = FinancialSiteProvider.marketwatch()
    
    def test_fetch_news(self):
        """Test fetching news from MarketWatch."""
        articles = self.provider.fetch_news()
        
        # Check if we got any articles
        self.assertIsNotNone(articles)
        self.assertIsInstance(articles, list)
        
        if len(articles) == 0:
            logger.warning("No articles returned from MarketWatch. This may indicate a problem with the provider or a change in the website structure.")
        
        # Check if articles have the expected fields
        for article in articles[:5]:  # Check just the first 5 articles
            self._verify_article_structure(article)
        
        logger.info(f"MarketWatch returned {len(articles)} articles")
    
    def _verify_article_structure(self, article: Dict[str, Any]):
        """Verify that an article has the expected structure."""
        self.assertIn('title', article)
        self.assertIn('url', article)
        self.assertIn('source', article)
        self.assertIn('name', article['source'])
        
        # Check that fields are not empty
        self.assertNotEqual(article['title'], '')
        self.assertNotEqual(article['url'], '')
        self.assertEqual(article['source']['name'], 'MarketWatch')

if __name__ == '__main__':
    unittest.main() 