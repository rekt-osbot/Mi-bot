"""
Comprehensive test for all news providers.
This file provides a simplified way to test all news providers at once.
"""

import unittest
import sys
import os
import logging

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

from marketbot.news_providers.google_news import GoogleNewsProvider
from marketbot.news_providers.financial_site import FinancialSiteProvider

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestAllNewsProviders(unittest.TestCase):
    """Comprehensive test suite for all news providers."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Initialize all providers
        self.google_news = GoogleNewsProvider()
        self.moneycontrol = FinancialSiteProvider.moneycontrol()
        self.financial_express = FinancialSiteProvider.financial_express()
        self.economic_times = FinancialSiteProvider.economic_times()
        self.yahoo_finance = FinancialSiteProvider.yahoo_finance()
        self.cnbc = FinancialSiteProvider.cnbc()
        self.marketwatch = FinancialSiteProvider.marketwatch()
        
        # List of all providers for convenience
        self.all_providers = [
            ("Google News", self.google_news),
            ("MoneyControl", self.moneycontrol),
            ("Financial Express", self.financial_express),
            ("Economic Times", self.economic_times),
            ("Yahoo Finance", self.yahoo_finance),
            ("CNBC", self.cnbc),
            ("MarketWatch", self.marketwatch)
        ]
    
    def test_all_providers(self):
        """Test all providers in a single test, with results for each."""
        results = []
        total_providers = len(self.all_providers)
        working_providers = 0
        
        for name, provider in self.all_providers:
            try:
                logger.info(f"Testing provider: {name}")
                articles = provider.fetch_news()
                
                # Check if we got any articles
                article_count = len(articles)
                
                if article_count > 0:
                    working_providers += 1
                    status = "✅ WORKING"
                    article_sample = articles[0]['title'][:50] + "..." if len(articles[0]['title']) > 50 else articles[0]['title']
                else:
                    status = "❌ NO ARTICLES"
                    article_sample = "N/A"
                
                results.append({
                    "provider": name,
                    "status": status,
                    "articles": article_count,
                    "sample": article_sample
                })
                
                logger.info(f"{name}: {status} - {article_count} articles")
                
            except Exception as e:
                logger.error(f"Error testing {name}: {e}")
                results.append({
                    "provider": name,
                    "status": "❌ ERROR",
                    "articles": 0,
                    "sample": f"Error: {str(e)}"
                })
        
        # Print a summary table
        self._print_results_table(results)
        
        # Make sure at least 50% of providers are working
        self.assertGreaterEqual(working_providers, total_providers / 2,
                               f"Only {working_providers} out of {total_providers} providers are working")
    
    def _print_results_table(self, results):
        """Print a formatted table of results."""
        logger.info("\n" + "=" * 100)
        logger.info(f"{'PROVIDER':<20} | {'STATUS':<15} | {'ARTICLES':<10} | {'SAMPLE':<50}")
        logger.info("-" * 100)
        
        for result in results:
            logger.info(f"{result['provider']:<20} | {result['status']:<15} | {result['articles']:<10} | {result['sample']:<50}")
        
        logger.info("=" * 100)

if __name__ == '__main__':
    unittest.main() 