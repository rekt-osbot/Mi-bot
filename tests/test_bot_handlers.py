"""
Tests for bot command handlers.
"""

import unittest
from unittest.mock import AsyncMock, patch, MagicMock
import sys
import os
import asyncio

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

from marketbot.handlers.bot_handlers import (
    start_command, help_command, subscribe_command, unsubscribe_command
)
from telegram import Update, Chat, User, InlineKeyboardMarkup

class TestBotHandlers(unittest.TestCase):
    """Test suite for bot command handlers."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock update and context
        self.update = MagicMock(spec=Update)
        self.context = MagicMock()
        
        # Add bot_data to context
        self.context.bot_data = {}
        
        # Add effective_user to update mock
        self.update.effective_user = MagicMock(spec=User)
        self.update.effective_user.id = 12345  # Admin ID
        self.update.effective_user.first_name = "Test"
        
        # Add effective_chat to update mock
        self.update.effective_chat = MagicMock(spec=Chat)
        self.update.effective_chat.id = 12345
        
        # Add message to update for reply
        self.update.message = MagicMock()
        self.update.message.reply_text = AsyncMock()
    
    @patch('marketbot.utils.decorators.ADMIN_USER_ID', 12345)  # Admin ID
    def test_start_command_admin(self):
        """Test the start command with admin user."""
        asyncio.run(self._test_start_command_admin())
    
    async def _test_start_command_admin(self):
        # Call the start command
        await start_command(self.update, self.context)
        
        # Assert that the message was sent
        self.update.message.reply_text.assert_called_once()
        
        # Check that reply includes a welcome message and keyboard
        args, kwargs = self.update.message.reply_text.call_args
        self.assertIn("Hello Test", args[0])
        self.assertIsInstance(kwargs.get('reply_markup'), InlineKeyboardMarkup)
        
        # Check that user was added to subscribed_users
        self.assertIn("subscribed_users", self.context.bot_data)
        self.assertIn(12345, self.context.bot_data["subscribed_users"])
    
    @patch('marketbot.utils.decorators.ADMIN_USER_ID', 12345)  # Admin ID
    def test_start_command_non_admin(self):
        """Test the start command with non-admin user."""
        # Set user ID to a non-admin ID
        self.update.effective_user.id = 67890
        
        asyncio.run(self._test_start_command_non_admin())
    
    async def _test_start_command_non_admin(self):
        # Call the start command
        await start_command(self.update, self.context)
        
        # Assert that an error message was sent
        self.update.message.reply_text.assert_called_once()
        args, kwargs = self.update.message.reply_text.call_args
        self.assertIn("restricted", args[0])
        
        # Check that user was not added to subscribed_users
        if "subscribed_users" in self.context.bot_data:
            self.assertNotIn(67890, self.context.bot_data["subscribed_users"])
    
    @patch('marketbot.utils.decorators.ADMIN_USER_ID', 12345)  # Admin ID
    def test_help_command_admin(self):
        """Test the help command with admin user."""
        asyncio.run(self._test_help_command_admin())
    
    async def _test_help_command_admin(self):
        # Call the help command
        await help_command(self.update, self.context)
        
        # Assert that the message was sent
        self.update.message.reply_text.assert_called_once()
        
        # Check that reply includes command list
        args, kwargs = self.update.message.reply_text.call_args
        self.assertIn("available commands", args[0])
    
    @patch('marketbot.utils.decorators.ADMIN_USER_ID', 12345)  # Admin ID
    def test_subscribe_command_admin(self):
        """Test the subscribe command with admin user."""
        asyncio.run(self._test_subscribe_command_admin())
    
    async def _test_subscribe_command_admin(self):
        # Call the subscribe command
        await subscribe_command(self.update, self.context)
        
        # Assert that the message was sent
        self.update.message.reply_text.assert_called_once()
        
        # Check that user was added to subscribed_users
        self.assertIn("subscribed_users", self.context.bot_data)
        self.assertIn(12345, self.context.bot_data["subscribed_users"])
    
    @patch('marketbot.utils.decorators.ADMIN_USER_ID', 12345)  # Admin ID
    def test_unsubscribe_command_admin(self):
        """Test the unsubscribe command with admin user."""
        # Add user to subscribed_users
        self.context.bot_data["subscribed_users"] = {12345}
        
        asyncio.run(self._test_unsubscribe_command_admin())
    
    async def _test_unsubscribe_command_admin(self):
        # Call the unsubscribe command
        await unsubscribe_command(self.update, self.context)
        
        # Assert that the message was sent
        self.update.message.reply_text.assert_called_once()
        
        # Check that user was removed from subscribed_users
        self.assertIn("subscribed_users", self.context.bot_data)
        self.assertNotIn(12345, self.context.bot_data["subscribed_users"])

if __name__ == '__main__':
    unittest.main() 