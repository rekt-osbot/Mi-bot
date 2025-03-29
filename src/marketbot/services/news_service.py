"""
News service for fetching and processing financial market news.
"""

import logging
from typing import List, Dict, Any, Union, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from collections import defaultdict

from marketbot.config.settings import GOOGLE_NEWS_SEARCH_QUERIES, FINANCIAL_NEWS_SOURCES
from marketbot.news_providers.google_news import GoogleNewsProvider
from marketbot.news_providers.financial_site import FinancialSiteProvider
from marketbot.services.content_analyzer import ContentAnalyzer
from marketbot.utils.text import clean_text, STOPWORDS
from marketbot.utils.telegram_formatter import format_news_articles, format_enhanced_news

logger = logging.getLogger(__name__)

class NewsService:
    """Service for managing news data collection and processing."""
    
    def __init__(self):
        self.google_news = GoogleNewsProvider()
        self.content_analyzer = ContentAnalyzer()
        self.financial_sites = {
            'moneycontrol': FinancialSiteProvider.moneycontrol(),
            'financial_express': FinancialSiteProvider.financial_express(),
            'economic_times': FinancialSiteProvider.economic_times(),
            'yahoo_finance': FinancialSiteProvider.yahoo_finance(),
            'cnbc': FinancialSiteProvider.cnbc(),
            'marketwatch': FinancialSiteProvider.marketwatch(),
        }
        
        # Define country-specific sources for better targeting
        self.country_sources = {
            'us': ['yahoo_finance', 'cnbc', 'marketwatch'],
            'india': ['moneycontrol', 'financial_express', 'economic_times'],
        }
        
        # Map topics to countries for better targeting
        self.topic_countries = {
            'us': 'us',
            'usa': 'us',
            'united states': 'us',
            'america': 'us',
            'wall street': 'us',
            'dow': 'us',
            'nasdaq': 'us',
            's&p': 'us',
            'india': 'india',
            'sensex': 'india',
            'nifty': 'india',
            'bse': 'india',
            'nse': 'india'
        }
    
    def fetch_news_from_google(self, query: str = None, country: str = None) -> List[Dict[str, Any]]:
        """
        Fetch news from Google News for a specific query.
        
        Args:
            query: Search query
            country: Country code for regional results
            
        Returns:
            List of news articles
        """
        return self.google_news.fetch_news(query=query, country=country)
    
    def fetch_news_from_financial_site(self, site_name: str) -> List[Dict[str, Any]]:
        """
        Fetch news from a financial site.
        
        Args:
            site_name: Name of the financial site
            
        Returns:
            List of news articles
        """
        if site_name in self.financial_sites:
            return self.financial_sites[site_name].fetch_news()
        return []
    
    def fetch_news_from_all_sources(self, query: str = None, country: str = None) -> List[Dict[str, Any]]:
        """
        Fetch news from all news sources.
        
        Args:
            query: Search query for Google News
            country: Country to prioritize sources from (e.g., 'us', 'india')
            
        Returns:
            List of news articles
        """
        all_news = []
        
        # Determine which sources to use based on country
        sources_to_use = []
        if country and country in self.country_sources:
            sources_to_use = self.country_sources[country]
            logger.info(f"Using {country}-specific sources: {sources_to_use}")
        else:
            # Use all sources if no country specified
            sources_to_use = list(self.financial_sites.keys())
        
        # First fetch from Google News with country-specific parameters
        try:
            google_news = self.fetch_news_from_google(query=query, country=country)
            all_news.extend(google_news)
            logger.info(f"Retrieved {len(google_news)} articles from Google News for {country or 'global'}")
        except Exception as e:
            logger.error(f"Error fetching from Google News: {e}")
        
        # Fetch from country-specific financial sites
        for site_name in sources_to_use:
            try:
                logger.info(f"Fetching news from {site_name}...")
                site_news = self.fetch_news_from_financial_site(site_name)
                all_news.extend(site_news)
                logger.info(f"Retrieved {len(site_news)} articles from {site_name}")
                
                # Add short delay between requests to avoid rate limiting
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error fetching from {site_name}: {e}")
        
        # Sort by time (most recent first) if available
        all_news.sort(key=lambda x: x.get("publishedAt", ""), reverse=True)
        
        return all_news
    
    def filter_articles_by_query(self, articles: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """
        Filter articles by query terms.
        
        Args:
            articles: List of articles to filter
            query: Query to filter by
            
        Returns:
            Filtered list of articles
        """
        if not query:
            return articles
            
        # Clean and split query into terms
        query_terms = clean_text(query).split()
        query_terms = [term for term in query_terms if term.lower() not in STOPWORDS]
        
        filtered_articles = []
        for article in articles:
            article_text = clean_text(article.get("title", "") + " " + article.get("content", ""))
            
            # Count matches for each term
            match_count = sum(1 for term in query_terms if term.lower() in article_text.lower())
            
            # If article contains at least one term, add it with score
            if match_count > 0:
                article["relevance_score"] = match_count / len(query_terms)
                filtered_articles.append(article)
        
        # Sort by relevance score
        filtered_articles.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        return filtered_articles
    
    def get_market_news(self, query: str = None, limit: int = 10, country: str = None) -> Dict[str, Any]:
        """
        Get market news from all sources with enhanced analysis.
        
        Args:
            query: Query to search for
            limit: Number of articles to return
            country: Country to get market news for
            
        Returns:
            Dictionary with news data and formatted message
        """
        # Use country-specific query if available
        if country in GOOGLE_NEWS_SEARCH_QUERIES:
            google_query = GOOGLE_NEWS_SEARCH_QUERIES[country] if not query else query
        else:
            google_query = query or "global stock markets"
            
        # Fetch articles
        articles = self.fetch_news_from_all_sources(query=google_query, country=country)
        
        # Remove duplicates by title
        seen_titles = set()
        unique_articles = []
        
        for article in articles:
            title = article.get("title", "").lower()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_articles.append(article)
        
        # Limit the number of articles for processing
        limited_articles = unique_articles[:limit]
        
        # Check if we have enough articles
        if not limited_articles:
            return {
                "articles": [],
                "count": 0,
                "analysis": {},
                "formatted_message": "No news articles found."
            }
            
        # Add summaries to articles
        try:
            for article in limited_articles:
                summary = self.content_analyzer.summarize_article(article)
                if summary:
                    article['summary'] = summary
                    
            # Generate comprehensive analysis
            analysis = self.content_analyzer.generate_comprehensive_analysis(limited_articles, query)
            
            # Format the message for Telegram using the enhanced formatter
            title = f"📰 Market News{' - ' + country.upper() if country else ''}"
            formatted_message = format_enhanced_news(
                limited_articles, 
                analysis,
                title=title
            )
        except Exception as e:
            logger.error(f"Error generating enhanced news: {e}")
            # Fallback to basic formatting
            formatted_message = format_news_articles(
                limited_articles,
                title=f"📰 Latest Market News{' - ' + country.upper() if country else ''}"
            )
            analysis = {"summary": "Market news summary unavailable."}
        
        return {
            "articles": limited_articles,
            "count": len(limited_articles),
            "analysis": analysis,
            "formatted_message": formatted_message
        }
    
    def get_topic_news(self, topic: str, limit: int = 10) -> Dict[str, Any]:
        """
        Get news for a specific topic with enhanced analysis.
        
        Args:
            topic: Topic to get news for
            limit: Number of articles to return
            
        Returns:
            Dict with topic title, articles, count and formatted message
        """
        topic_lower = topic.lower()
        country = None
        topic_title = f"📈 {topic.title()} News"
        
        # Determine if topic is country-specific
        if topic_lower in self.topic_countries:
            country = self.topic_countries[topic_lower]
            
            # Set country-specific topic title
            if country == "us":
                topic_title = "🇺🇸 US Market News"
            elif country == "india":
                topic_title = "🇮🇳 Indian Market News"
        
        # Use predefined query if available
        if topic_lower in GOOGLE_NEWS_SEARCH_QUERIES:
            query = GOOGLE_NEWS_SEARCH_QUERIES[topic_lower]
        else:
            # Create appropriate query based on topic
            query = f"{topic} stock market"
        
        # Get news articles
        articles = self.fetch_news_from_all_sources(query=query, country=country)
        
        # Filter by topic relevance
        filtered_articles = self.filter_articles_by_query(articles, topic)
        
        # Limit articles
        limited_articles = filtered_articles[:limit]
        
        # Add summaries to articles
        for article in limited_articles:
            article['summary'] = self.content_analyzer.summarize_article(article)
        
        # Generate comprehensive analysis
        analysis = self.content_analyzer.generate_comprehensive_analysis(limited_articles, topic)
        
        # Format for Telegram
        formatted_message = format_enhanced_news(
            limited_articles,
            analysis,
            title=topic_title
        )
        
        return {
            "topic": topic,
            "articles": limited_articles,
            "count": len(limited_articles),
            "analysis": analysis,
            "formatted_message": formatted_message
        }
    
    def get_technical_analysis(self, limit: int = 7) -> Dict[str, Any]:
        """
        Get news focused on technical analysis.
        
        Args:
            limit: Number of articles to return
            
        Returns:
            Dictionary with news data and formatted message
        """
        # Technical analysis specific query
        query = "stock market technical analysis chart pattern support resistance"
        
        # Get news articles
        articles = self.fetch_news_from_all_sources(query=query)
        
        # Filter and limit
        filtered_articles = self.filter_articles_by_query(articles, "technical analysis")
        limited_articles = filtered_articles[:limit]
        
        # Format for Telegram
        formatted_message = format_news_articles(
            limited_articles, 
            title="📊 Technical Analysis"
        )
        
        return {
            "title": "Technical Analysis",
            "articles": limited_articles,
            "count": len(limited_articles),
            "formatted_message": formatted_message
        }
        
    def get_country_news(self, country: str, limit: int = 10) -> Dict[str, Any]:
        """
        Get news specific to a country with enhanced analysis.
        
        Args:
            country: Country code ('us', 'india', etc.)
            limit: Number of articles to return
            
        Returns:
            Dict with country title, articles, count and formatted message
        """
        country_lower = country.lower()
        
        # Set country-specific title and emoji
        if country_lower == "us":
            title = "🇺🇸 US Market News"
            query = GOOGLE_NEWS_SEARCH_QUERIES.get("us", "US stock market")
        elif country_lower == "india":
            title = "🇮🇳 Indian Market News"
            query = GOOGLE_NEWS_SEARCH_QUERIES.get("india", "India stock market")
        else:
            title = f"📰 {country.title()} Market News"
            query = f"{country} stock market"
        
        # Fetch news
        return self.get_market_news(query=query, limit=limit, country=country_lower) 