"""
General command handlers for the Market Intelligence Bot.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from marketbot.utils.decorators import admin_only

logger = logging.getLogger(__name__)

@admin_only
async def start_command(update: Update, context: CallbackContext) -> None:
    """
    Handle the /start command to initialize the bot interaction.
    
    Args:
        update: The update object from Telegram
        context: The context object for the callback
    """
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Add user to subscribed_users if not already done
    if "subscribed_users" not in context.bot_data:
        context.bot_data["subscribed_users"] = set()
    context.bot_data["subscribed_users"].add(chat_id)
    
    keyboard = [
        [
            InlineKeyboardButton("Indian Markets", callback_data="news_india"),
            InlineKeyboardButton("US Markets", callback_data="news_us"),
        ],
        [
            InlineKeyboardButton("Global Markets", callback_data="news_global"),
            InlineKeyboardButton("Commodities", callback_data="news_commodities"),
        ],
        [
            InlineKeyboardButton("Breaking News", callback_data="news_breaking"),
            InlineKeyboardButton("Market Insights", callback_data="news_all"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Hello {user.first_name}! I'm your Market Intelligence Assistant.\n"
        "I provide meaningful market insights and breaking news to keep you ahead of the curve.\n"
        "What would you like to know about today?",
        reply_markup=reply_markup,
    )

@admin_only
async def help_command(update: Update, context: CallbackContext) -> None:
    """
    Handle the /help command to show available commands.
    
    Args:
        update: The update object from Telegram
        context: The context object for the callback
    """
    help_text = (
        "Here are the available commands:\n\n"
        "/start - Start the bot and see main menu\n"
        "/news - Get latest market insights and analysis\n"
        "/news_india - Get Indian market insights\n"
        "/news_us - Get US market insights\n"
        "/news_global - Get global market insights\n"
        "/news_commodities - Get commodities market analysis\n"
        "/news_breaking - Get breaking market news with analysis\n"
        "/technical - Get technical analysis news and trends\n"
        "/topicnews [topic] - Get news about a specific topic\n"
        "/subscribe - Subscribe to daily market insights\n"
        "/unsubscribe - Unsubscribe from daily updates\n\n"
        "You can also just ask a question about any market in plain English. For example:\n"
        "• 'What's happening in Indian markets?'\n"
        "• 'Tell me about oil prices'\n"
        "• 'Any breaking news on US stocks?'"
    )
    await update.message.reply_text(help_text)

@admin_only
async def subscribe_command(update: Update, context: CallbackContext) -> None:
    """
    Handle the /subscribe command to add user to daily updates.
    
    Args:
        update: The update object from Telegram
        context: The context object for the callback
    """
    chat_id = update.effective_chat.id
    
    # Initialize subscribed_users if not already done
    if "subscribed_users" not in context.bot_data:
        context.bot_data["subscribed_users"] = set()
    
    # Add user to subscribed users
    context.bot_data["subscribed_users"].add(chat_id)
    
    timezone = context.bot_data.get("timezone", "Asia/Kolkata")
    daily_update_time = context.bot_data.get("daily_update_time", "09:00")
    
    await update.message.reply_text(
        f"You are now subscribed to daily market insights at {daily_update_time} {timezone}.\n"
        "You'll receive a comprehensive analysis of market trends and breaking news every morning."
    )
    
    logger.info(f"User {update.effective_user.id} subscribed to daily updates")

@admin_only
async def unsubscribe_command(update: Update, context: CallbackContext) -> None:
    """
    Handle the /unsubscribe command to remove user from daily updates.
    
    Args:
        update: The update object from Telegram
        context: The context object for the callback
    """
    chat_id = update.effective_chat.id
    
    # Initialize subscribed_users if not already done
    if "subscribed_users" not in context.bot_data:
        context.bot_data["subscribed_users"] = set()
    
    # Check if user is subscribed
    if chat_id in context.bot_data["subscribed_users"]:
        context.bot_data["subscribed_users"].remove(chat_id)
        await update.message.reply_text("You have been unsubscribed from daily updates.")
        logger.info(f"User {update.effective_user.id} unsubscribed from daily updates")
    else:
        await update.message.reply_text("You are not currently subscribed to updates.")

async def error_handler(update: object, context: CallbackContext) -> None:
    """
    Handle errors encountered during updates.
    
    Args:
        update: The update object from Telegram
        context: The context object for the callback
    """
    logger.error(f"Update {update} caused error: {context.error}")
    
    # Try to notify user if possible
    if update and hasattr(update, 'effective_chat'):
        chat_id = update.effective_chat.id
        await context.bot.send_message(
            chat_id=chat_id,
            text="Sorry, something went wrong while processing your request. Please try again later."
        ) 