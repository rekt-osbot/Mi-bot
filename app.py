"""
Entry point script for the Market Intelligence Bot.

This file serves as the main entry point for the application.
It imports and runs the bot from the marketbot package.
"""

import logging
import sys
import os
import argparse

# Configure basic logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Ensure the src directory is in the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Try to import the keep-alive module (optional)
try:
    from keep_alive import keep_alive
    has_keep_alive = True
except ImportError:
    logger.info("Keep-alive module not found. Web server will not be started.")
    has_keep_alive = False

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Market Intelligence Bot")
    parser.add_argument(
        "--keep-alive", 
        action="store_true",
        help="Start a web server to keep the bot alive on free hosting"
    )
    parser.add_argument(
        "--long-polling", 
        action="store_true",
        help="Use a longer polling interval to reduce API calls"
    )
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Enable debug logging"
    )
    
    return parser.parse_args()

# Import and run the bot
try:
    # Check if we're running on Render or similar platform
    is_production = 'RENDER' in os.environ or 'PORT' in os.environ
    
    # Parse any command line arguments
    args = parse_args()
    
    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Start the keep-alive server if in production or explicitly requested
    if (is_production or args.keep_alive) and has_keep_alive:
        logger.info("Starting keep-alive server...")
        keep_alive()
    
    # Set environment variables for long polling if requested
    if args.long_polling:
        logger.info("Using long polling intervals to reduce API calls")
        os.environ["LONG_POLLING"] = "True"
    
    # Import the main bot module
    from marketbot.bot import main
    
    if __name__ == "__main__":
        logger.info("Starting Market Intelligence Bot")
        main()
except ImportError as e:
    logger.error(f"Error importing bot package: {e}")
    logger.error("Make sure you have set up the package structure correctly")
    sys.exit(1)
except Exception as e:
    logger.error(f"Error starting bot: {e}")
    sys.exit(1) 