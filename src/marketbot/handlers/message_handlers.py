"""
Message handlers for text-based interactions with the Market Intelligence Bot.
"""

import logging
import re
import random
from telegram import Update
from telegram.ext import CallbackContext

from marketbot.services.news_service import NewsService
from marketbot.utils.text_processing import extract_keywords, categorize_query, is_question
from marketbot.utils.decorators import admin_only

logger = logging.getLogger(__name__)

# Initialize the news service
news_service = NewsService()

# Define casual greeting patterns (including Hinglish)
GREETING_PATTERNS = [
    r'\b(hi|hello|hey|good morning|good afternoon|good evening|howdy|sup|yo|hola)\b',
    r'^(hi|hello|hey)[\s\W]*$',  # Just "hi", "hello", etc. with optional punctuation
    # Hinglish greetings
    r'\b(namaste|namaskar|jai hind|kaise ho|kya hal hai|kya hal chal|kaise hain|kya chal raha hai)\b',
    r'\b(kidhar ho|kidhar hai|kya kar rahe ho|kya ho raha hai|ram ram|jai shree ram)\b',
]

# Define market-related keywords for determining if a message is about markets
MARKET_KEYWORDS = [
    # English market terms
    'market', 'stock', 'share', 'price', 'investor', 'trading', 'index',
    'sensex', 'nifty', 'dow', 'nasdaq', 's&p', 'djia', 'bull', 'bear',
    'rally', 'crash', 'correction', 'economy', 'economic', 'finance',
    'financial', 'investment', 'commodity', 'gold', 'silver', 'oil',
    'currency', 'forex', 'dollar', 'rupee', 'euro', 'trade', 'fed',
    'inflation', 'gdp', 'growth', 'recession', 'interest rate',
    'news', 'update', 'analysis', 'report', 'forecast',
    
    # Hindi/Hinglish market terms
    'bazaar', 'bajar', 'share bazaar', 'sebi', 'sona', 'chandi', 'rupaya', 
    'sharebazaar', 'sharemarket', 'dalal street', 'rbi', 'reserve bank',
    'paisa', 'paise', 'arthvyavastha', 'arthik', 'nivesh', 'niveshak',
    'vyapar', 'munaafa', 'ghaata', 'mehangai', 'sensex', 'nifty', 'bse', 'nse'
]

# Strong market indicators in Hinglish
HINGLISH_MARKET_PHRASES = [
    'share market', 'market kya hal', 'market me kya', 'market me aaj',
    'sensex kitna', 'nifty kitna', 'share price', 'bazaar me kya',
    'kya invest karu', 'best shares', 'invest kaise kare', 'paise kaha lagaye',
    'stocks kaunse', 'aaj ka market', 'market news batao', 'stocks ke baare',
    'market trend', 'market update', 'bazaar ka haal', 'stocks ke bare me'
]

# User message handler - this will first screen messages before applying admin_only decorator
async def handle_message(update: Update, context: CallbackContext) -> None:
    """
    Initial message handler that screens messages before passing to the admin-only handler.
    This avoids spamming the admin message for non-market messages.
    """
    # Extract message data
    message = update.message.text
    user = update.effective_user
    
    logger.info(f"Received message from {user.first_name} ({user.id}): {message}")
    
    # Check if this is a casual greeting or non-market message first
    if is_greeting(message):
        # For greetings, we'll respond to everyone to be friendly
        greeting_responses = [
            f"Namaste {user.first_name}! Market ke baare mein kya jaanna chahte ho? Use /help for available commands.",
            f"Hello {user.first_name}! Market updates ke liye kya poochna chahte ho?",
            f"Hi {user.first_name}! Aaj market ke baare mein kya jaanna hai? Try /news for latest updates."
        ]
        await update.message.reply_text(random.choice(greeting_responses))
        return
    
    # For non-market messages, we'll silently ignore to avoid spam
    if not is_market_related(message):
        logger.info(f"Ignoring non-market message: {message}")
        return
        
    # For market-related messages, use the admin-only handler
    await _admin_only_handle_market_message(update, context)

# This is the admin-only handler for market-related messages
@admin_only
async def _admin_only_handle_market_message(update: Update, context: CallbackContext) -> None:
    """
    Process market-related messages and respond with relevant market information.
    Protected by admin_only decorator.
    
    Args:
        update: The update object from Telegram
        context: The context object for the callback
    """
    # Extract message data
    message = update.message.text
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    # Message is market-related and from an authorized user, proceed with analysis
    
    # Send typing indicator
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    
    try:
        # Extract key information from the message
        keywords = extract_keywords(message)
        category = categorize_query(message)
        
        logger.info(f"Extracted keywords: {keywords}, Category: {category}")
        
        # Handle based on category
        if category == "country_specific":
            # Check for country mentions
            country = None
            if re.search(r'\b(india|indian|nifty|sensex|bharat|bharatiya|hindustani)\b', message, re.IGNORECASE):
                country = "india"
            elif re.search(r'\b(us|usa|american|dow|nasdaq|s&p|wall street|america)\b', message, re.IGNORECASE):
                country = "us"
            else:
                country = "global"
            
            # Get country-specific news with enhanced analysis
            logger.info(f"Getting news for country: {country}")
            news_data = news_service.get_country_news(country)
            
            # Add context for deeper follow-up questions
            context.user_data['last_query_context'] = {
                'type': 'country',
                'country': country,
                'query_time': update.message.date
            }
            
        elif category == "topic_specific":
            # Determine the topic
            topic = "general"
            if re.search(r'\b(gold|silver|oil|commodity|commodities|sona|chandi|tel)\b', message, re.IGNORECASE):
                topic = "commodities"
            elif re.search(r'\b(crypto|bitcoin|ethereum|blockchain|btc|eth)\b', message, re.IGNORECASE):
                topic = "crypto"
            elif re.search(r'\b(currency|forex|dollar|rupee|euro|rupaya|rupaiya|paisa)\b', message, re.IGNORECASE):
                topic = "forex"
            elif re.search(r'\b(merger|acquisition|takeover|adhigrahan)\b', message, re.IGNORECASE):
                topic = "mergers"
            elif re.search(r'\b(ipo|listing|public offering|nayi company)\b', message, re.IGNORECASE):
                topic = "ipo"
            elif re.search(r'\b(earning|profit|revenue|quarterly|financial result|munafa|kamai)\b', message, re.IGNORECASE):
                topic = "earnings"
            elif re.search(r'\b(breaking|latest|urgent|alert|abhi|turant|taza)\b', message, re.IGNORECASE):
                topic = "breaking"
            
            # Get topic-specific news with enhanced analysis
            logger.info(f"Getting news for topic: {topic}")
            news_data = news_service.get_topic_news(topic)
            
            # Add context for deeper follow-up questions
            context.user_data['last_query_context'] = {
                'type': 'topic',
                'topic': topic,
                'query_time': update.message.date
            }
            
        elif category == "technical_analysis":
            # Get technical analysis news
            logger.info("Getting technical analysis news")
            news_data = news_service.get_topic_news("technical analysis")
            
            # Add context for deeper follow-up questions
            context.user_data['last_query_context'] = {
                'type': 'technical',
                'query_time': update.message.date
            }
        else:
            # Default to general market news with the user query
            logger.info(f"Getting market news for query: {message}")
            news_data = news_service.get_market_news(query=message)
            
            # Add context for deeper follow-up questions
            context.user_data['last_query_context'] = {
                'type': 'query',
                'query': message,
                'query_time': update.message.date
            }
        
        # Send the enhanced response
        if news_data["count"] > 0:
            # If we have analysis and articles, send the formatted message
            await context.bot.send_message(
                chat_id=chat_id,
                text=news_data["formatted_message"],
                parse_mode="Markdown",
                disable_web_page_preview=True  # Better formatting without previews cluttering the message
            )
            logger.info(f"Sent enhanced market analysis with {news_data['count']} news items to user {user.id}")
        else:
            # No articles found
            no_results_responses = [
                "Is topic par abhi koi news nahi mil rahi hai. Please try a different question or use /news for the latest market updates.",
                f"Sorry, '{message}' ke baare mein koi recent updates nahi hain. Koi aur topic try karein?",
                "No recent market updates found on this topic. Try being more specific or check general market news with /news."
            ]
            await context.bot.send_message(
                chat_id=chat_id,
                text=random.choice(no_results_responses)
            )
            logger.warning(f"No news found for user {user.id} query: {message}")
    
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="Sorry, aapke message ko process karne mein error aa gaya hai. Please try again or use one of the specific commands like /news or /help."
        )
        
def is_greeting(text: str) -> bool:
    """
    Check if a message is just a casual greeting, including Hinglish greetings.
    
    Args:
        text: Message text to check
        
    Returns:
        True if the message appears to be a greeting
    """
    text_lower = text.lower()
    for pattern in GREETING_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    
    # Check for very short messages that might be greetings
    if len(text_lower.split()) <= 2 and len(text_lower) < 15:
        common_short_greetings = ['haan', 'ji', 'haanji', 'hmm', 'hm', 'ok', 'okay', 'thik', 'theek', 'yes', 'no', 'nahi']
        if text_lower in common_short_greetings:
            return True
    
    return False

def is_market_related(text: str) -> bool:
    """
    Determine if a message is related to markets and finance, including Hinglish terms.
    
    Args:
        text: Message text to check
        
    Returns:
        True if the message appears to be market-related
    """
    # Check if it's a question - more likely to be market-related if it's a question
    is_a_question = is_question(text)
    text_lower = text.lower()
    
    # Count market-related keywords
    keyword_count = sum(1 for keyword in MARKET_KEYWORDS if keyword in text_lower)
    
    # Messages with multiple market keywords are likely market-related
    if keyword_count >= 2:
        return True
        
    # Check for Hinglish market phrases
    for phrase in HINGLISH_MARKET_PHRASES:
        if phrase in text_lower:
            return True
            
    # If it's a question and has at least one market keyword, consider it market-related
    if is_a_question and keyword_count >= 1:
        return True
        
    # If message contains specific financial instrument mentions
    if re.search(r'\b(nifty|sensex|bse|nse|dow|nasdaq|s&p|ftse|dax)\b', text_lower):
        return True
        
    return False 