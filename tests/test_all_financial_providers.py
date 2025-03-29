"""
Integration tests for all financial news providers.
This file tests each specific financial news provider to ensure they're working as expected.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import logging

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

from marketbot.news_providers.financial_site import FinancialSiteProvider

# Disable logging for tests
logging.disable(logging.CRITICAL)

class TestMoneyControlProvider(unittest.TestCase):
    """Test suite for the MoneyControl provider."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.provider = FinancialSiteProvider.moneycontrol()
        
        # Sample HTML for MoneyControl
        self.sample_html = """
        <html>
          <body>
            <li class="article-list">
              <h2 class="headline"><a href="/news/business/markets/article1">Sensex rises 500 points</a></h2>
              <span class="article_schedule"><span>Mar 29, 2023</span></span>
            </li>
            <li class="clearfix">
              <h2><a href="/news/business/stocks/article2">Auto stocks gain 3%</a></h2>
              <span class="article_schedule"><span>Mar 29, 2023</span></span>
            </li>
          </body>
        </html>
        """
    
    @patch('requests.get')
    def test_fetch_news(self, mock_get):
        """Test fetching news from MoneyControl."""
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
        self.assertEqual(articles[0]['title'], "Sensex rises 500 points")
        self.assertEqual(articles[0]['source'], {"name": "MoneyControl"})
        self.assertEqual(articles[1]['title'], "Auto stocks gain 3%")

class TestFinancialExpressProvider(unittest.TestCase):
    """Test suite for the Financial Express provider."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.provider = FinancialSiteProvider.financial_express()
        
        # Sample HTML for Financial Express
        self.sample_html = """
        <html>
          <body>
            <article class="articles-list">
              <h2 class="title"><a href="/market/article1">Nifty crosses 22,000</a></h2>
              <span class="date-time">March 29, 2023</span>
            </article>
            <li class="market-news-wrap">
              <h2 class="m-news-titile"><a href="/market/stock-market/article2">Bank Nifty hits record high</a></h2>
              <span class="time-stamp">March 29, 2023</span>
            </li>
          </body>
        </html>
        """
    
    @patch('requests.get')
    def test_fetch_news(self, mock_get):
        """Test fetching news from Financial Express."""
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
        self.assertEqual(articles[0]['title'], "Nifty crosses 22,000")
        self.assertEqual(articles[0]['source'], {"name": "Financial Express"})
        self.assertEqual(articles[1]['title'], "Bank Nifty hits record high")

class TestEconomicTimesProvider(unittest.TestCase):
    """Test suite for the Economic Times provider."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.provider = FinancialSiteProvider.economic_times()
        
        # Sample HTML for Economic Times
        self.sample_html = """
        <html>
          <body>
            <div class="eachStory">
              <h3><a href="/markets/stocks/news/article1">IT stocks lead market gains</a></h3>
              <span class="date-format">Mar 29, 2023</span>
            </div>
            <div class="story-box">
              <div class="story-title"><a href="/markets/stocks/article2">Oil prices fall, energy stocks drop</a></div>
              <span class="story-date">Mar 29, 2023</span>
            </div>
          </body>
        </html>
        """
    
    @patch('requests.get')
    def test_fetch_news(self, mock_get):
        """Test fetching news from Economic Times."""
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
        self.assertEqual(articles[0]['title'], "IT stocks lead market gains")
        self.assertEqual(articles[0]['source'], {"name": "Economic Times"})
        self.assertEqual(articles[1]['title'], "Oil prices fall, energy stocks drop")

class TestYahooFinanceProvider(unittest.TestCase):
    """Test suite for the Yahoo Finance provider."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.provider = FinancialSiteProvider.yahoo_finance()
        
        # Sample HTML for Yahoo Finance
        self.sample_html = """
        <html>
          <body>
            <li class="js-stream-content">
              <h3><a href="/news/article1">Dow surges past 37,000</a></h3>
              <span class="C(#959595)">5 hours ago</span>
            </li>
            <div class="Ov(h)">
              <h4><a href="/finance/article2">Tech stocks rally on AI enthusiasm</a></h4>
              <time>March 29, 2023</time>
            </div>
          </body>
        </html>
        """
    
    @patch('requests.get')
    def test_fetch_news(self, mock_get):
        """Test fetching news from Yahoo Finance."""
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
        self.assertEqual(articles[0]['title'], "Dow surges past 37,000")
        self.assertEqual(articles[0]['source'], {"name": "Yahoo Finance"})
        self.assertEqual(articles[1]['title'], "Tech stocks rally on AI enthusiasm")

class TestCNBCProvider(unittest.TestCase):
    """Test suite for the CNBC provider."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.provider = FinancialSiteProvider.cnbc()
        
        # Sample HTML for CNBC
        self.sample_html = """
        <html>
          <body>
            <div class="Card-standardBreakerCard">
              <h3 class="Card-title"><a href="/markets/article1">S&P 500 hits record close</a></h3>
              <time class="Card-time">5:24 PM ET</time>
            </div>
            <div class="Card-card">
              <a class="Card-title" href="/world-markets/article2">European markets close higher</a>
              <time>12:30 PM ET</time>
            </div>
          </body>
        </html>
        """
    
    @patch('requests.get')
    def test_fetch_news(self, mock_get):
        """Test fetching news from CNBC."""
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
        self.assertEqual(articles[0]['title'], "S&P 500 hits record close")
        self.assertEqual(articles[0]['source'], {"name": "CNBC"})
        self.assertEqual(articles[1]['title'], "European markets close higher")

class TestMarketWatchProvider(unittest.TestCase):
    """Test suite for the MarketWatch provider."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.provider = FinancialSiteProvider.marketwatch()
        
        # Sample HTML for MarketWatch
        self.sample_html = """
        <html>
          <body>
            <div class="article__content">
              <h3 class="article__headline"><a class="link" href="/markets/article1">Gold prices climb to all-time high</a></h3>
              <span class="article__timestamp">March 29, 2023</span>
            </div>
            <div class="element--article">
              <h3 class="headline"><a class="headline__link" href="/latest-news/article2">Fed signals potential rate cuts</a></h3>
              <span class="timestamp">March 29, 2023</span>
            </div>
          </body>
        </html>
        """
    
    @patch('requests.get')
    def test_fetch_news(self, mock_get):
        """Test fetching news from MarketWatch."""
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
        self.assertEqual(articles[0]['title'], "Gold prices climb to all-time high")
        self.assertEqual(articles[0]['source'], {"name": "MarketWatch"})
        self.assertEqual(articles[1]['title'], "Fed signals potential rate cuts")

if __name__ == '__main__':
    unittest.main() 