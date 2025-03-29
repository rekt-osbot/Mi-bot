"""
Date and time utility functions for the Market Intelligence Bot.
"""

import re
import pytz
import datetime
from typing import Optional, Tuple

from marketbot.config.settings import TIME_ZONE


def get_current_datetime(timezone_str: Optional[str] = None) -> datetime.datetime:
    """
    Get the current datetime in the specified timezone.
    
    Args:
        timezone_str: Timezone string (defaults to TIME_ZONE from settings)
        
    Returns:
        Current datetime in the specified timezone
    """
    timezone = pytz.timezone(timezone_str or TIME_ZONE)
    return datetime.datetime.now(timezone)


def format_datetime(dt: datetime.datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a datetime object to a string.
    
    Args:
        dt: Datetime object
        format_str: Format string
        
    Returns:
        Formatted datetime string
    """
    return dt.strftime(format_str)


def parse_datetime(dt_str: str, 
                  format_str: str = "%Y-%m-%d %H:%M:%S", 
                  timezone_str: Optional[str] = None) -> Optional[datetime.datetime]:
    """
    Parse a datetime string to a datetime object.
    
    Args:
        dt_str: Datetime string
        format_str: Format string
        timezone_str: Timezone string (defaults to TIME_ZONE from settings)
        
    Returns:
        Datetime object or None if parsing fails
    """
    try:
        dt = datetime.datetime.strptime(dt_str, format_str)
        
        # Set timezone if specified
        if timezone_str or TIME_ZONE:
            timezone = pytz.timezone(timezone_str or TIME_ZONE)
            dt = timezone.localize(dt)
            
        return dt
    except ValueError:
        return None


def parse_relative_time(time_text: str) -> Optional[datetime.datetime]:
    """
    Parse relative time strings like "2 hours ago", "yesterday", etc.
    
    Args:
        time_text: Relative time text
        
    Returns:
        Datetime object or None if parsing fails
    """
    now = get_current_datetime()
    time_text = time_text.lower().strip()
    
    # Handle "just now" or "now"
    if time_text in ["just now", "now"]:
        return now
    
    # Handle "today" or "yesterday"
    if time_text == "today":
        return datetime.datetime.combine(now.date(), datetime.time.min).replace(tzinfo=now.tzinfo)
    elif time_text == "yesterday":
        return (datetime.datetime.combine(now.date(), datetime.time.min) - 
                datetime.timedelta(days=1)).replace(tzinfo=now.tzinfo)
    
    # Handle "X minutes/hours/days/weeks/months ago"
    patterns = [
        (r'(\d+)\s+minute(?:s)?\s+ago', lambda x: datetime.timedelta(minutes=int(x))),
        (r'(\d+)\s+hour(?:s)?\s+ago', lambda x: datetime.timedelta(hours=int(x))),
        (r'(\d+)\s+day(?:s)?\s+ago', lambda x: datetime.timedelta(days=int(x))),
        (r'(\d+)\s+week(?:s)?\s+ago', lambda x: datetime.timedelta(weeks=int(x))),
        (r'(\d+)\s+month(?:s)?\s+ago', lambda x: datetime.timedelta(days=int(x)*30))  # Approximate
    ]
    
    for pattern, delta_fn in patterns:
        match = re.match(pattern, time_text)
        if match:
            value = match.group(1)
            delta = delta_fn(value)
            return now - delta
    
    return None


def is_today(dt: datetime.datetime) -> bool:
    """
    Check if a datetime is today.
    
    Args:
        dt: Datetime to check
        
    Returns:
        True if datetime is today, False otherwise
    """
    now = get_current_datetime()
    return dt.date() == now.date()


def is_recent(dt: datetime.datetime, hours: int = 24) -> bool:
    """
    Check if a datetime is within the last specified hours.
    
    Args:
        dt: Datetime to check
        hours: Number of hours to consider recent
        
    Returns:
        True if datetime is recent, False otherwise
    """
    now = get_current_datetime()
    delta = now - dt
    return delta.total_seconds() <= hours * 3600


def format_time_ago(dt: datetime.datetime) -> str:
    """
    Format a datetime as a human-readable time ago string (e.g., "2 hours ago").
    
    Args:
        dt: Datetime to format
        
    Returns:
        Human-readable time ago string
    """
    now = get_current_datetime()
    delta = now - dt
    
    seconds = delta.total_seconds()
    
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:
        days = int(seconds // 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif seconds < 2592000:
        weeks = int(seconds // 604800)
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    else:
        return dt.strftime("%Y-%m-%d") 