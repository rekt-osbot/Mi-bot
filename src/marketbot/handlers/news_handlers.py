"""
Command handlers for news-related Telegram bot commands.
"""

import logging
from telegram import Update
from telegram.ext import CallbackContext

from marketbot.services.news_service import NewsService
from marketbot.utils.decorators import admin_only

logger = logging.getLogger(__name__)

# Initialize the news service
news_service = NewsService()

@admin_only
async def news_command(update: Update, context: CallbackContext) -> None:
    """
    Handle the /news command to show general market news.
    
    Args:
        update: The update object from Telegram
        context: The context object for the callback
    """
    chat_id = update.effective_chat.id
    user = update.effective_user
    logger.info(f"User {user.first_name} ({user.id}) requested market news")
    
    # Send typing action
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    
    # Process any optional query
    query = None
    if context.args and len(context.args) > 0:
        query = ' '.join(context.args)
        logger.info(f"News query provided: {query}")
    
    try:
        # Get news with the optional query
        news_data = news_service.get_market_news(query=query)
        
        if news_data["count"] > 0:
            await context.bot.send_message(
                chat_id=chat_id, 
                text=news_data["formatted_message"],
                parse_mode="Markdown"
            )
            logger.info(f"Sent {news_data['count']} news items to user {user.id}")
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text="Sorry, I couldn't find any market news at the moment. Please try again later."
            )
            logger.warning(f"No news found for user {user.id}")
    
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="Sorry, I encountered an error while fetching market news. Please try again later."
        )

@admin_only
async def topic_news_command(update: Update, context: CallbackContext) -> None:
    """
    Handle the /topicnews command to show news for a specific market topic.
    
    Args:
        update: The update object from Telegram
        context: The context object for the callback
    """
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    # Send typing action
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    
    # Check if the topic was provided
    if not context.args or len(context.args) == 0:
        topics_list = ", ".join(list(context.bot_data.get("news_topics", [])))
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Please specify a topic. Available topics: {topics_list}\n"
                 f"Example: /topicnews earnings"
        )
        return
    
    topic = context.args[0].lower()
    logger.info(f"User {user.first_name} ({user.id}) requested news for topic: {topic}")
    
    try:
        # Get news for the specified topic
        news_data = news_service.get_topic_news(topic)
        
        if news_data["count"] > 0:
            await context.bot.send_message(
                chat_id=chat_id,
                text=news_data["formatted_message"],
                parse_mode="Markdown"
            )
            logger.info(f"Sent {news_data['count']} {topic} news items to user {user.id}")
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"Sorry, I couldn't find any news for the topic '{topic}' at the moment. "
                     f"Please try again later or try a different topic."
            )
            logger.warning(f"No news found for topic {topic} for user {user.id}")
    
    except Exception as e:
        logger.error(f"Error fetching topic news: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="Sorry, I encountered an error while fetching topic news. Please try again later."
        )

@admin_only
async def technical_command(update: Update, context: CallbackContext) -> None:
    """
    Handle the /technical command to show news about technical analysis.
    
    Args:
        update: The update object from Telegram
        context: The context object for the callback
    """
    chat_id = update.effective_chat.id
    user = update.effective_user
    logger.info(f"User {user.first_name} ({user.id}) requested technical analysis news")
    
    # Send typing action
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    
    try:
        # Get technical analysis news
        news_data = news_service.get_technical_analysis()
        
        if news_data["count"] > 0:
            await context.bot.send_message(
                chat_id=chat_id,
                text=news_data["formatted_message"],
                parse_mode="Markdown"
            )
            logger.info(f"Sent {news_data['count']} technical analysis news items to user {user.id}")
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text="Sorry, I couldn't find any technical analysis news at the moment. Please try again later."
            )
            logger.warning(f"No technical analysis news found for user {user.id}")
    
    except Exception as e:
        logger.error(f"Error fetching technical analysis news: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="Sorry, I encountered an error while fetching technical analysis news. Please try again later."
        ) 