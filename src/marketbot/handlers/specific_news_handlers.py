"""
Command handlers for specific market news Telegram bot commands.
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
async def news_india_command(update: Update, context: CallbackContext) -> None:
    """
    Handle the /news_india command to show Indian market news.
    
    Args:
        update: The update object from Telegram
        context: The context object for the callback
    """
    chat_id = update.effective_chat.id
    user = update.effective_user
    logger.info(f"User {user.first_name} ({user.id}) requested Indian market news")
    
    # Send typing action
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    
    try:
        # Get news for Indian markets
        news_data = news_service.get_topic_news("india")
        
        if news_data["count"] > 0:
            await context.bot.send_message(
                chat_id=chat_id,
                text=news_data["formatted_message"],
                parse_mode="Markdown"
            )
            logger.info(f"Sent {news_data['count']} Indian market news items to user {user.id}")
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text="Sorry, I couldn't find any Indian market news at the moment. Please try again later."
            )
            logger.warning(f"No Indian market news found for user {user.id}")
    
    except Exception as e:
        logger.error(f"Error fetching Indian market news: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="Sorry, I encountered an error while fetching Indian market news. Please try again later."
        )

@admin_only
async def news_us_command(update: Update, context: CallbackContext) -> None:
    """
    Handle the /news_us command to show US market news.
    
    Args:
        update: The update object from Telegram
        context: The context object for the callback
    """
    chat_id = update.effective_chat.id
    user = update.effective_user
    logger.info(f"User {user.first_name} ({user.id}) requested US market news")
    
    # Send typing action
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    
    try:
        # Get news for US markets
        news_data = news_service.get_topic_news("us")
        
        if news_data["count"] > 0:
            await context.bot.send_message(
                chat_id=chat_id,
                text=news_data["formatted_message"],
                parse_mode="Markdown"
            )
            logger.info(f"Sent {news_data['count']} US market news items to user {user.id}")
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text="Sorry, I couldn't find any US market news at the moment. Please try again later."
            )
            logger.warning(f"No US market news found for user {user.id}")
    
    except Exception as e:
        logger.error(f"Error fetching US market news: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="Sorry, I encountered an error while fetching US market news. Please try again later."
        )

@admin_only
async def news_global_command(update: Update, context: CallbackContext) -> None:
    """
    Handle the /news_global command to show global market news.
    
    Args:
        update: The update object from Telegram
        context: The context object for the callback
    """
    chat_id = update.effective_chat.id
    user = update.effective_user
    logger.info(f"User {user.first_name} ({user.id}) requested global market news")
    
    # Send typing action
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    
    try:
        # Get news for global markets
        news_data = news_service.get_topic_news("global")
        
        if news_data["count"] > 0:
            await context.bot.send_message(
                chat_id=chat_id,
                text=news_data["formatted_message"],
                parse_mode="Markdown"
            )
            logger.info(f"Sent {news_data['count']} global market news items to user {user.id}")
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text="Sorry, I couldn't find any global market news at the moment. Please try again later."
            )
            logger.warning(f"No global market news found for user {user.id}")
    
    except Exception as e:
        logger.error(f"Error fetching global market news: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="Sorry, I encountered an error while fetching global market news. Please try again later."
        )

@admin_only
async def news_commodities_command(update: Update, context: CallbackContext) -> None:
    """
    Handle the /news_commodities command to show commodities market news.
    
    Args:
        update: The update object from Telegram
        context: The context object for the callback
    """
    chat_id = update.effective_chat.id
    user = update.effective_user
    logger.info(f"User {user.first_name} ({user.id}) requested commodities market news")
    
    # Send typing action
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    
    try:
        # Get news for commodities markets
        news_data = news_service.get_topic_news("commodities")
        
        if news_data["count"] > 0:
            await context.bot.send_message(
                chat_id=chat_id,
                text=news_data["formatted_message"],
                parse_mode="Markdown"
            )
            logger.info(f"Sent {news_data['count']} commodities market news items to user {user.id}")
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text="Sorry, I couldn't find any commodities market news at the moment. Please try again later."
            )
            logger.warning(f"No commodities market news found for user {user.id}")
    
    except Exception as e:
        logger.error(f"Error fetching commodities market news: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="Sorry, I encountered an error while fetching commodities market news. Please try again later."
        )

@admin_only
async def news_breaking_command(update: Update, context: CallbackContext) -> None:
    """
    Handle the /news_breaking command to show breaking market news.
    
    Args:
        update: The update object from Telegram
        context: The context object for the callback
    """
    chat_id = update.effective_chat.id
    user = update.effective_user
    logger.info(f"User {user.first_name} ({user.id}) requested breaking market news")
    
    # Send typing action
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    
    try:
        # Get breaking market news
        news_data = news_service.get_topic_news("breaking")
        
        if news_data["count"] > 0:
            await context.bot.send_message(
                chat_id=chat_id,
                text=news_data["formatted_message"],
                parse_mode="Markdown"
            )
            logger.info(f"Sent {news_data['count']} breaking market news items to user {user.id}")
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text="Sorry, I couldn't find any breaking market news at the moment. Please try again later."
            )
            logger.warning(f"No breaking market news found for user {user.id}")
    
    except Exception as e:
        logger.error(f"Error fetching breaking market news: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="Sorry, I encountered an error while fetching breaking market news. Please try again later."
        ) 