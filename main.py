import logging
import os
import asyncio
from flask import Flask, request, jsonify
import google.generativeai as genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
)

# Load environment variables (for local development, overrides config.py)
from dotenv import load_dotenv
load_dotenv()

# Import configurations from config.py
import config

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Configuration (from Environment Variables first, then config.py) ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", config.TELEGRAM_BOT_TOKEN)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", config.GEMINI_API_KEY)

# IDs from config.py, can be overridden by environment variables for deployment flexibility
REQUIRED_CHANNEL_ID = int(os.getenv("REQUIRED_CHANNEL_ID", config.REQUIRED_CHANNEL_ID)) if config.REQUIRED_CHANNEL_ID is not None else None
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", config.ADMIN_USER_ID)) if config.ADMIN_USER_ID is not None else None
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", config.LOG_CHANNEL_ID)) if config.LOG_CHANNEL_ID is not None else None

# Webhook URL from environment or config.py default
WEBHOOK_URL = os.getenv("WEBHOOK_URL", config.WEBHOOK_URL_DEFAULT)
PORT = int(os.getenv("PORT", config.PORT))


# Configure Google Gemini API
if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY": # Check for placeholder
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
else:
    logger.error("GEMINI_API_KEY not set or is placeholder. Gemini functionality will be disabled.")
    model = None

# Initialize Flask app
app = Flask(__name__)

# Initialize python-telegram-bot Application
if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN": # Check for placeholder
    logger.critical("TELEGRAM_BOT_TOKEN is not set or is placeholder. Bot cannot run.")
    application = None
else:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# --- User ID Storage for Broadcast ---
USER_CHATS_FILE = "user_chats.txt"

def add_user_chat_id(chat_id: int):
    """Adds a unique chat ID to the storage file."""
    try:
        # Ensure the file exists, create if not
        if not os.path.exists(USER_CHATS_FILE):
            open(USER_CHATS_FILE, 'a').close()
            logger.info(f"Created user chat IDs file: {USER_CHATS_FILE}")

        with open(USER_CHATS_FILE, "r+") as f:
            existing_ids = set(line.strip() for line in f if line.strip())
            if str(chat_id) not in existing_ids:
                f.write(f"{chat_id}\n")
                logger.info(f"Added new chat ID to broadcast list: {chat_id}")
    except IOError as e:
        logger.error(f"Error writing chat ID to file {USER_CHATS_FILE}: {e}")

def get_all_user_chat_ids():
    """Retrieves all stored unique chat IDs."""
    try:
        with open(USER_CHATS_FILE, "r") as f:
            return [int(line.strip()) for line in f if line.strip()]
    except FileNotFoundError:
        logger.warning(f"User chat IDs file not found: {USER_CHATS_FILE}. Starting fresh.")
        return []
    except ValueError as e:
        logger.error(f"Error reading chat ID from file {USER_CHATS_FILE}: {e}. Some IDs might be corrupted.")
        return []

# --- User Log Channel Function ---
async def log_user_activity(bot, user, activity_type: str, message_text: str = None):
    """Sends user details and activity to a specified log channel."""
    if not config.ENABLE_USER_LOG_CHANNEL or LOG_CHANNEL_ID is None:
        logger.debug("User activity logging to channel is disabled or LOG_CHANNEL_ID not set.")
        return

    user_info = (
        f"<b>User Activity Log</b>\n"
        f"<b>User ID:</b> <code>{user.id}</code>\n"
        f"<b>Name:</b> {user.full_name or 'N/A'}\n"
    )
    if user.username:
        user_info += f"<b>Username:</b> @{user.username}\n"
        user_info += f"<b>Profile Link:</b> <a href='tg://user?id={user.id}'>Link to Profile</a>\n"
    else:
        user_info += f"<b>Username:</b> N/A (no public username)\n"

    user_info += (
        f"<b>Language Code:</b> {user.language_code or 'N/A'}\n"
        f"<b>Activity:</b> {activity_type}\n"
    )
    if message_text:
        # Truncate message text to avoid excessively long log messages
        truncated_message = message_text[:500] + "..." if len(message_text) > 500 else message_text
        user_info += f"<b>Message:</b> <code>{truncated_message}</code>\n"
    
    # Add timestamp
    user_info += f"<b>Timestamp:</b> {os.strftime('%Y-%m-%d %H:%M:%S %Z')}"

    try:
        await bot.send_message(
            chat_id=LOG_CHANNEL_ID,
            text=user_info,
            parse_mode="HTML"
        )
        logger.info(f"Logged {activity_type} for user {user.id} to channel {LOG_CHANNEL_ID}")
    except Exception as e:
        logger.error(f"Failed to send log to channel {LOG_CHANNEL_ID} for user {user.id}: {e}")

# --- Command Handler for /start ---
async def start(update: Update, context: CallbackContext) -> None:
    """Sends a custom start message with an image and multiple buttons."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    add_user_chat_id(chat_id)
    
    if application:
        await log_user_activity(application.bot, user, "Start Command")

    # Prepare inline keyboard from config
    keyboard = []
    for row in config.START_MESSAGE_BUTTONS:
        button_row = []
        for button_data in row:
            button_row.append(InlineKeyboardButton(button_data["text"], url=button_data["url"]))
        keyboard.append(button_row)
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        with open(config.START_IMAGE_PATH, "rb") as photo_file:
            await update.message.reply_photo(
                photo=photo_file,
                caption=config.START_MESSAGE_TEXT.format(user_first_name=user.first_name),
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
        logger.info(f"Sent start message with image to {user.first_name}")
    except FileNotFoundError:
        logger.warning(f"{config.START_IMAGE_PATH} not found. Sending text message instead.")
        await update.message.reply_text(
            f"{config.START_MESSAGE_TEXT.format(user_first_name=user.first_name)}\n\n"
            f"*(Image not found. Please ensure '{config.START_IMAGE_PATH}' is in the same directory.)*",
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error sending start message: {e}")
        await update.message.reply_text(
            f"{config.START_MESSAGE_TEXT.format(user_first_name=user.first_name)}\n\n"
            "*(An error occurred while sending the image.)*",
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

# --- User Message Reply (Gemini Integration) ---
async def echo(update: Update, context: CallbackContext) -> None:
    """Replies to the user's message using the Gemini API."""
    user_message = update.message.text
    user = update.effective_user
    chat_id = update.effective_chat.id
    add_user_chat_id(chat_id)

    if application:
        await log_user_activity(application.bot, user, "Message Received", message_text=user_message)

    if not user_message:
        return

    logger.info(f"Received message from {user.first_name} (ID: {user.id}): {user_message}")

    if config.ENABLE_CHANNEL_SUBSCRIPTION_CHECK and REQUIRED_CHANNEL_ID is not None:
        try:
            chat_member = await context.bot.get_chat_member(
                chat_id=REQUIRED_CHANNEL_ID, user_id=user.id
            )
            is_subscribed = chat_member.status in ["member", "administrator", "creator"]
        except Exception as e:
            logger.warning(f"Could not check subscription for {user.first_name} (ID: {user.id}) in channel {REQUIRED_CHANNEL_ID}: {e}")
            is_subscribed = False # Default to false if check fails

        if not is_subscribed:
            channel_link = ""
            if str(REQUIRED_CHANNEL_ID).startswith("-100"): # Private channel
                # Construct private channel invite link if possible, or provide fallback
                # Note: Direct link for private channels needs a prior invite link or manual lookup
                channel_link = f"https://t.me/c/{str(REQUIRED_CHANNEL_ID)[4:]}" # This is a direct link to a chat, not an invite.
                fallback_message = config.PRIVATE_CHANNEL_FALLBACK
            else: # Public channel
                # Attempt to get channel username
                try:
                    chat_info = await context.bot.get_chat(REQUIRED_CHANNEL_ID)
                    if chat_info.username:
                        channel_link = f"https://t.me/{chat_info.username}"
                    else:
                        channel_link = f"https://t.me/c/{str(REQUIRED_CHANNEL_ID)[4:]}" # Fallback for public without username
                        fallback_message = f"Please subscribe to our channel: {channel_link}"
                except Exception as chat_info_e:
                    logger.error(f"Could not get chat info for channel {REQUIRED_CHANNEL_ID}: {chat_info_e}")
                    channel_link = ""
                    fallback_message = "Please subscribe to our channel. The link could not be generated automatically."
                
            await update.message.reply_text(
                config.CHANNEL_REQUIRED_MESSAGE.format(
                    channel_link=channel_link,
                    fallback_message=fallback_message
                )
            )
            return
    
    if not config.ENABLE_USER_MESSAGE_REPLY:
        logger.info(f"User message reply is disabled in config.py for {user.first_name}")
        return # Do not reply if feature is disabled

    if not model:
        await update.message.reply_text(config.AI_UNAVAILABLE_MESSAGE)
        return

    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        response = model.generate_content(user_message)
        gemini_reply = response.text
        logger.info(f"Gemini responded to {user.first_name}: {gemini_reply[:100]}...")
        await update.message.reply_text(gemini_reply)
    except Exception as e:
        logger.error(f"Error calling Gemini API for {user.first_name}: {e}")
        await update.message.reply_text(config.GEMINI_API_ERROR_MESSAGE)

# --- Command Handler for /broadcast ---
async def broadcast(update: Update, context: CallbackContext) -> None:
    """Sends a message to all users who have interacted with the bot."""
    user = update.effective_user
    
    if not config.ENABLE_BROADCAST:
        await update.message.reply_text("Broadcast feature is disabled.")
        logger.warning(f"Broadcast feature is disabled in config.py. Attempt by {user.id}")
        return

    if ADMIN_USER_ID is None or user.id != ADMIN_USER_ID:
        await update.message.reply_text(config.UNAUTHORIZED_BROADCAST_MESSAGE)
        logger.warning(f"Unauthorized broadcast attempt by user ID: {user.id}")
        return

    if not context.args:
        await update.message.reply_text(config.BROADCAST_USAGE_MESSAGE)
        return

    message_to_send = " ".join(context.args)
    all_chat_ids = get_all_user_chat_ids()
    
    # Remove admin's own ID from broadcast list if present
    if ADMIN_USER_ID in all_chat_ids:
        all_chat_ids.remove(ADMIN_USER_ID)

    sent_count = 0
    failed_count = 0

    await update.message.reply_text(f"Starting broadcast to {len(all_chat_ids)} users...")
    logger.info(f"Broadcast initiated by {user.first_name} (ID: {user.id}) to {len(all_chat_ids)} users.")

    for chat_id in all_chat_ids:
        try:
            await context.bot.send_message(chat_id=chat_id, text=message_to_send)
            sent_count += 1
            await asyncio.sleep(0.05) # Small delay to avoid hitting Telegram API rate limits
        except Exception as e:
            logger.error(f"Failed to send broadcast to chat ID {chat_id}: {e}")
            failed_count += 1

    await update.message.reply_text(
        f"Broadcast finished!\nSent to: {sent_count} users\nFailed for: {failed_count} users"
    )
    logger.info(f"Broadcast completed. Sent: {sent_count}, Failed: {failed_count}.")

# --- Webhook handler for Flask ---
@app.route("/webhook", methods=["POST"])
async def telegram_webhook():
    """Handle incoming Telegram updates via webhook."""
    if not application:
        return jsonify({"status": "error", "message": config.BOT_NOT_INITIALIZED_MESSAGE}), 500

    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        asyncio.create_task(application.process_update(update))
        return jsonify({"status": "ok"})
    except Exception as e:
        logger.error(f"Error processing webhook update: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# --- Set up webhook command (for local testing or initial setup) ---
async def set_webhook_command(update: Update, context: CallbackContext) -> None:
    """Sets the Telegram webhook."""
    if not application:
        await update.message.reply_text(config.BOT_NOT_INITIALIZED_MESSAGE)
        return

    # Check if WEBHOOK_URL is set and not a placeholder
    if not WEBHOOK_URL or WEBHOOK_URL == config.WEBHOOK_URL_DEFAULT:
        await update.message.reply_text(config.WEBHOOK_NOT_SET_MESSAGE)
        return

    try:
        await application.bot.set_webhook(url=WEBHOOK_URL)
        await update.message.reply_text(f"Webhook successfully set to: {WEBHOOK_URL}")
        logger.info(f"Webhook set to {WEBHOOK_URL}")
    except Exception as e:
        await update.message.reply_text(f"Failed to set webhook: {e}")
        logger.error(f"Failed to set webhook: {e}")

# --- Main function to run the bot (Flask for webhook) ---
def main() -> None:
    """Starts the bot with webhook."""
    if not application:
        logger.critical("Bot application could not be initialized. Exiting.")
        return

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setwebhook", set_webhook_command))
    application.add_handler(CommandHandler("broadcast", broadcast))
    
    # Only add echo handler if user message reply is enabled
    if config.ENABLE_USER_MESSAGE_REPLY:
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    logger.info(f"Starting Flask app on port {PORT}...")
    app.run(host="0.0.0.0", port=PORT, debug=False)


if __name__ == "__main__":
    main()
