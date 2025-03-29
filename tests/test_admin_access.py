"""
Tests for admin-only access functionality.
"""

import unittest
from unittest.mock import AsyncMock, patch, MagicMock
import sys
import os
import asyncio

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

from marketbot.utils.decorators import admin_only
from telegram import Update

class TestAdminAccess(unittest.TestCase):
    """Test suite for admin-only access functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock function to be decorated
        self.mock_func = AsyncMock()
        
        # Create decorated function
        self.decorated_func = admin_only(self.mock_func)
        
        # Mock update and context
        self.update = MagicMock(spec=Update)
        self.context = MagicMock()
        
        # Add effective_user to update mock
        self.update.effective_user = MagicMock()
        self.update.effective_user.id = 12345  # Default ID matches our test admin ID
        
        # Add message to update for reply
        self.update.message = MagicMock()
        self.update.message.reply_text = AsyncMock()
    
    @patch('marketbot.utils.decorators.ADMIN_USER_ID', 12345)  # Admin ID
    def test_admin_access_allowed(self):
        """Test that admin user can access the function."""
        # Set user ID to admin ID
        self.update.effective_user.id = 12345
        
        # Call the decorated function using asyncio.run
        asyncio.run(self._test_admin_access_allowed())
    
    async def _test_admin_access_allowed(self):
        # Call the decorated function
        await self.decorated_func(self.update, self.context)
        
        # Assert that the wrapped function was called
        self.mock_func.assert_called_once_with(self.update, self.context)
        
        # Assert that no error message was sent
        self.update.message.reply_text.assert_not_called()
    
    @patch('marketbot.utils.decorators.ADMIN_USER_ID', 12345)  # Admin ID
    def test_non_admin_access_denied(self):
        """Test that non-admin user cannot access the function."""
        # Set user ID to a non-admin ID
        self.update.effective_user.id = 67890
        
        # Call the decorated function using asyncio.run
        asyncio.run(self._test_non_admin_access_denied())
    
    async def _test_non_admin_access_denied(self):
        # Call the decorated function
        await self.decorated_func(self.update, self.context)
        
        # Assert that the wrapped function was not called
        self.mock_func.assert_not_called()
        
        # Assert that an error message was sent
        self.update.message.reply_text.assert_called_once()
        self.assertIn("restricted", self.update.message.reply_text.call_args[0][0])
    
    @patch('marketbot.utils.decorators.ADMIN_USER_ID', 0)  # Admin check disabled
    def test_admin_check_disabled(self):
        """Test that when ADMIN_USER_ID is 0, admin check is disabled."""
        # Set any user ID
        self.update.effective_user.id = 67890
        
        # Call the decorated function using asyncio.run
        asyncio.run(self._test_admin_check_disabled())
    
    async def _test_admin_check_disabled(self):
        # Call the decorated function
        await self.decorated_func(self.update, self.context)
        
        # Assert that the wrapped function was called (no restrictions)
        self.mock_func.assert_called_once_with(self.update, self.context)
        
        # Assert that no error message was sent
        self.update.message.reply_text.assert_not_called()

if __name__ == '__main__':
    unittest.main() 