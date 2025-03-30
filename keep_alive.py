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
import json
import traceback

# Set up logging for this module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Global reference to the bot application
bot_app = None

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
    # Get webhook info from Telegram
    webhook_info = {}
    try:
        import requests
        token = os.environ.get('BOT_TOKEN', '')
        if token:
            response = requests.get(f"https://api.telegram.org/bot{token}/getWebhookInfo")
            if response.status_code == 200:
                webhook_info = response.json().get('result', {})
    except Exception as e:
        logger.error(f"Error getting webhook info: {e}")
    
    return {
        "status": "online",
        "version": "1.0.0",
        "platform": "Render" if 'RENDER' in os.environ else "Unknown",
        "time_zone": os.environ.get("TIME_ZONE", "UTC"),
        "webhook_mode": True,
        "bot_initialized": bot_app is not None,
        "webhook_info": webhook_info
    }

@app.route('/telegram-webhook', methods=['POST'])
def telegram_webhook():
    """
    Process incoming updates from Telegram.
    This is the endpoint Telegram sends updates to when using webhook mode.
    """
    try:
        # Log the entire request for debugging
        logger.info(f"Webhook request received: {request.method} {request.url}")
        logger.info(f"Request headers: {dict(request.headers)}")
        
        # Get the update JSON
        update_json = request.get_json(force=True)
        logger.info(f"Received Telegram update: {json.dumps(update_json)}")
        
        global bot_app
        if not bot_app:
            # Initialize the bot application if it's not already initialized
            try:
                from src.marketbot.bot import setup_bot
                bot_app = setup_bot()
                logger.info("Bot application initialized for webhook processing")
            except Exception as e:
                logger.error(f"Failed to initialize bot application: {e}")
                logger.error(traceback.format_exc())
                return {"status": "error", "message": "Bot initialization failed"}, 500
        
        # Process the update
        if bot_app:
            try:
                from telegram import Update
                
                # Create the Update object and process it
                update = Update.de_json(update_json, bot_app.bot)
                
                # Use application.process_update which processes synchronously
                bot_app.process_update(update)
                
                logger.info("Update processed successfully")
                return {"status": "success"}, 200
            except Exception as e:
                logger.error(f"Error processing update: {e}")
                logger.error(traceback.format_exc())
                return {"status": "error", "message": f"Update processing error: {str(e)}"}, 500
        else:
            logger.error("Bot not initialized")
            return {"status": "error", "message": "Bot not initialized"}, 500
    except Exception as e:
        logger.error(f"Error in telegram_webhook: {e}")
        logger.error(traceback.format_exc())
        return {"status": "error", "message": str(e)}, 500

@app.route('/telegram-webhook-test', methods=['GET'])
def test_webhook():
    """
    Test endpoint to verify the webhook is working.
    """
    try:
        logger.info("Webhook test request received")
        
        # Check if bot is initialized
        if not bot_app:
            from src.marketbot.bot import setup_bot
            global bot_app
            bot_app = setup_bot()
            
        # Create a test message
        test_update = {
            "update_id": 123456789,
            "message": {
                "message_id": 123,
                "from": {
                    "id": int(os.environ.get("ADMIN_USER_ID", "12345")),
                    "is_bot": False,
                    "first_name": "Test",
                    "username": "testuser"
                },
                "chat": {
                    "id": int(os.environ.get("ADMIN_USER_ID", "12345")),
                    "first_name": "Test",
                    "username": "testuser",
                    "type": "private"
                },
                "date": 1616788800,
                "text": "/test"
            }
        }
        
        # Process the test update
        from telegram import Update
        update = Update.de_json(test_update, bot_app.bot)
        
        # Process the test update manually
        logger.info("Processing test webhook update...")
        
        if bot_app:
            # Just log that we would process it
            logger.info(f"Would process update: {test_update}")
            return {"status": "success", "message": "Test webhook received and would be processed"}, 200
        else:
            return {"status": "error", "message": "Bot not initialized"}, 500
    except Exception as e:
        logger.error(f"Error in test_webhook: {e}")
        logger.error(traceback.format_exc())
        return {"status": "error", "message": str(e)}, 500

@app.route('/set-webhook', methods=['GET'])
def set_webhook():
    """
    Set up the Telegram webhook with the correct URL.
    """
    try:
        # Get the webhook URL from query parameters or environment
        webhook_url = request.args.get('url', os.environ.get('WEBHOOK_URL', ''))
        token = request.args.get('token', os.environ.get('BOT_TOKEN', ''))
        
        if not webhook_url or not token:
            return {"status": "error", "message": "Missing webhook URL or token"}, 400
        
        # Format the webhook URL if needed
        if not webhook_url.endswith('/telegram-webhook'):
            if not webhook_url.endswith('/'):
                webhook_url += '/'
            webhook_url += 'telegram-webhook'
        
        # Set up the webhook with Telegram
        import requests
        api_url = f"https://api.telegram.org/bot{token}/setWebhook"
        response = requests.post(api_url, json={'url': webhook_url})
        
        # Check if the webhook was set successfully
        if response.status_code == 200 and response.json().get('ok'):
            logger.info(f"Webhook set successfully: {webhook_url}")
            return {"status": "success", "webhook_url": webhook_url}, 200
        else:
            logger.error(f"Failed to set webhook: {response.text}")
            return {"status": "error", "message": response.text}, 500
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        logger.error(traceback.format_exc())
        return {"status": "error", "message": str(e)}, 500

@app.route('/send-test-message', methods=['GET'])
def send_test_message():
    """
    Send a test message to verify the bot is working.
    """
    try:
        # Get the chat ID from query parameters or environment
        chat_id = request.args.get('chat_id', os.environ.get('ADMIN_USER_ID', ''))
        token = request.args.get('token', os.environ.get('BOT_TOKEN', ''))
        
        if not chat_id or not token:
            return {"status": "error", "message": "Missing chat ID or token"}, 400
        
        # Send a test message using the Telegram API
        import requests
        api_url = f"https://api.telegram.org/bot{token}/sendMessage"
        response = requests.post(api_url, json={
            'chat_id': chat_id,
            'text': "This is a test message from the Market Intelligence Bot running on Render."
        })
        
        # Check if the message was sent successfully
        if response.status_code == 200 and response.json().get('ok'):
            logger.info(f"Test message sent successfully to chat ID: {chat_id}")
            return {"status": "success", "message": "Test message sent"}, 200
        else:
            logger.error(f"Failed to send test message: {response.text}")
            return {"status": "error", "message": response.text}, 500
    except Exception as e:
        logger.error(f"Error sending test message: {e}")
        logger.error(traceback.format_exc())
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

def init_bot_for_webhooks():
    """
    Initialize the bot in webhook mode.
    """
    try:
        # Import the setup function from the bot module
        from src.marketbot.bot import setup_bot
        
        # Initialize the bot application
        global bot_app
        bot_app = setup_bot()
        
        logger.info("Bot initialized for webhook mode")
        return True
    except Exception as e:
        logger.error(f"Error initializing bot for webhooks: {e}")
        logger.error(traceback.format_exc())
        return False

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
        
        # Initialize the bot for webhook mode
        init_bot_for_webhooks()
        
        # Start web server in main thread
        run()
        sys.exit(0)  # Should never reach here on Render
    else:
        # For other environments, start the server in a daemon thread
        logger.info(f"Starting web server on port {port} in background thread")
        server_thread = Thread(target=run, daemon=True)
        server_thread.start()
        return server_thread 