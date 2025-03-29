"""
Google News provider for fetching news from Google News.
"""

import time
import logging
import requests
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

from marketbot.news_providers.base import NewsProvider
from marketbot.config.settings import REQUEST_HEADERS, NEWS_SOURCES, GOOGLE_NEWS_SEARCH_QUERIES

logger = logging.getLogger(__name__)

class GoogleNewsProvider(NewsProvider):
    """Provider for fetching news from Google News."""
    
    def __init__(self, save_debug: bool = False):
        """
        Initialize the Google News provider.
        
        Args:
            save_debug: Whether to save debug HTML files
        """
        self.save_debug = save_debug
        
    def fetch_news(self, query: str = None, country: str = None) -> List[Dict[str, Any]]:
        """
        Fetch news from Google News.
        
        Args:
            query: Search query for Google News
            country: Country code to use for default query (e.g., 'us', 'india')
            
        Returns:
            List of news articles
        """
        if not query:
            # Use country-specific default query if provided
            if country and country in GOOGLE_NEWS_SEARCH_QUERIES:
                query = GOOGLE_NEWS_SEARCH_QUERIES[country]
            else:
                # Default to global market news if no query or country provided
                query = GOOGLE_NEWS_SEARCH_QUERIES.get("global", "stock market")
            
        logger.info(f"Fetching Google News for query: {query}")
        news_items = []
        
        try:
            encoded_term = requests.utils.quote(query)
            # Set regional parameters for better results
            region_param = "US"
            lang_param = "en-US"
            if country == "india":
                region_param = "IN"
                lang_param = "en-IN"
                
            url = f"{NEWS_SOURCES['google_news']}?q={encoded_term}&hl={lang_param}&gl={region_param}&ceid={region_param}%3Aen"
            
            # Add a browser-like User-Agent to avoid 403 errors
            headers = dict(REQUEST_HEADERS)
            headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
            
            response = requests.get(url, headers=headers)
            logger.info(f"Google News response status: {response.status_code}")
            
            if response.status_code == 200:
                # Save the HTML content for debugging if enabled
                if self.save_debug:
                    debug_filename = f"debug_google_news_{query.replace(' ', '_')[:20]}.html"
                    with open(debug_filename, "w", encoding="utf-8") as f:
                        f.write(response.text)
                
                soup = BeautifulSoup(response.content, "html.parser")
                
                # Updated comprehensive list of selectors to cover more possible layouts
                # The structure of Google News can vary, so we try multiple selectors
                article_selectors = [
                    "div.NiLAwe", "div.xrnccd", "article", "div.SbNwzf", 
                    "div[jscontroller]", "div.WjL5x", "c-wiz div.lBwEZb",
                    "main article", "div.DBQmFf", "div[jsname='gKDw6b']",
                    "div.XlKvRb", "div.ftJPW", "div.IBr9hb", "div.Oc0wGc",
                    "div.vh5dYd"
                ]
                
                # Use a list comprehension with an OR pattern to find all article elements
                # matching any of the selectors
                article_blocks = []
                for selector in article_selectors:
                    article_blocks.extend(soup.select(selector))
                
                # Log the count after filters are applied
                logger.info(f"Found {len(article_blocks)} article blocks")
                
                # Process each article block
                for article in article_blocks:
                    try:
                        # Title extraction - multiple possible selectors combined
                        title_selectors = [
                            "h3 a", "h4 a", "a.VDXfz", "h3.ipQwMb a", 
                            "a[href*='articles']", "div.PsKE7e", "div.DY5T1d", 
                            "h4", "a.JtKRv", "div.vI3xob", "div.VDXfz"
                        ]
                        
                        # Try each selector until we find a title
                        title_element = None
                        for selector in title_selectors:
                            title_element = article.select_one(selector)
                            if title_element:
                                break
                                
                        if not title_element:
                            continue
                        
                        title = title_element.get_text(strip=True)
                        if not title:
                            continue
                        
                        # Extract URL from the title element or its parent
                        link_rel = ""
                        if title_element.has_attr('href'):
                            link_rel = title_element.get("href", "")
                        else:
                            # Try to find a parent with href
                            parent_links = title_element.find_parents("a")
                            if parent_links:
                                link_rel = parent_links[0].get("href", "")
                        
                        if not link_rel:
                            # Try alternative link selectors
                            link_element = article.select_one("a[href*='articles'], a[data-n-tid], a[jsname]")
                            if link_element:
                                link_rel = link_element.get("href", "")
                            else:
                                continue  # Skip if still no URL found
                        
                        # Handle different URL formats
                        if link_rel.startswith("./articles/"):
                            link = f"https://news.google.com/{link_rel[2:]}"
                        elif link_rel.startswith("/articles/"):
                            link = f"https://news.google.com{link_rel}"
                        elif link_rel.startswith(("http://", "https://")):
                            link = link_rel
                        else:
                            # For other formats, prepend the base URL
                            link = f"https://news.google.com/{link_rel}"
                        
                        # Source extraction - include more selectors
                        source_selectors = [
                            ".SVJrMe", ".wsLqz", ".vr1PYe", "[data-n-tid]", ".KbnJ8",
                            ".wEwyrc", ".IH8v7", ".UOVrGd", ".GI74Re", ".MgUUmf"
                        ]
                        
                        # Try each source selector
                        source_element = None
                        for selector in source_selectors:
                            source_element = article.select_one(selector)
                            if source_element:
                                break
                                
                        source = source_element.get_text(strip=True) if source_element else "Unknown"
                        
                        # Time extraction - try multiple selectors
                        time_selectors = [
                            "time", ".WW6dff span", ".hvbAAd", ".LfVVr", 
                            ".ZoLQ5", "div[data-znc]", ".OSrXXb"
                        ]
                        
                        time_element = None
                        for selector in time_selectors:
                            time_element = article.select_one(selector)
                            if time_element:
                                break
                                
                        published_at = time_element.get("datetime", "") if time_element and time_element.has_attr("datetime") else ""
                        time_text = time_element.get_text(strip=True) if time_element else "Recent"
                        
                        # Create article dict and normalize
                        article_data = {
                            "title": title,
                            "url": link,
                            "source": {"name": source},
                            "publishedAt": published_at,
                            "time": time_text,
                            "query": query
                        }
                        
                        news_items.append(self.normalize_article(article_data))
                    except Exception as e:
                        logger.error(f"Error parsing Google News article: {e}")
                        continue
            
            # Filter out duplicates by title
            seen_titles = set()
            filtered_news = []
            
            for item in news_items:
                if item["title"] not in seen_titles:
                    seen_titles.add(item["title"])
                    filtered_news.append(item)
            
            logger.info(f"Final filtered Google News articles: {len(filtered_news)}")
            
            # If we still don't have any articles, try an alternative approach
            if not filtered_news:
                logger.warning("No articles found with primary approach, trying alternative methods")
                # Try just finding all anchor tags that might be news headlines
                all_links = soup.select("a[href*='articles'], h3 a, h4 a")
                
                for link in all_links[:10]:  # Limit to top 10
                    title = link.get_text(strip=True)
                    href = link.get("href", "")
                    
                    if title and href and len(title) > 15:  # Likely a headline
                        # Normalize the URL
                        if href.startswith("/"):
                            href = f"https://news.google.com{href}"
                        elif not href.startswith(("http://", "https://")):
                            href = f"https://news.google.com/{href}"
                        
                        article_data = {
                            "title": title,
                            "url": href,
                            "source": {"name": "Google News"},
                            "publishedAt": "",
                            "time": "Recent",
                            "query": query
                        }
                        filtered_news.append(self.normalize_article(article_data))
                
                logger.info(f"Alternative approach found {len(filtered_news)} articles")
            
            return filtered_news
        
        except Exception as e:
            logger.error(f"Error fetching Google News for query '{query}': {e}")
            return [] 