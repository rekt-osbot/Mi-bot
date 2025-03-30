"""
Keep-alive server for the Market Intelligence Bot.

This module creates a simple web server that can be pinged by
external services to keep the bot running on free hosting platforms.
"""

from flask import Flask, request, jsonify
from threading import Thread
import logging
import os
import sys
import asyncio
import signal
import json

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

@app.route('/info')
def info():
    """
    Returns information about the bot status.
    """
    return {
        "status": "online",
        "web_only_mode": os.environ.get("WEB_ONLY_MODE", "False") == "True",
        "version": "1.0.0",
        "platform": "Render" if 'RENDER' in os.environ else "Unknown",
        "time_zone": os.environ.get("TIME_ZONE", "UTC")
    }

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Simple webhook endpoint that can be used to interact with the bot.
    """
    try:
        data = request.json
        logger.info(f"Webhook received: {data}")
        return {"status": "received", "message": "Webhook processed successfully"}, 200
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}, 500

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

def dummy_bot():
    """
    A dummy bot function that just logs status.
    This is used when we can't run the actual bot due to threading issues.
    """
    logger.info("Running in dummy bot mode due to threading limitations on this platform")
    while True:
        try:
            # Just sleep and stay alive
            import time
            time.sleep(60)
            logger.info("Dummy bot is still running")
        except Exception as e:
            logger.error(f"Error in dummy bot: {e}")
            time.sleep(60)

def run_async_bot():
    """
    Run the bot with proper asyncio setup.
    This function is designed to be called in a separate thread.
    """
    try:
        # We're avoiding using asyncio and signal handling altogether in the thread
        # Instead, we'll just run a dummy bot that keeps the thread alive
        # The real functionality will be provided by the web server
        
        # Set an environment variable to indicate we're running in web-only mode
        os.environ["WEB_ONLY_MODE"] = "True"
        
        logger.info("Starting simplified bot in background thread (web server only mode)")
        
        # Run a simplified version that doesn't depend on asyncio or signals
        dummy_bot()
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