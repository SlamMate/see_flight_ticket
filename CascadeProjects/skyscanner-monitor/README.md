# Skyscanner Price Monitor

This project uses Python, Playwright, and GitHub Actions to automatically monitor flight prices on Skyscanner and send updates to a Telegram chat.

## Setup Instructions

### 1. Telegram Bot Setup
1. Open Telegram and search for `@BotFather`.
2. Send `/newbot` and follow the instructions to create a new bot.
3. Save the **Bot Token** provided by BotFather (e.g., `123456789:ABCdefGHIjklMNOpqrSTUvwxYZ`).
4. Search for your new bot in Telegram and send a message (e.g., "Hello") to start a chat.
5. To get your **Chat ID**, open the following URL in your browser: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
6. Look for `"chat":{"id":123456789}` in the response. Save that ID.

### 2. GitHub Setup
1. Fork or push this repository to your own GitHub account.
2. Go to your repository settings -> **Secrets and variables** -> **Actions**.
3. Click **New repository secret** and add the following:
   - Name: `TELEGRAM_BOT_TOKEN`
   - Value: `<your-bot-token>`
   - Name: `TELEGRAM_CHAT_ID`
   - Value: `<your-chat-id>`

### 3. How it works
The GitHub Action is scheduled to run 3 times a day (00:00, 06:00, 12:00 UTC) which corresponds roughly to morning, afternoon, and evening depending on your time zone.

It uses Playwright to open Skyscanner in a headless browser, waits for the page to load, extracts the top 5 flight prices, and sends them to your configured Telegram chat.

If it fails to find prices (e.g., due to bot protection or page layout changes), it will upload a screenshot to the GitHub Actions artifacts for debugging.

## Local Testing
If you want to run this locally:

```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Set environment variables
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"

# Run the script
python monitor.py
```
