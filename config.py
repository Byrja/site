import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Token - loaded from environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Data files
USER_DATA_FILE = "user_data.json"
USER_STATES_FILE = "user_states.json"