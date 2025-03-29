# Market Intelligence Bot

A Telegram bot that provides real-time market intelligence, news, and analysis with Hinglish support.

## Features

- **Market News**: Get the latest news from various financial markets
- **Country-Specific News**: Filter news by country (US, India, global)
- **Topic-Based News**: Get news on specific topics (commodities, crypto, forex, etc.)
- **Smart Filtering**: Automatically filters casual conversation from market queries
- **Admin-Only Mode**: Restrict access to authorized users only
- **Hinglish Support**: Interact with the bot in Hindi-English mixed language
- **Enhanced Analysis**: Get summaries and insights from news articles, not just links
- **Optimized for Free Hosting**: Configured to run efficiently on free hosting platforms

## Screenshots

![Bot Screenshot](https://ibb.co/0yvp6mX8)

## Setup

### Prerequisites

- Python 3.8 or higher
- A Telegram bot token (get one from [@BotFather](https://t.me/BotFather))
- Your Telegram User ID (get it from [@userinfobot](https://t.me/userinfobot))

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/market-intelligence-bot.git
   cd market-intelligence-bot
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with the following:
   ```
   BOT_TOKEN=your_telegram_bot_token
   ADMIN_USER_ID=your_telegram_user_id
   TIME_ZONE=Asia/Kolkata  # Change to your timezone
   DAILY_UPDATE_TIME=09:00
   ```

4. Run the bot
   ```bash
   python app.py
   ```

### Command Line Options

The bot supports several command line options:

- `--keep-alive`: Start a web server to keep the bot alive on free hosting platforms
- `--long-polling`: Use a longer polling interval to reduce API calls and conserve resources
- `--debug`: Enable debug logging for troubleshooting

Example:
```bash
python app.py --keep-alive --long-polling
```

## Deployment

For detailed deployment instructions on free hosting platforms, see [DEPLOYMENT.md](DEPLOYMENT.md).

Quick options:
- **Replit**: Easy setup with free hosting
- **Render**: Free tier for web services
- **PythonAnywhere**: Limited free tier
- **Railway.app**: Credit-based free tier

## Usage

### User Commands

- `/start` - Start the bot and get a welcome message
- `/help` - Show help message with available commands
- `/news` - Get the latest market news
- `/news_india` - Get Indian market news
- `/news_us` - Get US market news
- `/news_global` - Get global market news
- `/news_commodities` - Get commodities news
- `/news_breaking` - Get breaking market news
- `/topicnews` - Get news on a specific topic
- `/technical` - Get technical analysis

### Natural Language Queries

The bot also understands natural language queries in both English and Hinglish:

- "What's happening in the US market today?"
- "Latest news on Nifty"
- "Sensex kitna hai abhi?" (What's the Sensex level now?)
- "Gold price kya chal raha hai?" (What's the gold price doing?)
- "Share market me kya ho raha hai?" (What's happening in the share market?)

## Admin Features

The bot offers special admin controls through the `admin_only` decorator. 
By default, only the user ID specified in the `ADMIN_USER_ID` environment 
variable and users in the whitelist can access the bot's commands.

To add a user to the whitelist, edit the `WHITELISTED_USER_IDS` set in 
`src/marketbot/utils/text_processing.py`.

## Customization

### Adding New Sources

To add a new financial news source:

1. Add the source configuration in `src/marketbot/config/settings.py`
2. Create a provider method in `src/marketbot/news_providers/financial_site.py`
3. Add the provider to the `financial_sites` dictionary in `NewsService.__init__` method

### Modifying Hinglish Support

To enhance Hinglish recognition:

1. Add patterns to `GREETING_PATTERNS` in `src/marketbot/handlers/message_handlers.py`
2. Add terms to `MARKET_KEYWORDS` in the same file
3. Add phrases to `HINGLISH_MARKET_PHRASES` for better detection

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Python Telegram Bot library
- Beautiful Soup for web scraping
- Financial news providers for their content

## Contact

For questions or support, please open an issue on the GitHub repository. 