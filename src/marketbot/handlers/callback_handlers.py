"""
Callback handlers for inline button interactions in the Market Intelligence Bot.
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
async def button_callback(update: Update, context: CallbackContext) -> None:
    """
    Handle inline button callbacks.
    
    Args:
        update: The update object from Telegram
        context: The context object for the callback
    """
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    chat_id = query.message.chat_id
    callback_data = query.data
    
    logger.info(f"Received callback query from {user.first_name} ({user.id}): {callback_data}")
    
    # Send typing action
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    
    try:
        if callback_data == "news_india":
            news_data = news_service.get_country_news("india")
        elif callback_data == "news_us":
            news_data = news_service.get_country_news("us")
        elif callback_data == "news_global":
            news_data = news_service.get_country_news("global")
        elif callback_data == "news_commodities":
            news_data = news_service.get_topic_news("commodities")
        elif callback_data == "news_breaking":
            news_data = news_service.get_topic_news("breaking")
        elif callback_data == "news_all":
            news_data = news_service.get_market_news()
        else:
            news_data = news_service.get_market_news()
        
        if news_data["count"] > 0:
            await context.bot.send_message(
                chat_id=chat_id,
                text=news_data["formatted_message"],
                parse_mode="Markdown"
            )
            logger.info(f"Sent {news_data['count']} news items to user {user.id} for callback: {callback_data}")
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text="Sorry, I couldn't find any relevant news at the moment. Please try another option or try again later."
            )
            logger.warning(f"No news found for user {user.id} callback: {callback_data}")
    
    except Exception as e:
        logger.error(f"Error processing callback: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="Sorry, I encountered an error while processing your request. Please try again later."
        ) 