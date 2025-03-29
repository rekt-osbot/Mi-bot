"""
Content analyzer for the Market Intelligence Bot.
"""

import re
import logging
from typing import List, Dict, Any, Optional

from marketbot.utils.text import clean_text

logger = logging.getLogger(__name__)

class ContentAnalyzer:
    """Analyzes news content and generates insights."""
    
    def __init__(self):
        """Initialize the content analyzer."""
        # Define market terms for different countries
        self.market_terms = {
            'global': [
                'market', 'stock', 'equity', 'trade', 'investor', 'economy',
                'bull', 'bear', 'volatile', 'rally', 'correction', 'crash',
                'investment', 'dividend', 'yield', 'bond', 'treasury', 'etf',
                'index', 'portfolio', 'fund', 'asset', 'derivative', 'hedge',
                'inflation', 'recession', 'growth', 'interest rate', 'fed', 'central bank'
            ],
            'us': [
                'dow', 'nasdaq', 's&p', 's&p 500', 'djia', 'nyse', 'wall street', 
                'russell', 'ftse', 'dax', 'federal reserve', 'fed', 'powell', 
                'treasury', 'yellen', 'sec', 'nyse', 'wall st'
            ],
            'india': [
                'sensex', 'nifty', 'bse', 'nse', 'rbi', 'sebi', 'dalal street',
                'bombay stock exchange', 'national stock exchange', 'reserve bank of india'
            ]
        }
        
        # Term mapping for proper capitalization
        self.term_mapping = {
            'dow': 'Dow Jones',
            'djia': 'Dow Jones',
            'nasdaq': 'NASDAQ',
            's&p': 'S&P 500',
            's&p 500': 'S&P 500',
            'nyse': 'NYSE',
            'russell': 'Russell',
            'sensex': 'Sensex',
            'nifty': 'Nifty',
            'bse': 'BSE',
            'nse': 'NSE',
            'rbi': 'RBI',
            'sebi': 'SEBI',
            'fed': 'Federal Reserve',
            'federal reserve': 'Federal Reserve',
            'wall street': 'Wall Street',
            'wall st': 'Wall Street',
            'dalal street': 'Dalal Street'
        }
        
        # Patterns for identifying intent in user queries
        self.intent_patterns = {
            'market_news': [
                'market', 'markets', 'news', 'latest', 'update', 'updates', 
                'what\'s happening', 'what is happening'
            ],
            'us_market': [
                'us market', 'us stock', 'us economy', 'usa', 'america', 'american', 
                'united states', 'dow', 'nasdaq', 's&p', 'wall street', 'nyse'
            ],
            'india_market': [
                'india market', 'india stock', 'india economy', 'indian', 
                'sensex', 'nifty', 'bse', 'nse', 'dalal street'
            ],
            'global_market': [
                'global market', 'global stock', 'global economy', 'world market', 
                'international market', 'european market', 'asian market'
            ],
            'tech_analysis': [
                'tech analysis', 'technical analysis', 'chart pattern', 'indicator',
                'support', 'resistance', 'trend', 'moving average', 'macd', 'rsi'
            ]
        }
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze a user query to determine intent.
        
        Args:
            query: The user query string
            
        Returns:
            Dictionary with analysis results including intent
        """
        query_lower = query.lower()
        
        # Determine intent based on keyword matches
        best_intent = "unknown"
        best_score = 0
        
        for intent, patterns in self.intent_patterns.items():
            score = sum(1 for pattern in patterns if pattern in query_lower)
            if score > best_score:
                best_score = score
                best_intent = intent
        
        # Return analysis results
        return {
            "intent": best_intent,
            "confidence": best_score / max(1, len(self.intent_patterns[best_intent])) if best_score > 0 else 0,
            "query": query
        }
    
    def generate_market_insight(self, articles: List[Dict[str, Any]], country: str = None) -> str:
        """
        Generate market insights from a list of news articles.
        
        Args:
            articles: List of news article dictionaries
            country: Specific country to focus on (e.g., 'us', 'india')
            
        Returns:
            String with market insights
        """
        if not articles:
            return "No recent market data available for insights."
        
        # Get the relevant market terms based on country
        terms_to_check = []
        
        # Always include global terms
        terms_to_check.extend(self.market_terms['global'])
        
        # Add country-specific terms if specified
        if country and country in self.market_terms:
            terms_to_check.extend(self.market_terms[country])
        else:
            # If no country specified, include all countries' terms
            for country_terms in self.market_terms.values():
                terms_to_check.extend(country_terms)
        
        # Count term occurrences across all articles
        term_counts = {}
        for article in articles:
            title = article.get('title', '').lower()
            content = article.get('content', '').lower()
            text = f"{title} {content}"
            
            for term in terms_to_check:
                if term.lower() in text:
                    term_counts[term] = term_counts.get(term, 0) + 1
        
        # Get most mentioned terms
        sorted_terms = sorted(term_counts.items(), key=lambda x: x[1], reverse=True)
        top_terms = sorted_terms[:5] if sorted_terms else []
        
        # Analyze sentiment and key movements in the market
        insights = []
        
        # Look for percentage changes and market movements
        movement_insights = self._extract_market_movements(articles, country)
        if movement_insights:
            insights.extend(movement_insights)
        
        # Look for recurring themes across articles
        themes = self._identify_themes(articles)
        if themes:
            themes_text = f"Key themes: {', '.join(themes)}."
            insights.append(themes_text)
        
        # If we have top mentioned market terms, include them
        if top_terms:
            top_term_names = []
            for term, _ in top_terms:
                # Use proper capitalization from mapping if available
                formatted_term = self.term_mapping.get(term.lower(), term.title())
                top_term_names.append(formatted_term)
                
            focus_insight = f"Market focus: {', '.join(top_term_names)}."
            insights.append(focus_insight)
        
        # If we have insights, join them into a paragraph, otherwise use default message
        if insights:
            return " ".join(insights)
        else:
            return "No significant market insights detected from recent news."
    
    def _extract_market_movements(self, articles: List[Dict[str, Any]], country: str = None) -> List[str]:
        """
        Extract market movement information from articles.
        
        Args:
            articles: List of news article dictionaries
            country: Specific country to focus on
            
        Returns:
            List of insights about market movements
        """
        insights = []
        
        # Look for percentage patterns like "+0.5%" or "-1.2%"
        percentage_pattern = r'([+-]?\d+(?:\.\d+)?)\s*%'
        
        # Country-specific index mapping
        index_mapping = {
            'us': ['dow', 'nasdaq', 's&p', 's&p 500', 'djia'],
            'india': ['sensex', 'nifty', 'bse', 'nse']
        }
        
        # Only check specific indices if country is specified
        check_indices = []
        if country and country in index_mapping:
            check_indices = index_mapping[country]
        
        # Track which indices we've already reported on
        reported_indices = set()
        
        for article in articles:
            title = article.get('title', '').lower()
            content = article.get('content', '').lower()
            text = f"{title} {content}"
            
            # Look for percentage changes
            matches = re.findall(percentage_pattern, text)
            if matches:
                # Try to associate the percentage with a market index
                for idx in self.term_mapping.keys():
                    idx_lower = idx.lower()
                    
                    # Skip if not relevant to the specified country
                    if check_indices and idx_lower not in check_indices:
                        continue
                    
                    # Skip if we already reported on this index
                    if idx_lower in reported_indices:
                        continue
                    
                    # Look for the index name near the percentage
                    if idx_lower in text:
                        idx_pos = text.find(idx_lower)
                        
                        # Get a window of text around the index mention
                        start = max(0, idx_pos - 50)
                        end = min(len(text), idx_pos + 50)
                        window = text[start:end]
                        
                        # Find percentages in this window
                        window_matches = re.findall(percentage_pattern, window)
                        if window_matches:
                            try:
                                # Take the first percentage as the change
                                change = float(window_matches[0])
                                
                                # Format the insight based on whether it's positive or negative
                                index_name = self.term_mapping.get(idx_lower, idx.title())
                                
                                if change > 0:
                                    # Look for reasons for positive movement
                                    reason = self._extract_reason(window, positive=True)
                                    if reason:
                                        insights.append(f"{index_name} gained {abs(change)}% {reason}.")
                                    else:
                                        insights.append(f"{index_name} is up {abs(change)}%.")
                                else:
                                    # Look for reasons for negative movement
                                    reason = self._extract_reason(window, positive=False)
                                    if reason:
                                        insights.append(f"{index_name} fell {abs(change)}% {reason}.")
                                    else:
                                        insights.append(f"{index_name} is down {abs(change)}%.")
                                
                                # Mark this index as reported
                                reported_indices.add(idx_lower)
                                
                                # Limit the number of movement insights
                                if len(insights) >= 3:
                                    break
                                    
                            except (ValueError, IndexError):
                                continue
                
                # If we have enough insights, stop processing
                if len(insights) >= 3:
                    break
        
        return insights
    
    def _extract_reason(self, text: str, positive: bool) -> str:
        """
        Extract reason for market movement from text.
        
        Args:
            text: The text to search in
            positive: Whether to look for positive or negative movement reasons
            
        Returns:
            Reason string or empty string if none found
        """
        # Phrases indicating reasons for movement
        reason_indicators = ['as', 'after', 'due to', 'following', 'amid', 'on', 'because of']
        
        # Additional specific phrases based on movement direction
        if positive:
            reason_indicators.extend(['boosted by', 'lifted by', 'supported by', 'driven by'])
        else:
            reason_indicators.extend(['dragged by', 'pressured by', 'weighed by', 'hit by'])
        
        for indicator in reason_indicators:
            if indicator in text:
                # Get the text after the indicator
                parts = text.split(indicator, 1)
                if len(parts) > 1:
                    reason_text = parts[1].strip()
                    
                    # Limit the length of the reason
                    words = reason_text.split()
                    if len(words) > 8:
                        reason_text = ' '.join(words[:8])
                    
                    # Clean up the reason text
                    reason_text = reason_text.rstrip('.,;:')
                    
                    return f"{indicator} {reason_text}"
        
        return ""
    
    def _identify_themes(self, articles: List[Dict[str, Any]]) -> List[str]:
        """
        Identify common themes across multiple articles.
        
        Args:
            articles: List of news article dictionaries
            
        Returns:
            List of theme strings
        """
        # Get all title words
        all_words = []
        for article in articles:
            title = clean_text(article.get('title', ''))
            words = [w.lower() for w in title.split() if len(w) > 3]
            all_words.extend(words)
        
        # Count word occurrences
        word_counts = {}
        for word in all_words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # Find words that appear multiple times
        themes = [word for word, count in word_counts.items() if count >= 2]
        
        # Keep the top 3 themes
        themes = sorted(themes, key=lambda x: word_counts[x], reverse=True)[:3]
        
        return themes
    
    def format_news_with_insights(self, news_items: List[Dict[str, Any]], country: str = None) -> str:
        """
        Format news items with insights for display.
        
        Args:
            news_items: List of news article dictionaries
            country: Specific country to focus on
            
        Returns:
            Formatted message string
        """
        if not news_items:
            return "No recent market news available."
        
        # Generate insights
        insights = self.generate_market_insight(news_items, country=country)
        
        # Format news items
        news_text = ""
        for i, item in enumerate(news_items[:5], 1):  # Limit to top 5 articles
            title = item.get('title', 'No title')
            url = item.get('url', '')
            source = item.get('source', {}).get('name', 'Unknown')
            time = item.get('time', '')
            
            news_text += f"{i}. [{title}]({url}) - {source} {time}\n\n"
        
        # Build the complete message
        if country == "us":
            header = "🇺🇸 US MARKET NEWS"
        elif country == "india":
            header = "🇮🇳 INDIAN MARKET NEWS"
        else:
            header = "📈 MARKET NEWS"
        
        message = f"{header}\n\n"
        
        if insights:
            message += f"*INSIGHTS:*\n{insights}\n\n"
        
        message += f"*LATEST NEWS:*\n{news_text}"
        
        return message 

    def summarize_article(self, article: Dict[str, Any]) -> str:
        """
        Generate a short summary of a news article.
        
        Args:
            article: The article dictionary
            
        Returns:
            A summary of the article content
        """
        # Extract article content
        title = article.get('title', '')
        content = article.get('content', '')
        
        if not content and not title:
            return "No content available for summarization."
            
        # If we only have title, return it
        if not content:
            return title
            
        # Clean content
        cleaned_content = clean_text(content)
        sentences = re.split(r'(?<=[.!?])\s+', cleaned_content)
        
        # Get first 2-3 sentences depending on length
        if len(sentences) >= 3 and sum(len(s) for s in sentences[:3]) < 200:
            summary = ' '.join(sentences[:3])
        else:
            summary = ' '.join(sentences[:2]) if len(sentences) >= 2 else sentences[0]
            
        # Ensure summary isn't too long
        if len(summary) > 280:
            summary = summary[:277] + '...'
            
        return summary
            
    def extract_key_points(self, articles: List[Dict[str, Any]], count: int = 3) -> List[str]:
        """
        Extract key points from multiple articles.
        
        Args:
            articles: List of article dictionaries
            count: Number of key points to extract
            
        Returns:
            List of key points
        """
        if not articles:
            return []
            
        # Extract potential key points from article titles
        key_points = []
        seen_points = set()
        
        for article in articles:
            title = article.get('title', '')
            if not title:
                continue
                
            # Skip duplicate points
            if title.lower() in seen_points:
                continue
                
            # Clean and add to key points
            cleaned_title = title.replace('...', '').strip()
            key_points.append(cleaned_title)
            seen_points.add(title.lower())
            
        # Return top N key points
        return key_points[:count]
    
    def generate_comprehensive_analysis(self, articles: List[Dict[str, Any]], query: str = None) -> Dict[str, Any]:
        """
        Generate a comprehensive analysis of the news articles.
        
        Args:
            articles: List of article dictionaries
            query: The original user query (if any)
            
        Returns:
            Dictionary with analysis data
        """
        if not articles:
            return {
                "summary": "No articles available for analysis.",
                "key_points": [],
                "insights": "",
                "trending_topics": []
            }
            
        # 1. Get key points from article titles
        key_points = self.extract_key_points(articles, count=3)
        
        # 2. Generate market insights
        insights = self.generate_market_insight(articles)
        
        # 3. Identify trending topics
        trending_topics = []
        term_counts = {}
        
        for article in articles:
            text = f"{article.get('title', '')} {article.get('content', '')}"
            text = clean_text(text)
            
            # Count occurrences of important terms
            for term in self.market_terms['global']:
                if term.lower() in text.lower():
                    term_counts[term] = term_counts.get(term, 0) + 1
                    
        # Get top trending topics
        sorted_terms = sorted(term_counts.items(), key=lambda x: x[1], reverse=True)
        trending_topics = [self.term_mapping.get(term, term.title()) for term, _ in sorted_terms[:5]]
        
        # 4. Generate a summary of the overall news
        if query:
            summary = f"Here's what I found about '{query}':"
        else:
            if trending_topics:
                summary = f"Current market focus is on {', '.join(trending_topics[:3])}."
            else:
                summary = "Here's the latest from the financial markets:"
        
        return {
            "summary": summary,
            "key_points": key_points,
            "insights": insights,
            "trending_topics": trending_topics
        } 