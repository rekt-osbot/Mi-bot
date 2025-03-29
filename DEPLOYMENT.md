# Market Intelligence Bot Deployment Guide

This guide outlines how to deploy the Market Intelligence Bot on various free hosting platforms.

## Deployment Options

### 1. Replit (Easiest Option)

[Replit](https://replit.com/) offers free hosting for Python applications including bots.

**Setup Steps:**

1. Create a free account on Replit
2. Create a new Python Repl
3. Upload the bot code or connect to your GitHub repository
4. Add environment variables in the Secrets tab:
   - `BOT_TOKEN` - Your Telegram bot token
   - `ADMIN_USER_ID` - Your Telegram user ID 
   - `TIME_ZONE` - Your timezone (e.g., "Asia/Kolkata")
5. Run the bot by executing `python app.py`

**Keep Alive:**
- Create a `keep_alive.py` file:
```python
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
```
- Modify `app.py` to import and use this function:
```python
from keep_alive import keep_alive

# At the top of main():
keep_alive()
```
- Use a service like [UptimeRobot](https://uptimerobot.com/) to ping the bot URL every 5 minutes

### 2. Render (Free Tier)

[Render](https://render.com/) provides a free tier for web services.

**Setup Steps:**

1. Create a free Render account
2. Connect your GitHub repository 
3. Create a new Web Service
4. Configure the following:
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`
5. Add environment variables in the dashboard
6. Deploy the service

### 3. PythonAnywhere (Limited Free Tier)

[PythonAnywhere](https://www.pythonanywhere.com/) offers a free tier with some limitations.

**Setup Steps:**

1. Create a free account
2. Upload your code or clone from GitHub
3. Set up a new virtual environment
4. Install dependencies using `pip install -r requirements.txt`
5. Configure environment variables
6. Create a new "Always-on task" (free accounts have limited hours)
7. Set the task to run `python app.py`

### 4. Railway.app (Credit-Based Free Tier)

[Railway.app](https://railway.app/) offers $5 of free credits per month.

**Setup Steps:**

1. Create a Railway account
2. Connect your GitHub repository
3. Deploy a new project from the repository
4. Configure environment variables
5. Deploy the service

## Optimizations for Free Hosting

The bot has been configured with several optimizations to minimize resource usage:

1. **Extended Polling Interval**: Set to 60 seconds to reduce API calls
2. **Lower Timeouts**: All timeouts reduced to 30 seconds
3. **Message Filtering**: Non-market messages are ignored completely
4. **Single Warning System**: Users are only warned once about admin access
5. **Whitelist System**: Only specified users can access the bot

## Additional Free Hosting Recommendations

- **GitHub Actions**: You can set up a GitHub Action workflow to run your bot periodically
- **Google Cloud Run**: Has a generous free tier but requires more setup
- **Heroku**: Limited free dyno hours (currently 550 hours/month) which is enough if the bot doesn't need to run 24/7

## Troubleshooting

- **Bot Stops Responding**: Most free services have inactivity timeouts. Implement a keep-alive mechanism.
- **Memory Errors**: Free tiers have memory limitations. The bot is optimized for low memory usage.
- **CPU Usage**: If the bot is terminated for excessive CPU usage, increase the polling interval further.

## Keeping the Bot Free Forever

To ensure the bot remains free forever:

1. Use the longest practical polling interval (60-300 seconds)
2. Implement lightweight keep-alive mechanisms
3. Avoid computationally expensive operations
4. Use caching for frequently accessed data
5. Limit news article fetching to only when requested
6. Consider disabling scheduled updates during low-usage hours
7. Rotate between free services if necessary

If you encounter any issues with the deployment, please open an issue on the GitHub repository. 