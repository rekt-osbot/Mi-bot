"""
Utility decorators for the Market Intelligence Bot.
"""

import logging
import os
import functools
from typing import Callable, Any
from telegram import Update
from telegram.ext import CallbackContext

from marketbot.utils.text_processing import is_user_whitelisted

logger = logging.getLogger(__name__)

# Get admin ID from environment variable
ADMIN_USER_ID = os.environ.get('ADMIN_USER_ID', '')
# Set this to True to allow any user to use the bot during testing
ALLOW_ALL_USERS = False  # Disable this in production

# Keep track of users we've already warned
WARNED_USERS = set()

def admin_only(func: Callable) -> Callable:
    """
    Decorator to restrict command access to admin user only.
    For non-admin users, it will silently ignore their messages rather than sending a response.
    
    Args:
        func: The function to decorate
        
    Returns:
        Wrapped function that only executes for admin users
    """
    @functools.wraps(func)
    async def wrapped(update: Update, context: CallbackContext, *args: Any, **kwargs: Any) -> Any:
        user = update.effective_user
        user_id = str(user.id)
        
        # Check if user is admin, whitelisted, or if all users are allowed
        if ALLOW_ALL_USERS or (ADMIN_USER_ID and user_id == ADMIN_USER_ID) or is_user_whitelisted(user_id):
            return await func(update, context, *args, **kwargs)
        else:
            # Log unauthorized attempt
            logger.warning(f"Unauthorized access attempt by user {user.id}")
            
            # Only send a warning message once per user to avoid spam
            if user_id not in WARNED_USERS:
                # Add user to warned list
                WARNED_USERS.add(user_id)
                # Send message to user
                await update.message.reply_text("Sorry, this command is restricted to the bot administrator only.")
            
            # Simply return without processing further
            return None
        
    return wrapped 