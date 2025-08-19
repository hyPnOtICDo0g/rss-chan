import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    BaseFilter,
)

# Load environment variables from config.env
load_dotenv("config.env")

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
LOGGER = logging.getLogger(__name__)

# Load config safely
def getConfig(name: str):
    return os.environ[name]

try:
    BOT_TOKEN = getConfig('BOT_TOKEN')
    OWNER_ID = int(getConfig('OWNER_ID'))
    CHAT_ID = getConfig('CHAT_ID')
    DELAY = int(getConfig('DELAY'))
    DATABASE_URL = getConfig('DATABASE_URL')
    if not DATABASE_URL:
        raise KeyError
except KeyError:
    LOGGER.error("One or more env variables are missing! Exiting now.")
    exit(1)

try:
    CUSTOM_MESSAGES = getConfig('CUSTOM_MESSAGES')
except KeyError:
    CUSTOM_MESSAGES = ""

# Custom Owner Filter using BaseFilter (v20+)
class OwnerFilter(BaseFilter):
    def __call__(self, message):
        return message.from_user and message.from_user.id == OWNER_ID

owner_filter = OwnerFilter()

# Define message handler
async def owner_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello Owner! ✅")

# Start application
app = ApplicationBuilder().token(BOT_TOKEN).build()

# Register handler
app.add_handler(MessageHandler(owner_filter, owner_handler))

# Run polling
if __name__ == "__main__":
    LOGGER.info("Bot is starting...")
    app.run_polling()
