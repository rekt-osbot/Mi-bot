"""
Keep-alive server for the Market Intelligence Bot.

This module creates a simple web server that can be pinged by
external services to keep the bot running on free hosting platforms.
"""

from flask import Flask
from threading import Thread
import logging
import os
import sys
import asyncio

# Set up logging for this module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

@app.route('/')
def home():
    """
    Home route that confirms the bot is running.
    This can be pinged by services like UptimeRobot to keep the bot alive.
    """
    logger.info("Keep-alive endpoint hit")
    return "Market Intelligence Bot is running!"

@app.route('/health')
def health():
    """
    Health check endpoint that returns a 200 status code.
    Useful for hosting platforms that require health checks.
    """
    return {"status": "healthy", "message": "Bot is operational"}, 200

def run():
    """
    Run the Flask app in a non-blocking way.
    Uses a production-ready server configuration.
    """
    # Get port from environment variable for platforms like Render
    # Default to 8080 if not provided
    port = int(os.environ.get('PORT', 8080))
    
    # Use 0.0.0.0 to make the server publicly accessible
    # for external ping services to reach it
    app.run(host='0.0.0.0', port=port)
    logger.info(f"Server running on port {port}")

def run_async_bot():
    """
    Run the bot with proper asyncio setup.
    This function is designed to be called in a separate thread.
    """
    try:
        # Set up a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Import the main bot function
        from marketbot.bot import main
        
        logger.info("Starting bot in background thread with asyncio event loop")
        
        # Run the bot
        loop.run_until_complete(main())
    except Exception as e:
        logger.error(f"Error starting bot in thread: {e}")

def keep_alive():
    """
    Start the keep-alive server.
    
    On platforms like Render, we run the web server directly.
    On other platforms, we run it in a daemon thread.
    """
    port = int(os.environ.get('PORT', 8080))
    logger.info("Starting keep-alive server")
    
    # Check if we're running on Render
    is_render = 'RENDER' in os.environ
    
    # If running on Render, execute the Flask server directly
    # This ensures the process stays alive as long as the server runs
    if is_render and 'PORT' in os.environ:
        logger.info(f"Running on Render. Starting web server on port {port} as main process")
        
        # Start bot in background thread with proper asyncio handling
        bot_thread = Thread(target=run_async_bot)
        bot_thread.daemon = True
        bot_thread.start()
        
        # Start web server in main thread
        run()
        sys.exit(0)  # Should never reach here on Render
    else:
        # For other environments, start the server in a daemon thread
        logger.info(f"Starting web server on port {port} in background thread")
        server_thread = Thread(target=run, daemon=True)
        server_thread.start()
        return server_thread 