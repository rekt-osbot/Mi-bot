"""
Market Intelligence Bot main application.
"""

import logging
import os
import signal
import asyncio
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters
)

from marketbot.config.settings import BOT_TOKEN, TIME_ZONE, DAILY_UPDATE_TIME
from marketbot.handlers.bot_handlers import (
    start_command, help_command, subscribe_command,
    unsubscribe_command, error_handler
)
from marketbot.handlers.news_handlers import (
    news_command, topic_news_command, technical_command
)
from marketbot.handlers.specific_news_handlers import (
    news_india_command, news_us_command, news_global_command,
    news_commodities_command, news_breaking_command
)
from marketbot.handlers.callback_handlers import button_callback
from marketbot.handlers.message_handlers import handle_message
from marketbot.services.scheduler_service import SchedulerService

logger = logging.getLogger(__name__)

# Default polling settings
DEFAULT_POLL_INTERVAL = 10.0  # 10 seconds for responsive usage
DEFAULT_TIMEOUT = 60          # 60 seconds default timeout

# Long polling settings (for resource-constrained environments)
LONG_POLL_INTERVAL = 60.0     # 60 seconds for conserving resources
LONG_TIMEOUT = 30             # 30 seconds timeout for conserving resources

async def main() -> None:
    """Initialize and start the bot."""
    # Verify token
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not provided in environment variables or .env file")
        return
    
    # Set up a custom exception handler for the event loop
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(custom_exception_handler)
    
    # Check if we should use long polling intervals (for free hosting)
    use_long_polling = os.environ.get("LONG_POLLING", "").lower() in ("true", "1", "yes")
    
    # Create the Application with appropriate polling settings
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Initialize bot data 
    application.bot_data["news_topics"] = [
        "india", "us", "global", "commodities", "breaking", "earnings",
        "crypto", "forex", "ipo", "mergers"
    ]
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # News command handlers
    application.add_handler(CommandHandler("news", news_command))
    application.add_handler(CommandHandler("topicnews", topic_news_command))
    application.add_handler(CommandHandler("technical", technical_command))
    
    # Specific news command handlers
    application.add_handler(CommandHandler("news_india", news_india_command))
    application.add_handler(CommandHandler("news_us", news_us_command))
    application.add_handler(CommandHandler("news_global", news_global_command))
    application.add_handler(CommandHandler("news_commodities", news_commodities_command))
    application.add_handler(CommandHandler("news_breaking", news_breaking_command))
    
    # Subscription handlers
    application.add_handler(CommandHandler("subscribe", subscribe_command))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe_command))
    
    # Callback query handler for inline buttons
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Message handler for natural language queries - this is now the screening handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Initialize and start the scheduler
    scheduler = SchedulerService(application, TIME_ZONE, DAILY_UPDATE_TIME)
    scheduler.start_scheduler()
    
    # Log startup message
    logger.info("Market Intelligence Bot started")
    logger.info(f"Daily updates scheduled for {DAILY_UPDATE_TIME} {TIME_ZONE}")
    
    # Determine polling settings based on configuration
    if use_long_polling:
        poll_interval = LONG_POLL_INTERVAL
        timeout = LONG_TIMEOUT
        logger.info(f"Using long polling interval ({poll_interval}s) to conserve resources")
    else:
        poll_interval = DEFAULT_POLL_INTERVAL
        timeout = DEFAULT_TIMEOUT
        logger.info(f"Using standard polling interval ({poll_interval}s) for responsive usage")
    
    try:
        # Start the Bot with appropriate polling settings
        await application.run_polling(
            allowed_updates=None,
            poll_interval=poll_interval,
            timeout=timeout,
            read_timeout=timeout,
            write_timeout=timeout,
            connect_timeout=timeout,
            pool_timeout=timeout,
            # Disabling signals to avoid set_wakeup_fd issues in non-main threads
            drop_pending_updates=True,
        )
    except Exception as e:
        logger.error(f"Error in polling: {e}")
        
def custom_exception_handler(loop, context):
    """Custom exception handler for the asyncio event loop."""
    exception = context.get("exception")
    logger.error(f"Caught exception in event loop: {context.get('message')}")
    if exception:
        logger.error(f"Exception details: {exception}")
    
if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 