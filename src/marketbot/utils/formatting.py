"""
Message formatting utilities for the Market Intelligence Bot.

This module provides functions to format messages for Telegram, including
support for Markdown and HTML formatting.
"""

from typing import List, Dict, Any, Optional
import re
import html


def escape_markdown(text: str) -> str:
    """
    Escape Markdown special characters.
    
    Args:
        text: Text to escape
        
    Returns:
        Escaped text suitable for Markdown v2 format
    """
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)


def escape_html(text: str) -> str:
    """
    Escape HTML special characters.
    
    Args:
        text: Text to escape
        
    Returns:
        Escaped text suitable for HTML format
    """
    return html.escape(text)


def format_news_article_markdown(article: Dict[str, Any]) -> str:
    """
    Format a news article for Telegram using Markdown v2.
    
    Args:
        article: News article dictionary
        
    Returns:
        Formatted article text in Markdown v2 format
    """
    title = escape_markdown(article.get('title', 'No title'))
    source = escape_markdown(article.get('source', 'Unknown source'))
    published_at = escape_markdown(article.get('time', ''))
    url = article.get('url', '')
    
    # Format the message
    message = f"*{title}*\n"
    message += f"Source: {source}\n"
    if published_at:
        message += f"Published: {published_at}\n"
    if url:
        message += f"[Read more]({url})\n"
    
    return message


def format_news_article_html(article: Dict[str, Any]) -> str:
    """
    Format a news article for Telegram using HTML.
    
    Args:
        article: News article dictionary
        
    Returns:
        Formatted article text in HTML format
    """
    title = escape_html(article.get('title', 'No title'))
    source = escape_html(article.get('source', 'Unknown source'))
    published_at = escape_html(article.get('time', ''))
    url = article.get('url', '')
    
    # Format the message
    message = f"<b>{title}</b>\n"
    message += f"Source: {source}\n"
    if published_at:
        message += f"Published: {published_at}\n"
    if url:
        message += f'<a href="{url}">Read more</a>\n'
    
    return message


def format_news_digest_markdown(articles: List[Dict[str, Any]], 
                              max_articles: int = 5, 
                              header: Optional[str] = None) -> str:
    """
    Format a digest of news articles using Markdown v2.
    
    Args:
        articles: List of news article dictionaries
        max_articles: Maximum number of articles to include
        header: Optional header text
        
    Returns:
        Formatted digest in Markdown v2 format
    """
    if not articles:
        return "No news articles available."
    
    articles = articles[:max_articles]  # Limit the number of articles
    
    digest = ""
    if header:
        digest = f"*{escape_markdown(header)}*\n\n"
    
    for i, article in enumerate(articles, 1):
        title = escape_markdown(article.get('title', 'No title'))
        source = escape_markdown(article.get('source', 'Unknown source'))
        url = article.get('url', '')
        
        digest += f"{i}\\. [{title}]({url})\n"
        digest += f"   Source: {source}\n\n"
    
    return digest


def format_news_digest_html(articles: List[Dict[str, Any]], 
                          max_articles: int = 5, 
                          header: Optional[str] = None) -> str:
    """
    Format a digest of news articles using HTML.
    
    Args:
        articles: List of news article dictionaries
        max_articles: Maximum number of articles to include
        header: Optional header text
        
    Returns:
        Formatted digest in HTML format
    """
    if not articles:
        return "No news articles available."
    
    articles = articles[:max_articles]  # Limit the number of articles
    
    digest = ""
    if header:
        digest = f"<b>{escape_html(header)}</b>\n\n"
    
    for i, article in enumerate(articles, 1):
        title = escape_html(article.get('title', 'No title'))
        source = escape_html(article.get('source', 'Unknown source'))
        url = article.get('url', '')
        
        digest += f"{i}. <a href=\"{url}\">{title}</a>\n"
        digest += f"   Source: {source}\n\n"
    
    return digest


def format_error_message(error_text: str) -> str:
    """
    Format an error message.
    
    Args:
        error_text: Error text
        
    Returns:
        Formatted error message
    """
    return f"⚠️ Error: {error_text}"


def truncate_message(message: str, max_length: int = 4096) -> str:
    """
    Truncate a message to the maximum length allowed by Telegram.
    
    Args:
        message: Message to truncate
        max_length: Maximum length
        
    Returns:
        Truncated message
    """
    if len(message) <= max_length:
        return message
    
    # Try to truncate at a newline to avoid breaking in the middle of a line
    truncate_point = message[:max_length-3].rfind('\n')
    if truncate_point < max_length - 200:  # If newline is too far back, just truncate at max_length
        truncate_point = max_length - 3
    
    return message[:truncate_point] + "..." 