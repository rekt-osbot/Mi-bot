"""
Configuration settings for the Market Intelligence Bot.
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot settings
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("Telegram bot token not found! Please set TELEGRAM_BOT_TOKEN in .env file")

# Admin settings
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "0"))  # Set your Telegram user ID in .env file
if ADMIN_USER_ID == 0:
    logger.warning("Admin user ID not set! The bot will not restrict commands to admin only.")
    logger.warning("Set ADMIN_USER_ID in .env file with your Telegram user ID")

# Time zone settings
TIME_ZONE = os.getenv("TIMEZONE", "Asia/Kolkata")
DAILY_UPDATE_TIME = os.getenv("DAILY_UPDATE_TIME", "09:00")

# API Keys (optional)
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
EVENT_REGISTRY_API_KEY = os.getenv("EVENT_REGISTRY_API_KEY", "")

# News scraping settings
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
REQUEST_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
}

# News sources
NEWS_SOURCES = {
    "google_news": "https://news.google.com/search",
    "moneycontrol": [
        "https://www.moneycontrol.com/",  # Using the home page instead which is less likely to be blocked
        "https://www.moneycontrol.com/news/business/markets/"
    ],
    "financial_express": [
        "https://www.financialexpress.com/market/",
        "https://www.financialexpress.com/market/stock-market/"
    ],
    "economic_times": [
        "https://economictimes.indiatimes.com/markets/stocks/news",
        "https://economictimes.indiatimes.com/markets/stocks"
    ]
}

# Define financial news sources for the FinancialSiteProvider
FINANCIAL_NEWS_SOURCES = {
    "moneycontrol": {
        "name": "MoneyControl",
        "urls": [
            "https://www.moneycontrol.com/",  # Main page is less likely to be blocked
            "https://www.moneycontrol.com/stocksmarketsindia/"  # Alternative URL with market news
        ],
        "article_selector": ".article-list li, .clearfix, .top-news li, .hmpage_left li, .mid-contener-1 li",
        "title_selector": "h2 a, h2.headline, h3 a, a.arial11_summ, .article a",
        "link_selector": "h2 a, h2.headline a, h3 a, a.arial11_summ, .article a",
        "time_selector": ".article_schedule span"
    },
    "financial_express": {
        "name": "Financial Express",
        "urls": [
            "https://www.financialexpress.com/market/",
            "https://www.financialexpress.com/market/stock-market/"
        ],
        "article_selector": ".articles-list article, .market-news-wrap li",
        "title_selector": "h2.title a, h2.m-news-titile a",
        "link_selector": "h2.title a, h2.m-news-titile a",
        "time_selector": ".date-time, .time-stamp"
    },
    "economic_times": {
        "name": "Economic Times",
        "urls": [
            "https://economictimes.indiatimes.com/markets/stocks/news",
            "https://economictimes.indiatimes.com/markets/stocks"
        ],
        "article_selector": ".eachStory, .story-box",
        "title_selector": "h3 a, .story-title",
        "link_selector": "h3 a, .story-title a",
        "time_selector": ".date-format, .story-date"
    },
    "yahoo_finance": {
        "name": "Yahoo Finance",
        "urls": [
            "https://finance.yahoo.com/news/",
            "https://finance.yahoo.com/topic/stock-market-news/"
        ],
        "article_selector": "li.js-stream-content, div.Ov\\(h\\), ul.My\\(0\\) li",
        "title_selector": "h3, a[data-test='mega-item-header'], h4",
        "link_selector": "a[href^='/news'], a[href^='/finance'], a[data-test='mega-item-image']",
        "time_selector": "time, span.C\\(\\#959595\\), span.Fz\\(12px\\)"
    },
    "cnbc": {
        "name": "CNBC",
        "urls": [
            "https://www.cnbc.com/world-markets/",
            "https://www.cnbc.com/markets/"
        ],
        "article_selector": ".Card-standardBreakerCard, .Card-card, .RiverPlusCard-riverPlusCard",
        "title_selector": ".Card-title, h3.Card-title, a.Card-title",
        "link_selector": "a.Card-title, a.Card-mediaContainer",
        "time_selector": ".Card-time, time"
    },
    "marketwatch": {
        "name": "MarketWatch",
        "urls": [
            "https://www.marketwatch.com/markets",
            "https://www.marketwatch.com/latest-news"
        ],
        "article_selector": ".article__content, .element--article, .card",
        "title_selector": ".article__headline, .card__headline, h3.headline",
        "link_selector": "a.link, a.headline__link",
        "time_selector": ".article__timestamp, .card__timestamp, .timestamp"
    }
}

# Search query templates
GOOGLE_NEWS_SEARCH_QUERIES = {
    "india": "India stock market OR Sensex OR Nifty",
    "us": "US stock market OR Dow Jones OR Nasdaq OR S&P 500 OR Wall Street",
    "global": "global stock market OR international finance OR world economy",
    "commodities": "gold price OR crude oil price OR commodity markets",
    "breaking": "breaking market news OR stock market latest",
    "china": "China stock market OR Shanghai OR Hang Seng",
    "earnings": "company earnings OR quarterly results OR financial performance",
    "crypto": "cryptocurrency OR bitcoin OR ethereum OR blockchain",
    "forex": "forex OR currency exchange OR dollar OR rupee",
    "ipo": "IPO OR initial public offering OR new listing",
    "mergers": "mergers OR acquisitions OR takeover"
}

# Country-specific timeframes
COUNTRY_TIMEFRAMES = {
    "us": "US trading hours",
    "india": "Indian trading hours",
    "global": "24-hour global markets"
} 