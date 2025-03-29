"""
Utility functions for formatting messages for Telegram.
"""

from typing import List, Dict, Any, Optional

def format_news_message(title: str, articles: List[Dict[str, Any]], 
                        insights: str = None, time: str = None) -> str:
    """
    Format news articles into a structured Telegram message.
    
    Args:
        title: Title of the message
        articles: List of article dictionaries
        insights: Optional insights about the articles
        time: Optional timestamp for the message
        
    Returns:
        Formatted message string for Telegram
    """
    if not articles:
        return f"{title}\n\nNo news articles available at this time."
    
    # Start with the title
    message = f"{title}\n\n"
    
    # Add timestamp if provided
    if time:
        message += f"_Updated: {time}_\n\n"
    
    # Add insights if provided
    if insights:
        message += f"*MARKET INSIGHTS:*\n{insights}\n\n"
    
    # Add articles
    message += "*LATEST NEWS:*\n\n"
    
    for i, article in enumerate(articles, 1):
        title = article.get('title', 'No title')
        url = article.get('url', '')
        source = article.get('source', {}).get('name', 'Unknown')
        time_text = article.get('time', '')
        
        message += f"{i}. [{title}]({url})"
        
        # Add source and time if available
        source_time = []
        if source:
            source_time.append(source)
        if time_text:
            source_time.append(time_text)
            
        if source_time:
            message += f" - {' | '.join(source_time)}"
            
        message += "\n\n"
    
    return message

def format_news_articles(articles: List[Dict[str, Any]], title: str = "Latest News", 
                         max_articles: int = 10, include_summary: bool = False) -> str:
    """
    Format news articles for Telegram with a cleaner, more modern style.
    
    Args:
        articles: List of article dictionaries
        title: Title for the news section
        max_articles: Maximum number of articles to include
        include_summary: Whether to include a summary
        
    Returns:
        Formatted message string for Telegram
    """
    if not articles:
        return f"{title}\n\nNo news articles available at this time."
    
    # Start with the title
    message = f"*{title}*\n\n"
    
    # Add summary if requested
    if include_summary:
        message += f"*{len(articles)} articles found*\n\n"
    
    # Add articles (limit to max_articles)
    articles_to_show = articles[:max_articles]
    
    for i, article in enumerate(articles_to_show, 1):
        # Extract article information
        article_title = article.get('title', 'No title')
        article_url = article.get('url', '')
        
        # Get source name
        source = article.get('source', {})
        if isinstance(source, dict):
            source_name = source.get('name', 'Unknown')
        else:
            source_name = str(source) if source else 'Unknown'
            
        # Get publication time or date
        time_info = article.get('publishedAt', article.get('time', ''))
        
        # Format the article line
        if article_url:
            message += f"*{i}.* [{article_title}]({article_url})"
        else:
            message += f"*{i}.* {article_title}"
        
        # Add source and time information
        source_time = []
        if source_name and source_name != "Unknown":
            source_time.append(f"_{source_name}_")
        if time_info:
            source_time.append(f"{time_info}")
            
        if source_time:
            message += f"\n   {' | '.join(source_time)}"
            
        # Add a separator between articles
        message += "\n\n"
    
    # If there are more articles than shown, add a note
    if len(articles) > max_articles:
        message += f"_...and {len(articles) - max_articles} more articles_"
    
    # Ensure the message doesn't exceed Telegram's limits
    return truncate_message(message)

def format_article_list(articles: List[Dict[str, Any]], max_articles: int = 5) -> str:
    """
    Format a simple list of articles for Telegram.
    
    Args:
        articles: List of article dictionaries
        max_articles: Maximum number of articles to include
        
    Returns:
        Formatted article list string
    """
    if not articles:
        return "No articles available."
        
    message = ""
    
    for i, article in enumerate(articles[:max_articles], 1):
        title = article.get('title', 'No title')
        url = article.get('url', '')
        source = article.get('source', {}).get('name', 'Unknown')
        
        if url:
            message += f"{i}. [{title}]({url})"
        else:
            message += f"{i}. {title}"
            
        if source:
            message += f" - {source}"
            
        message += "\n\n"
    
    return message

def format_error_message(error: str) -> str:
    """
    Format an error message for Telegram.
    
    Args:
        error: Error message
        
    Returns:
        Formatted error message string
    """
    return f"❌ *Error*\n\n{error}"

def format_success_message(message: str) -> str:
    """
    Format a success message for Telegram.
    
    Args:
        message: Success message
        
    Returns:
        Formatted success message string
    """
    return f"✅ *Success*\n\n{message}"

def truncate_message(message: str, max_length: int = 4000) -> str:
    """
    Truncate a message to fit within Telegram's message length limits.
    
    Args:
        message: Message to truncate
        max_length: Maximum length of the message
        
    Returns:
        Truncated message string
    """
    if len(message) <= max_length:
        return message
    
    # Try to find a good break point (preferably end of paragraph)
    break_point = message[:max_length-4].rfind('\n\n')
    
    if break_point == -1 or break_point < max_length / 2:
        # If no good paragraph break, try to find end of sentence
        break_point = message[:max_length-4].rfind('. ')
        if break_point != -1:
            break_point += 1  # Include the period
    
    if break_point == -1 or break_point < max_length / 2:
        # If no good sentence break, just cut at max length
        break_point = max_length - 4
    
    return message[:break_point] + "..."

def format_enhanced_news(articles: List[Dict[str, Any]], analysis: Dict[str, Any], 
                         title: str = "📊 Market Analysis", max_articles: int = 7) -> str:
    """
    Format news articles with enhanced summaries and insights for Telegram.
    
    Args:
        articles: List of article dictionaries
        analysis: Analysis data from ContentAnalyzer
        title: Title for the message
        max_articles: Maximum number of articles to include
        
    Returns:
        Formatted message string for Telegram
    """
    if not articles:
        return f"*{title}*\n\nNo news articles available at this time."
    
    # Start with the title
    message = f"*{title}*\n\n"
    
    # Add summary
    if analysis.get("summary"):
        message += f"{analysis['summary']}\n\n"
    
    # Add key insights
    if analysis.get("insights"):
        message += f"*Key Market Insights:*\n{analysis['insights']}\n\n"
    
    # Add key points if available
    if analysis.get("key_points"):
        message += "*Top Headlines:*\n"
        for i, point in enumerate(analysis["key_points"], 1):
            message += f"• {point}\n"
        message += "\n"
    
    # Add trending topics if available
    if analysis.get("trending_topics"):
        message += f"*Trending Topics:* {', '.join(analysis['trending_topics'][:5])}\n\n"
    
    # Add article details with summaries
    message += "*Latest Articles:*\n\n"
    
    for i, article in enumerate(articles[:max_articles], 1):
        # Extract article information
        article_title = article.get('title', 'No title')
        article_url = article.get('url', '')
        
        # Get source name
        source = article.get('source', {})
        if isinstance(source, dict):
            source_name = source.get('name', 'Unknown')
        else:
            source_name = str(source) if source else 'Unknown'
            
        # Get publication time or date
        time_info = article.get('publishedAt', article.get('time', ''))
        
        # Format the article line
        if article_url:
            message += f"*{i}.* [{article_title}]({article_url})"
        else:
            message += f"*{i}.* {article_title}"
        
        # Add source and time information
        source_time = []
        if source_name and source_name != "Unknown":
            source_time.append(f"_{source_name}_")
        if time_info:
            source_time.append(f"{time_info}")
            
        if source_time:
            message += f"\n   {' | '.join(source_time)}"
        
        # Add summary if available
        if article.get('summary'):
            message += f"\n   _{article['summary']}_"
            
        # Add a separator between articles
        message += "\n\n"
    
    # If there are more articles than shown, add a note
    if len(articles) > max_articles:
        message += f"_...and {len(articles) - max_articles} more articles_"
    
    # Ensure the message doesn't exceed Telegram's limits
    return truncate_message(message) 