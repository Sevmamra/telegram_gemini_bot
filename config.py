import re
from os import getenv, environ



TELEGRAM_BOT_TOKEN = environ.get("TELEGRAM_BOT_TOKEN", "")
LOG_CHANNEL = environ.get("LOG_CHANNEL", "-1002344280987")
ADMIN_USER_ID = environ.get("ADMIN_USER_ID", "7841292070")
REQUIRED_CHANNEL_ID = environ.get("REQUIRED_CHANNEL_ID", "-1002375692750")
LOG_CHANNEL_ID = environ.get("LOG_CHANNEL_ID", "-1002344280987")
GEMINI_API_KEY = environ.get("GEMINI_API_KEY", "AIzaSyBHT9Tv3pyB0xwOKJzGvv1MYi6bvpSwRtA")
WEBHOOK_URL = environ.get("WEBHOOK_URL", "")
