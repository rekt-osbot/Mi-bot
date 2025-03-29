"""
Keep-alive server for the Market Intelligence Bot.

This module creates a simple web server that can be pinged by
external services to keep the bot running on free hosting platforms.
"""

from flask import Flask
from threading import Thread
import logging

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
    # Use 0.0.0.0 to make the server publicly accessible
    # for external ping services to reach it
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    """
    Start the keep-alive server in a separate thread.
    This function should be called from the main bot script.
    """
    logger.info("Starting keep-alive server")
    
    # Create a daemon thread so it auto-closes when the main program exits
    server_thread = Thread(target=run, daemon=True)
    server_thread.start()
    
    logger.info("Keep-alive server started on port 8080")
    
    return server_thread 