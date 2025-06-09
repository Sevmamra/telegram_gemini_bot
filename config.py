import re
from os import getenv, environ

# config.py

# --- Bot API Keys (Placeholders) ---
# IMPORTANT: For deployment, use environment variables on your hosting platform!
# These are primarily for local testing convenience if you don't use a .env file.
TELEGRAM_BOT_TOKEN = environ.get("TELEGRAM_BOT_TOKEN", "")  # Replace with your actual bot token from BotFather
GEMINI_API_KEY = environ.get("GEMINI_API_KEY", "AIzaSyAeqhTYD_goXKmVch8C_a5NCNnDl0PTKfQ")          # Replace with your actual Gemini API key from Google AI Studio

# --- Bot and Channel IDs (Placeholders) ---
# REQUIRED_CHANNEL_ID: Users must subscribe to this channel to use the bot.
# Get your channel ID by forwarding any message from the channel to @JsonDumpBot or @RawDataBot.
# It will be a negative number, e.g., -1001234567890. Set to None if no channel check is needed.
REQUIRED_CHANNEL_ID = environ.get("REQUIRED_CHANNEL_ID", "-1002781903513")  # Example: -1001234567890

# ADMIN_USER_ID: Your Telegram User ID to enable the broadcast command.
# Get your user ID by messaging @userinfobot. It's a numeric ID, e.g., 1234567890.
# Set to None if no admin broadcast is needed.
ADMIN_USER_ID = environ.get("ADMIN_USER_ID", "6567162029")  # Example: 1234567890

# LOG_CHANNEL_ID: Private channel for bot activity logs. Bot must be an admin in this channel.
# Get its ID like REQUIRED_CHANNEL_ID. Set to None if no logging to channel is needed.
LOG_CHANNEL_ID = environ.get("LOG_CHANNEL_ID", "-1002781903513")  # Example: -1001234567891

# --- Deployment Configuration ---
# Default Bot Port for Flask server. This will be used by Gunicorn.
PORT = 8080

# WEBHOOK_URL_DEFAULT: For local testing, this will be your ngrok URL + /webhook.
# For cloud deployment, this is typically set via an environment variable on the platform.
# This default is used if WEBHOOK_URL environment variable is not explicitly set.
WEBHOOK_URL_DEFAULT = "YOUR_NGROK_URL/webhook" # Example: "https://abcdef123456.ngrok-free.app/webhook"

# --- Custom Start Message Details ---
# Path to the image file for the /start command. Ensure it's in the project root.
START_IMAGE_PATH = "start_image.jpg"

# The text message sent with the /start command. {user_first_name} is a placeholder.
START_MESSAGE_TEXT = (
    "Hello, {user_first_name}! 👋\n\n"
    "I'm your friendly AI assistant, powered by Google Gemini. "
    "I can chat with you about almost anything. Just send me a message!\n\n"
    "Here are some useful links:"
)

# Buttons for the start message (Text, URL).
# Each inner list is a row of buttons.
START_MESSAGE_BUTTONS = [
    [
        {"text": "Visit My Website", "url": "https://example.com"},
        {"text": "Follow on Twitter", "url": "https://twitter.com/your_handle"},
    ],
    [
        {"text": "Join Our Community", "url": "https://t.me/your_community_channel"},
        {"text": "Support Me", "url": "https://buymeacoffee.com/your_profile"},
    ],
]

# --- Bot Behavior Toggles ---
# Set to True to enable automatic replies to user messages via Gemini.
ENABLE_USER_MESSAGE_REPLY = True

# Set to True to enable the mandatory channel subscription check.
# Make sure REQUIRED_CHANNEL_ID is set if this is True.
ENABLE_CHANNEL_SUBSCRIPTION_CHECK = False # Set to True once REQUIRED_CHANNEL_ID is configured

# Set to True to enable the admin broadcast feature.
# Make sure ADMIN_USER_ID is set if this is True.
ENABLE_BROADCAST = False # Set to True once ADMIN_USER_ID is configured

# Set to True to enable logging user activity to a dedicated channel.
# Make sure LOG_CHANNEL_ID is set if this is True.
ENABLE_USER_LOG_CHANNEL = False # Set to True once LOG_CHANNEL_ID is configured

# --- Error and System Messages ---
GEMINI_API_ERROR_MESSAGE = "I'm sorry, I'm having trouble processing that right now with Gemini. Please try again later."
AI_UNAVAILABLE_MESSAGE = "AI functionality is currently unavailable. Please check the API key configuration."
UNAUTHORIZED_BROADCAST_MESSAGE = "You are not authorized to use this command."
BROADCAST_USAGE_MESSAGE = "Usage: /broadcast <your message here>"
WEBHOOK_NOT_SET_MESSAGE = "WEBHOOK_URL is not set in environment variables or config.py. Cannot set webhook."
BOT_NOT_INITIALIZED_MESSAGE = "Bot not initialized. Cannot set webhook."

CHANNEL_REQUIRED_MESSAGE = (
    "🚨 To use this bot, please subscribe to our channel.\n\n"
    "For public channels: {channel_link}\n"
    "For private channels: {fallback_message}\n\n"
    "Once subscribed, you can send your message again. Thank you!"
)
PRIVATE_CHANNEL_FALLBACK = "Please join our private channel to use the bot. Ask an admin for the invite link."
