"""
Unit tests for the ContentAnalyzer class.
"""

import unittest
from unittest.mock import patch, MagicMock

from marketbot.services.content_analyzer import ContentAnalyzer

class TestContentAnalyzer(unittest.TestCase):
    """Test suite for the ContentAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = ContentAnalyzer()
        
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
                'title': 'Nifty declines 200 points on weak global markets',
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
        
        # Sample article content
        self.sample_content = """
        Indian equity indices, Sensex and Nifty, rose 1.5% on Wednesday, 
        driven by positive global cues and strong buying in banking and IT stocks. 
        The 30-share BSE Sensex jumped 500 points to close at 60,000, 
        while the NSE Nifty climbed 150 points to finish at 18,000 level.
        Banking stocks were the top gainers, with HDFC Bank rising 3% and ICICI Bank up 2.5%.
        This rally comes amid a positive trend in global markets after US inflation data.
        """
    
    @patch('requests.get')
    def test_extract_article_content(self, mock_get):
        """Test extracting article content from a URL."""
        # Configure mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = f"""
        <html>
            <body>
                <article>
                    <p>{self.sample_content}</p>
                </article>
            </body>
        </html>
        """
        mock_get.return_value = mock_response
        
        # Call the method
        content = self.analyzer.extract_article_content("https://example.com/article1")
        
        # Assertions
        self.assertIsNotNone(content)
        self.assertIn("Indian equity indices", content)
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_extract_article_content_failure(self, mock_get):
        """Test handling of extraction failures."""
        # Configure mock for HTTP error
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        # Call the method
        content = self.analyzer.extract_article_content("https://example.com/not-found")
        
        # Assertions
        self.assertIsNone(content)
        mock_get.assert_called_once()
        
        # Test non-HTTP URL
        content = self.analyzer.extract_article_content("file:///invalid-url")
        self.assertIsNone(content)
    
    @patch.object(ContentAnalyzer, 'extract_article_content')
    def test_enrich_articles_with_content(self, mock_extract):
        """Test enriching articles with content."""
        # Configure mock
        mock_extract.return_value = self.sample_content
        
        # Call the method
        enriched = self.analyzer.enrich_articles_with_content(self.sample_articles, max_articles=2)
        
        # Assertions
        self.assertEqual(len(enriched), 2)  # Only 2 articles should be processed
        self.assertEqual(enriched[0]['content'], self.sample_content)
        self.assertEqual(mock_extract.call_count, 2)
    
    @patch.object(ContentAnalyzer, 'enrich_articles_with_content')
    def test_get_market_insights(self, mock_enrich):
        """Test getting market insights from news items."""
        # Configure mock
        mock_enrich.return_value = [
            {
                'title': 'Sensex rises 500 points on positive global cues',
                'content': self.sample_content,
                'url': 'https://example.com/article1',
                'source': 'SampleSource1'
            }
        ]
        
        # Call the method
        insights = self.analyzer.get_market_insights(self.sample_articles)
        
        # Assertions
        self.assertGreater(len(insights), 0)
        self.assertIsInstance(insights, list)
        mock_enrich.assert_called_once()
    
    def test_generate_market_insight_positive(self):
        """Test generating positive market insights."""
        text = "Sensex rises 500 points (1.2%) due to positive global cues and strong buying in banking stocks."
        
        # Call the method
        insight = self.analyzer.generate_market_insight(text, positive=True)
        
        # Assertions
        self.assertIsNotNone(insight)
        self.assertIn("Sensex", insight)
        self.assertIn("1.2%", insight)
    
    def test_generate_market_insight_negative(self):
        """Test generating negative market insights."""
        text = "Nifty falls 200 points (1.1%) amid global selloff and concerns over rising inflation."
        
        # Call the method
        insight = self.analyzer.generate_market_insight(text, positive=False)
        
        # Assertions
        self.assertIsNotNone(insight)
        self.assertIn("Nifty", insight)
        self.assertIn("1.1%", insight)
    
    def test_generate_sector_insight(self):
        """Test generating sector-specific insights."""
        text = "Banking stocks lead gains with HDFC Bank rising 3% and SBI up 2% after positive Q2 results."
        
        # Call the method
        insight = self.analyzer.generate_sector_insight(text, "banking")
        
        # Assertions
        self.assertIsNotNone(insight)
        self.assertIn("Banking", insight)
    
    def test_format_news_with_insights(self):
        """Test formatting news with insights."""
        # Call the method
        formatted = self.analyzer.format_news_with_insights(self.sample_articles)
        
        # Assertions
        self.assertIsInstance(formatted, str)
        self.assertIn("📰", formatted)  # News emoji
        self.assertIn("MARKET INTELLIGENCE REPORT", formatted)
        self.assertIn("MARKET INSIGHTS", formatted)

if __name__ == '__main__':
    unittest.main() 