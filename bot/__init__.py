import os
import logging
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageFilter

# Prevent unauthorised access to the bot
class OwnerFilter(MessageFilter):
    def filter(self, message):
        return bool(message.from_user.id == OWNER_ID)
owner_filter = OwnerFilter()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
LOGGER = logging.getLogger(__name__)

# Environment Variables
def getConfig(name: str):
    return os.environ[name]
load_dotenv('config.env')

try:
    BOT_TOKEN = getConfig('BOT_TOKEN')
    OWNER_ID = int(getConfig('OWNER_ID'))
    CHAT_ID = getConfig('CHAT_ID')
    DELAY = int(getConfig('DELAY'))
    DATABASE_URL = getConfig('DATABASE_URL')
    if len(DATABASE_URL) == 0:
        raise KeyError
except KeyError as e:
    LOGGER.error("One or more env variables are missing! Exiting now.")
    exit(1)
try:
    CUSTOM_MESSAGES = getConfig('CUSTOM_MESSAGES')
except:
    pass

updater = Updater(token=BOT_TOKEN, use_context=True)