"""
Keep-alive server for the Market Intelligence Bot.

This module creates a simple web server that can be pinged by
external services to keep the bot running on free hosting platforms.
"""

from flask import Flask
from threading import Thread
import logging
import os

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

def keep_alive():
    """
    Start the keep-alive server in a separate thread.
    This function should be called from the main bot script.
    """
    logger.info("Starting keep-alive server")
    
    # Create a daemon thread so it auto-closes when the main program exits
    server_thread = Thread(target=run, daemon=True)
    server_thread.start()
    
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Keep-alive server started on port {port}")
    
    return server_thread 