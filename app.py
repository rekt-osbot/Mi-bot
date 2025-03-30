"""
Entry point script for the Market Intelligence Bot.

This file serves as the main entry point for the application.
It imports and runs the bot from the marketbot package.
"""

import logging
import sys
import os
import argparse
import threading
import traceback

# Configure basic logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Thread exception handler
def thread_exception_handler(args):
    """Handler for unhandled exceptions in threads."""
    logger.error(f"Unhandled exception in thread {args.thread.name}: {args.exc_value}")
    logger.error("".join(traceback.format_tb(args.exc_traceback)))

# Register the thread exception handler
threading.excepthook = thread_exception_handler

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
        # In production environments, keep_alive() may not return if it runs the web server
        # in the main thread (which is what we want for Render)
        keep_alive()
        
        # If we're still here, keep_alive() didn't take over the main thread,
        # which means we're not in a production environment that requires it
    
    # Set environment variables for long polling if requested
    if args.long_polling or is_production:
        logger.info("Using long polling intervals to reduce API calls")
        os.environ["LONG_POLLING"] = "True"
    
    # Only continue to start the bot if we're not in a production environment
    # where keep_alive() has taken over the main thread
    if not is_production or 'PORT' not in os.environ:
        # Import the main bot module
        from marketbot.bot import main
        
        if __name__ == "__main__":
            logger.info("Starting Market Intelligence Bot in main thread")
            
            # Import asyncio here to avoid circular imports
            import asyncio
            
            # Run the main function
            asyncio.run(main())
except ImportError as e:
    logger.error(f"Error importing bot package: {e}")
    logger.error("Make sure you have set up the package structure correctly")
    sys.exit(1)
except Exception as e:
    logger.error(f"Error starting bot: {e}")
    logger.error(traceback.format_exc())
    sys.exit(1) 