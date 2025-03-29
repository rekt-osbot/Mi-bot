"""
Web utility functions for the Market Intelligence Bot.
"""

import logging
import requests
from typing import Optional, Dict, Any
from urllib.parse import urljoin, urlparse

from marketbot.config.settings import REQUEST_HEADERS

logger = logging.getLogger(__name__)


def fetch_url_with_retry(url: str, 
                         headers: Optional[Dict[str, str]] = None, 
                         max_retries: int = 3, 
                         timeout: int = 10) -> Optional[requests.Response]:
    """
    Fetch a URL with retry capability.
    
    Args:
        url: URL to fetch
        headers: HTTP headers to use (defaults to REQUEST_HEADERS)
        max_retries: Maximum number of retry attempts
        timeout: Request timeout in seconds
        
    Returns:
        Response object or None if failed
    """
    if not headers:
        headers = REQUEST_HEADERS
        
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            
            # Check if we got a valid response
            if response.status_code == 200:
                return response
            
            # Log the error and retry
            logger.warning(f"Failed to fetch {url}: HTTP {response.status_code}, retrying ({retry_count+1}/{max_retries})")
            retry_count += 1
            
        except (requests.RequestException, ConnectionError, TimeoutError) as e:
            logger.warning(f"Error fetching {url}: {e}, retrying ({retry_count+1}/{max_retries})")
            retry_count += 1
    
    logger.error(f"Failed to fetch {url} after {max_retries} attempts")
    return None


def make_absolute_url(base_url: str, relative_url: str) -> str:
    """
    Convert a relative URL to an absolute URL.
    
    Args:
        base_url: Base URL
        relative_url: Relative URL
        
    Returns:
        Absolute URL
    """
    if not relative_url:
        return base_url
        
    # If it's already an absolute URL, return it as is
    if relative_url.startswith(('http://', 'https://')):
        return relative_url
        
    # Handle protocol-relative URLs (//example.com)
    if relative_url.startswith('//'):
        parsed_base = urlparse(base_url)
        return f"{parsed_base.scheme}:{relative_url}"
        
    # Otherwise, use urljoin to handle the various relative URL formats
    return urljoin(base_url, relative_url)


def get_base_url(url: str) -> str:
    """
    Get the base URL (scheme + domain) from a full URL.
    
    Args:
        url: Full URL
        
    Returns:
        Base URL (scheme + domain)
    """
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def is_same_domain(url1: str, url2: str) -> bool:
    """
    Check if two URLs are from the same domain.
    
    Args:
        url1: First URL
        url2: Second URL
        
    Returns:
        True if from the same domain, False otherwise
    """
    parsed1 = urlparse(url1)
    parsed2 = urlparse(url2)
    
    return parsed1.netloc == parsed2.netloc


def extract_domain(url: str) -> str:
    """
    Extract domain name from a URL.
    
    Args:
        url: URL to extract domain from
        
    Returns:
        Domain name without scheme or www
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # Remove www. if present
        if domain.startswith('www.'):
            domain = domain[4:]
            
        return domain
    except Exception:
        return "" 