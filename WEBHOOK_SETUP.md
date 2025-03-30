# Setting Up Telegram Bot Webhook Mode on Render

This guide explains how to set up your Market Intelligence Bot to use webhook mode on Render, which is more reliable and efficient than polling mode for serverless environments.

## What are Webhooks?

Instead of the bot constantly polling Telegram's servers for updates, webhook mode allows Telegram to send updates directly to your server whenever there's a new message or interaction with your bot. This is:

- More efficient (no constant polling)
- More responsive (updates are received immediately)
- Better suited for serverless/cloud environments like Render

## Prerequisites

1. Your bot is already deployed to Render
2. You have your bot token from BotFather
3. Your Render service has a public HTTPS URL

## Setup Steps

### 1. Get Your Render Service URL

Your Render service will have a URL like: `https://your-app-name.onrender.com`

### 2. Set the Webhook

There are two ways to set up the webhook:

#### Option 1: Using the built-in endpoint

Visit the following URL in your browser (replace with your actual values):

```
https://your-app-name.onrender.com/set-webhook?token=YOUR_BOT_TOKEN&url=https://your-app-name.onrender.com
```

This will:
1. Tell Telegram to send all bot updates to your Render service
2. Configure your application to process these updates

#### Option 2: Using the Telegram API directly

If Option 1 doesn't work, you can set the webhook directly with Telegram:

```
https://api.telegram.org/botYOUR_BOT_TOKEN/setWebhook?url=https://your-app-name.onrender.com/telegram-webhook
```

### 3. Verify Webhook Setup

Visit:

```
https://api.telegram.org/botYOUR_BOT_TOKEN/getWebhookInfo
```

You should see a response showing that your webhook is properly configured with your Render URL.

### 4. Test Your Bot

Send a message to your bot on Telegram. It should now respond properly.

## Troubleshooting

### Bot Doesn't Respond

1. Check the Render logs for any errors
2. Verify the webhook is set correctly using getWebhookInfo
3. Make sure your bot token is correctly set in the Render environment variables

### Error in Webhook Setup

If you get an error when setting the webhook:

1. Make sure your URL is https (Telegram requires this)
2. Check that your bot token is correct
3. Ensure your Render service is running

## Environment Variables

Make sure these are set in your Render dashboard:

- `BOT_TOKEN`: Your Telegram bot token
- `WEBHOOK_URL`: Your full Render service URL (https://your-app-name.onrender.com)
- `TIME_ZONE`: Your timezone (e.g., "Asia/Kolkata")

## Benefits of Webhook Mode on Render

- **Always responsive**: Bot responds immediately to messages
- **No polling loop**: Reduces CPU and memory usage
- **More reliable**: No need to worry about keeping a long-running process alive
- **Better scaling**: Handles traffic spikes more efficiently 