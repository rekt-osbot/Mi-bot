"""
Financial site news provider for the Market Intelligence Bot.
"""

import logging
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
import re
import random
import time

from marketbot.news_providers.base import NewsProvider
from marketbot.config.settings import REQUEST_HEADERS, FINANCIAL_NEWS_SOURCES
from marketbot.utils.web_helpers import make_absolute_url, get_base_url

logger = logging.getLogger(__name__)

class FinancialSiteProvider(NewsProvider):
    """Provider for scraping news from financial sites."""
    
    def __init__(self, site_name: str, 
                 urls: List[str], 
                 article_selector: str, 
                 title_selector: str, 
                 link_selector: str,
                 time_selector: Optional[str] = None,
                 max_articles: int = 10):
        """
        Initialize the financial site provider.
        
        Args:
            site_name: Name of the financial site
            urls: URLs to scrape
            article_selector: CSS selector for article elements
            title_selector: CSS selector for article titles
            link_selector: CSS selector for article links
            time_selector: CSS selector for article timestamps (optional)
            max_articles: Maximum number of articles to return
        """
        self.site_name = site_name
        self.urls = urls
        self.article_selector = article_selector
        self.title_selector = title_selector
        self.link_selector = link_selector
        self.time_selector = time_selector
        self.max_articles = max_articles
    
    def fetch_news(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch news from the financial site.
        
        Args:
            query: Optional search query (not used for direct scraping)
            
        Returns:
            List of news articles
        """
        articles = []
        
        for url in self.urls:
            try:
                logger.info(f"Fetching news from {self.site_name}: {url}")
                
                # Use a more browser-like request to avoid being blocked
                headers = self._get_browser_headers()
                
                # Add a small delay between requests to avoid triggering rate limits
                time.sleep(random.uniform(0.5, 2.0))
                
                response = requests.get(url, headers=headers, timeout=15)
                if response.status_code != 200:
                    logger.warning(f"Failed to fetch from {url}: {response.status_code}")
                    continue
                
                soup = BeautifulSoup(response.content, "html.parser")
                base_url = get_base_url(url)
                
                # Find all article elements
                article_elements = soup.select(self.article_selector)
                logger.info(f"Found {len(article_elements)} articles at {url}")
                
                # If no articles found with the primary selector, try alternative selectors
                if not article_elements:
                    article_elements = self._try_alternative_selectors(soup, url)
                    logger.info(f"Found {len(article_elements)} articles after trying alternative selectors")
                
                for article_element in article_elements[:self.max_articles]:
                    try:
                        # Extract title and link
                        title, link = self._extract_title_and_link(
                            article_element, 
                            self.title_selector, 
                            self.link_selector,
                            base_url
                        )
                        
                        if not title or not link:
                            # Try alternative extraction
                            title, link = self._extract_title_and_link_alternative(article_element, base_url)
                            
                        if not title or not link:
                            continue
                        
                        # Extract time if available
                        time_text = ""
                        if self.time_selector:
                            time_element = article_element.select_one(self.time_selector)
                            if time_element:
                                time_text = time_element.get_text().strip()
                        
                        # Create article dictionary and normalize
                        article = {
                            "title": title,
                            "url": link,
                            "source": {"name": self.site_name},
                            "time": time_text
                        }
                        
                        # Normalize and add to the list
                        articles.append(self.normalize_article(article))
                    
                    except Exception as e:
                        logger.error(f"Error extracting article from {self.site_name}: {e}")
                        continue
            
            except Exception as e:
                logger.error(f"Error fetching from {self.site_name} ({url}): {e}")
        
        return articles
    
    def _get_browser_headers(self) -> Dict[str, str]:
        """
        Get browser-like headers to avoid being blocked by anti-scraping measures.
        
        Returns:
            Dict of HTTP headers
        """
        # Start with the default headers
        headers = dict(REQUEST_HEADERS)
        
        # Use a more specific and recent User-Agent
        headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        
        # Add common browser headers
        headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
        headers["Accept-Language"] = "en-US,en;q=0.9"
        headers["Accept-Encoding"] = "gzip, deflate, br"
        headers["Referer"] = "https://www.google.com/"
        headers["Connection"] = "keep-alive"
        headers["Upgrade-Insecure-Requests"] = "1"
        headers["Sec-Fetch-Dest"] = "document"
        headers["Sec-Fetch-Mode"] = "navigate"
        headers["Sec-Fetch-Site"] = "none"
        headers["Sec-Fetch-User"] = "?1"
        
        return headers
    
    def _try_alternative_selectors(self, soup, url) -> List:
        """
        Try alternative selectors when the main ones don't work.
        
        Args:
            soup: BeautifulSoup object of the page
            url: URL being scraped
            
        Returns:
            List of article elements
        """
        # Common patterns for article elements across financial sites
        alternative_selectors = [
            "article", "div.article", "div.story", "div.news-item", "li.story", 
            "div.card", ".newsItem", "div.item", ".article-card", ".content-card",
            ".news-card", ".news-article", ".market-news", ".financial-news",
            "div.headline", "div.story-card", "ul li.clearfix", "li.list-item"
        ]
        
        # For Yahoo Finance
        if "yahoo.com" in url:
            alternative_selectors.extend([
                "li.js-stream-content", "div.Ov\\(h\\)", "div[data-test='mrt-node-Card']",
                "div.mega-item", "div.Mt\\(30px\\)"
            ])
        
        # For MoneyControl
        elif "moneycontrol.com" in url:
            alternative_selectors.extend([
                "li.clearfix", ".article_box", ".common_newslist", 
                ".mid_section li", ".story_list li"
            ])
        
        # For Financial Express
        elif "financialexpress.com" in url:
            alternative_selectors.extend([
                ".content-grid .articles", ".main-content .article", 
                "div.posts-list div.post-item", ".ie-stories-list li"
            ])
        
        # Try each alternative selector
        for selector in alternative_selectors:
            articles = soup.select(selector)
            if articles:
                return articles
                
        # If all else fails, try to find any headlines that look like news articles
        all_headlines = soup.find_all(["h1", "h2", "h3", "h4"])
        possible_articles = []
        
        for headline in all_headlines:
            # If the headline has a link or is in a container that looks like an article
            if headline.find("a") or headline.parent.find("a"):
                possible_articles.append(headline.parent)
        
        return possible_articles
    
    def _extract_title_and_link(self, article_element, title_selector, link_selector, base_url):
        """
        Extract title and link from an article element.
        
        Args:
            article_element: HTML element containing the article
            title_selector: CSS selector for the title
            link_selector: CSS selector for the link
            base_url: Base URL for resolving relative links
            
        Returns:
            Tuple of (title, link)
        """
        title = ""
        link = ""
        
        # Extract title
        title_element = article_element.select_one(title_selector)
        if title_element:
            title = title_element.get_text().strip()
        
        # Extract link
        link_element = article_element.select_one(link_selector)
        if link_element and link_element.has_attr('href'):
            link = make_absolute_url(base_url, link_element['href'])
        
        return title, link
    
    def _extract_title_and_link_alternative(self, article_element, base_url):
        """
        Alternative method to extract title and link when standard selectors fail.
        
        Args:
            article_element: HTML element containing the article
            base_url: Base URL for resolving relative links
            
        Returns:
            Tuple of (title, link)
        """
        title = ""
        link = ""
        
        # Try to find any heading
        heading = article_element.find(["h1", "h2", "h3", "h4", "h5"])
        if heading:
            title = heading.get_text().strip()
            
            # Look for a link in the heading or its parent
            link_elem = heading.find("a") or heading.parent.find("a")
            if link_elem and link_elem.has_attr('href'):
                link = make_absolute_url(base_url, link_elem['href'])
        
        # If no heading, look for any link with text
        if not title or not link:
            for a_tag in article_element.find_all("a"):
                if a_tag.get_text().strip() and a_tag.has_attr('href'):
                    title = a_tag.get_text().strip()
                    link = make_absolute_url(base_url, a_tag['href'])
                    break
        
        return title, link
    
    @classmethod
    def moneycontrol(cls) -> "FinancialSiteProvider":
        """Factory method for MoneyControl."""
        config = FINANCIAL_NEWS_SOURCES["moneycontrol"]
        return cls(
            site_name=config["name"],
            urls=config["urls"],
            article_selector=config["article_selector"],
            title_selector=config["title_selector"],
            link_selector=config["link_selector"],
            time_selector=config["time_selector"]
        )
    
    @classmethod
    def financial_express(cls) -> "FinancialSiteProvider":
        """Factory method for Financial Express."""
        config = FINANCIAL_NEWS_SOURCES["financial_express"]
        return cls(
            site_name=config["name"],
            urls=config["urls"],
            article_selector=config["article_selector"],
            title_selector=config["title_selector"],
            link_selector=config["link_selector"],
            time_selector=config["time_selector"]
        )
    
    @classmethod
    def economic_times(cls) -> "FinancialSiteProvider":
        """Factory method for Economic Times."""
        config = FINANCIAL_NEWS_SOURCES["economic_times"]
        return cls(
            site_name=config["name"],
            urls=config["urls"],
            article_selector=config["article_selector"],
            title_selector=config["title_selector"],
            link_selector=config["link_selector"],
            time_selector=config["time_selector"]
        )
    
    @classmethod
    def yahoo_finance(cls) -> "FinancialSiteProvider":
        """Factory method for Yahoo Finance."""
        config = FINANCIAL_NEWS_SOURCES["yahoo_finance"]
        return cls(
            site_name=config["name"],
            urls=config["urls"],
            article_selector=config["article_selector"],
            title_selector=config["title_selector"],
            link_selector=config["link_selector"],
            time_selector=config["time_selector"]
        )
    
    @classmethod
    def cnbc(cls) -> "FinancialSiteProvider":
        """Factory method for CNBC."""
        config = FINANCIAL_NEWS_SOURCES["cnbc"]
        return cls(
            site_name=config["name"],
            urls=config["urls"],
            article_selector=config["article_selector"],
            title_selector=config["title_selector"],
            link_selector=config["link_selector"],
            time_selector=config["time_selector"]
        )
    
    @classmethod
    def marketwatch(cls) -> "FinancialSiteProvider":
        """Factory method for MarketWatch."""
        config = FINANCIAL_NEWS_SOURCES["marketwatch"]
        return cls(
            site_name=config["name"],
            urls=config["urls"],
            article_selector=config["article_selector"],
            title_selector=config["title_selector"],
            link_selector=config["link_selector"],
            time_selector=config["time_selector"]
        ) 