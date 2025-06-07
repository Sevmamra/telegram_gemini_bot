import logging
import os
import asyncio
from flask import Flask, request, jsonify
import google.generativeai as genai
from config import  TELEGRAM_BOT_TOKEN, LOG_CHANNEL, ADMIN_USER_ID, REQUIRED_CHANNEL_ID, LOG_CHANNEL_ID, GEMINI_API_KEY, WEBHOOK_URL
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
)

# Load environment variables (for local development)
from dotenv import load_dotenv
load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Configuration (from Environment Variables) ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
REQUIRED_CHANNEL_ID = os.getenv("REQUIRED_CHANNEL_ID")
if REQUIRED_CHANNEL_ID:
    try:
        REQUIRED_CHANNEL_ID = int(REQUIRED_CHANNEL_ID)
    except ValueError:
        logger.error("REQUIRED_CHANNEL_ID must be an integer if set. Disabling channel check.")
        REQUIRED_CHANNEL_ID = None

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 8080))
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID")
if ADMIN_USER_ID:
    try:
        ADMIN_USER_ID = int(ADMIN_USER_ID)
    except ValueError:
        logger.error("ADMIN_USER_ID must be an integer if set. Broadcast feature will be restricted.")
        ADMIN_USER_ID = None

LOG_CHANNEL_ID = os.getenv("LOG_CHANNEL_ID") # New: Channel for logging user details
if LOG_CHANNEL_ID:
    try:
        LOG_CHANNEL_ID = int(LOG_CHANNEL_ID)
    except ValueError:
        logger.error("LOG_CHANNEL_ID must be an integer if set. User logging to channel disabled.")
        LOG_CHANNEL_ID = None


# Configure Google Gemini API
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
else:
    logger.error("GEMINI_API_KEY not set. Gemini functionality will be disabled.")
    model = None

# Initialize Flask app
app = Flask(__name__)

# Initialize python-telegram-bot Application
if not TELEGRAM_BOT_TOKEN:
    logger.critical("TELEGRAM_BOT_TOKEN is not set. Bot cannot run.")
    application = None
else:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# --- User ID Storage for Broadcast ---
USER_CHATS_FILE = "user_chats.txt" # File to store chat IDs

def add_user_chat_id(chat_id: int):
    """Adds a unique chat ID to the storage file."""
    try:
        with open(USER_CHATS_FILE, "a+") as f:
            f.seek(0)
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
    if not LOG_CHANNEL_ID:
        logger.debug("LOG_CHANNEL_ID not set. Skipping user activity logging to channel.")
        return

    user_info = (
        f"<b>User Activity Log</b>\n"
        f"<b>User ID:</b> <code>{user.id}</code>\n"
        f"<b>Name:</b> {user.full_name or 'N/A'}\n"
    )
    if user.username:
        user_info += f"<b>Username:</b> @{user.username}\n"
        user_info += f"<b>Profile Link:</b> <a href='tg://user?id={user.id}'>Link to Profile</a>\n" # This link works inside Telegram
    else:
        user_info += f"<b>Username:</b> N/A (no public username)\n"

    user_info += (
        f"<b>Language Code:</b> {user.language_code or 'N/A'}\n"
        f"<b>Activity:</b> {activity_type}\n"
    )
    if message_text:
        user_info += f"<b>Message:</b> <code>{message_text[:200]}</code>" # Log first 200 chars of message

    try:
        await bot.send_message(
            chat_id=LOG_CHANNEL_ID,
            text=user_info,
            parse_mode="HTML"
        )
        logger.info(f"Logged {activity_type} for user {user.id} to channel {LOG_CHANNEL_ID}")
    except Exception as e:
        logger.error(f"Failed to send log to channel {LOG_CHANNEL_ID} for user {user.id}: {e}")

# --- Custom Start Message with Image and Buttons ---
async def start(update: Update, context: CallbackContext) -> None:
    """Sends a custom start message with an image and multiple buttons."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    add_user_chat_id(chat_id) # Store user chat ID
    
    # Log user activity to channel
    if application: # Ensure application.bot is available
        await log_user_activity(application.bot, user, "Start Command")

    welcome_message = (
        f"Hello, {user.first_name}! 👋\n\n"
        "I'm your friendly AI assistant, powered by Google Gemini. "
        "I can chat with you about almost anything. Just send me a message!\n\n"
        "Here are some useful links:"
    )

    keyboard = [
        [
            InlineKeyboardButton("Visit My Website", url="https://example.com"),
            InlineKeyboardButton("Follow on Twitter", url="https://twitter.com/your_handle"),
        ],
        [
            InlineKeyboardButton("Join Our Community", url="https://t.me/your_community_channel"),
            InlineKeyboardButton("Support Me", url="https://buymeacoffee.com/your_profile"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        with open("start_image.jpg", "rb") as photo_file:
            await update.message.reply_photo(
                photo=photo_file,
                caption=welcome_message,
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
        logger.info(f"Sent start message with image to {user.first_name}")
    except FileNotFoundError:
        logger.warning("start_image.jpg not found. Sending text message instead.")
        await update.message.reply_text(
            f"{welcome_message}\n\n"
            "*(Image not found. Please ensure 'start_image.jpg' is in the same directory.)*",
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error sending start message: {e}")
        await update.message.reply_text(
            f"{welcome_message}\n\n"
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
    add_user_chat_id(chat_id) # Store user chat ID

    # Log user activity to channel
    if application:
        await log_user_activity(application.bot, user, "Message Received", message_text=user_message)

    if not user_message:
        return

    logger.info(f"Received message from {user.first_name} (ID: {user.id}): {user_message}")

    if REQUIRED_CHANNEL_ID:
        try:
            chat_member = await context.bot.get_chat_member(
                chat_id=REQUIRED_CHANNEL_ID, user_id=user.id
            )
            is_subscribed = chat_member.status in ["member", "administrator", "creator"]
        except Exception as e:
            logger.warning(f"Could not check subscription for {user.first_name} (ID: {user.id}) in channel {REQUIRED_CHANNEL_ID}: {e}")
            is_subscribed = False

        if not is_subscribed:
            if str(REQUIRED_CHANNEL_ID).startswith("-100"):
                channel_link = f"https://t.me/c/{str(REQUIRED_CHANNEL_ID)[4:]}"
                fallback_message = "Please join our private channel to use the bot. Ask an admin for the invite link."
            else:
                channel_link = f"https://t.me/{REQUIRED_CHANNEL_ID}"
                fallback_message = f"Please subscribe to our channel to use the bot: {channel_link}"

            await update.message.reply_text(
                f"🚨 To use this bot, please subscribe to our channel.\n\n"
                f"For public channels: {channel_link}\n"
                f"For private channels: {fallback_message}\n\n"
                "Once subscribed, you can send your message again. Thank you!"
            )
            return

    if not model:
        await update.message.reply_text("AI functionality is currently unavailable. Please check the API key configuration.")
        return

    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        response = model.generate_content(user_message)
        gemini_reply = response.text
        logger.info(f"Gemini responded to {user.first_name}: {gemini_reply[:100]}...")
        await update.message.reply_text(gemini_reply)
    except Exception as e:
        logger.error(f"Error calling Gemini API for {user.first_name}: {e}")
        await update.message.reply_text(
            "I'm sorry, I'm having trouble processing that right now with Gemini. Please try again later."
        )

# --- Broadcast Message Functionality ---
async def broadcast(update: Update, context: CallbackContext) -> None:
    """Sends a message to all users who have interacted with the bot."""
    user = update.effective_user
    
    if ADMIN_USER_ID is None or user.id != ADMIN_USER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        logger.warning(f"Unauthorized broadcast attempt by user ID: {user.id}")
        return

    if not context.args:
        await update.message.reply_text("Usage: /broadcast <your message here>")
        return

    message_to_send = " ".join(context.args)
    all_chat_ids = get_all_user_chat_ids()
    
    # Filter out the admin's own chat ID if it's in the list (optional, but prevents self-broadcast)
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
            await asyncio.sleep(0.05)
        except Exception as e:
            logger.error(f"Failed to send broadcast to chat ID {chat_id}: {e}")
            # Optionally remove this chat_id if errors are persistent (e.g., user blocked bot)
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
        return jsonify({"status": "error", "message": "Bot not initialized due to missing token."}), 500

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
        await update.message.reply_text("Bot not initialized. Cannot set webhook.")
        return

    if not WEBHOOK_URL:
        await update.message.reply_text("WEBHOOK_URL is not set in environment variables. Cannot set webhook.")
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

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setwebhook", set_webhook_command))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    logger.info(f"Starting Flask app on port {PORT}...")
    app.run(host="0.0.0.0", port=PORT, debug=False)


if __name__ == "__main__":
    main()
