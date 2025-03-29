"""
Scheduler service for managing periodic updates.
"""

import logging
import threading
import asyncio
import time
import pytz
import schedule
from datetime import datetime
from typing import Dict, Set

from marketbot.services.news_service import NewsService

logger = logging.getLogger(__name__)

class SchedulerService:
    """Service for scheduling and sending daily updates."""
    
    def __init__(self, application, timezone: str = "Asia/Kolkata", daily_update_time: str = "09:00"):
        """
        Initialize the scheduler service.
        
        Args:
            application: Telegram application instance
            timezone: Timezone for scheduling updates
            daily_update_time: Time of day for daily updates (HH:MM format)
        """
        self.application = application
        self.timezone = timezone
        self.daily_update_time = daily_update_time
        self.news_service = NewsService()
        
        # Subscription data will be stored in application.bot_data
        if "subscribed_users" not in self.application.bot_data:
            self.application.bot_data["subscribed_users"] = set()
        
        # Store timezone and update time in bot_data for access by other modules
        self.application.bot_data["timezone"] = timezone
        self.application.bot_data["daily_update_time"] = daily_update_time
        
    def start_scheduler(self):
        """Start the scheduler in a separate thread."""
        scheduler_thread = threading.Thread(target=self._run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        logger.info(f"Scheduler started - daily updates at {self.daily_update_time} {self.timezone}")
        return scheduler_thread
    
    def _run_scheduler(self):
        """Run the scheduler in a loop."""
        tz = pytz.timezone(self.timezone)
        
        def trigger_daily_update():
            """Trigger the daily update function."""
            now = datetime.now(tz)
            logger.info(f"Triggering daily update at {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            asyncio.run_coroutine_threadsafe(
                self._send_daily_update(), self.application.loop
            )
        
        # Schedule daily updates
        schedule.every().day.at(self.daily_update_time).do(trigger_daily_update)
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    async def _send_daily_update(self):
        """Send daily news update to all subscribed users."""
        subscribed_users = self.application.bot_data.get("subscribed_users", set())
        
        if not subscribed_users:
            logger.info("No users subscribed to daily updates")
            return
        
        logger.info(f"Sending daily update to {len(subscribed_users)} users")
        
        try:
            # Get market news
            news_data = self.news_service.get_market_news()
            formatted_news = news_data["formatted_message"]
            
            # Add daily header
            current_date = datetime.now(pytz.timezone(self.timezone)).strftime("%A, %d %B %Y")
            message = f"📅 DAILY MARKET UPDATE - {current_date} 📅\n\n{formatted_news}"
            
            # Send to all subscribed users
            for chat_id in list(subscribed_users):
                try:
                    await self.application.bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode="Markdown"
                    )
                    logger.info(f"Daily update sent to {chat_id}")
                except Exception as e:
                    logger.error(f"Error sending daily update to {chat_id}: {e}")
                    # Remove user from subscription list if they blocked the bot or chat not found
                    if ("blocked" in str(e).lower() or 
                        "chat not found" in str(e).lower() or 
                        "deactivated" in str(e).lower()):
                        logger.info(f"Removing user {chat_id} from subscription list")
                        subscribed_users.remove(chat_id)
        
        except Exception as e:
            logger.error(f"Error preparing daily update: {e}")
            
        # Update the subscribed users in case any were removed
        self.application.bot_data["subscribed_users"] = subscribed_users 