import os
import logging

import feedparser
from dotenv import load_dotenv

import psycopg2
from psycopg2 import Error

from telegram import Bot
from telegram.error import BadRequest
from telegram.ext import Updater, CommandHandler, MessageFilter

rss_dict = {}
load_dotenv('config.env')
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
LOGGER = logging.getLogger(__name__)

# Environment Variables
def getConfig(name: str):
    return os.environ[name]

try:
    BOT_TOKEN = getConfig('BOT_TOKEN')
    OWNER_ID = int(getConfig('OWNER_ID'))
    CHAT_ID = getConfig('CHAT_ID')
    DELAY = int(getConfig('DELAY'))
    DATABASE_URL = getConfig('DATABASE_URL')
    if len(DATABASE_URL) == 0:
        raise KeyError
except KeyError as e:
    LOGGER.error("One or more env variables missing! Exiting now.")
    exit(1)
try:
    CUSTOM_MESSAGES = getConfig('CUSTOM_MESSAGES')
except:
    pass

# Bot Commands
bot = Bot(BOT_TOKEN)
botcmds = [
        (f'help','To get this message'),
        (f'list','List your subscriptions'),
        (f'get','Force fetch last n item(s)'),
        (f'sub','Subscribe to a RSS feed'),
        (f'unsub','Remove a specific subscription'),
        (f'unsuball','Remove all subscriptions')
    ]

# Prevent unauthorised access to the bot
class OwnerFilter(MessageFilter):
    def filter(self, message):
        return bool(message.from_user.id == OWNER_ID)
owner_filter = OwnerFilter()

# Database Operations
class PostgreSQL():
    def connect(self):
        try:
            self.conn = psycopg2.connect(DATABASE_URL)
            self.cur = self.conn.cursor()
        except psycopg2.DatabaseError as error:
            LOGGER.error(error)

    def disconnect(self):
        self.conn.commit()
        self.cur.close()
        self.conn.close()

    def init(self):
        try:
            self.connect()
            self.cur.execute("CREATE TABLE rss (name text, link text, last text, title text)")
            self.disconnect()
            LOGGER.info("Database Created.")
        except psycopg2.errors.DuplicateTable:
            LOGGER.info("Database already exists.")
            rss_load()

    def load_all(self):
        self.connect()
        self.cur.execute("SELECT * FROM rss")
        rows = self.cur.fetchall()
        self.disconnect()
        return rows

    def write(self, name, link, last, title):
        self.connect()
        q = [(name), (link), (last), (title)]
        self.cur.execute("INSERT INTO rss (name, link, last, title) VALUES(%s, %s, %s, %s)", q)
        self.disconnect()
        rss_load()

    def update(self, last, name, title):
        self.connect()
        q = [(last), (title), (name)]
        self.cur.execute("UPDATE rss SET last=%s, title=%s WHERE name=%s", q)
        self.disconnect()

    def find(self, q):
        self.connect()
        # check the database for the latest feed
        self.cur.execute("SELECT link FROM rss WHERE name = %s", q)
        feed_url = self.cur.fetchone()
        self.disconnect()
        return feed_url

    def delete(self, q):
        try:
            self.connect()
            self.cur.execute("DELETE FROM rss WHERE name = %s", q)
            self.disconnect()
        except psycopg2.errors.UndefinedTable:
            pass
        rss_load()

    def deleteall(self):
        self.connect()
        # clear database & dictionary
        self.cur.execute("TRUNCATE TABLE rss")
        self.disconnect()
        rss_dict.clear()
        LOGGER.info('Database deleted.')
postgres = PostgreSQL()

# RSS Operations
def rss_load():
    # if the dict is not empty, empty it.
    if bool(rss_dict):
        rss_dict.clear()

    for row in postgres.load_all():
        rss_dict[row[0]] = (row[1], row[2], row[3])

def cmd_rss_start(update, context):
    if owner_filter(update):
        update.effective_message.reply_text(f"Send me a link to a RSS feed.\nUse /help for further instructions.")
    else:
        update.effective_message.reply_text("Oops! not an Authorized user.")
        LOGGER.info('UID: {} - UN: {} - MSG: {}'.format(update.message.chat.id, update.message.chat.username, update.message.text))

def cmd_rsshelp(update, context):
    help_string=f"""
<b>Commands:</b>
• /help: <i>To get this message</i>
• /list: <i>List your subscriptions</i>
• /get Title 10: <i>Force fetch last n item(s)</i>
• /sub Title https://www.rss-url.com: <i>Subscribe to a RSS feed</i>
• /unsub Title: <i>Removes the RSS subscription corresponding to it's title</i>
• /unsuball: <i>Removes all subscriptions</i>
"""
    update.effective_message.reply_text(help_string, parse_mode='HTMl')

def cmd_rss_list(update, context):
    if bool(rss_dict) is False:
        update.effective_message.reply_text("No subscriptions.")
    else:
        list_feed = ""
        for title, url_list in rss_dict.items():
            list_feed +=f"Title: {title}\nFeed: {url_list[0]}\n\n"
        update.effective_message.reply_text(f"<b>Your subscriptions:</b>\n\n" + list_feed, parse_mode='HTMl')

def cmd_get(update, context):
    try:
        count = int(context.args[1])
        q = (context.args[0],)
        feed_url = postgres.find(q)
        if feed_url != None and count > 0:
            try:
                item_info = ""
                msg = update.effective_message.reply_text(f"Getting the last <b>{count}</b> item(s), please wait!", parse_mode='HTMl')
                rss_d = feedparser.parse(feed_url[0])
                for item_num in range(count):
                    item_info +=f"<b>{rss_d.entries[item_num]['title']}</b>\n{rss_d.entries[item_num]['link']}\n\n"
                msg.edit_text(item_info, parse_mode='HTMl')
            except (IndexError, BadRequest):
                msg.edit_text("Parse depth exceeded. Try again with a lower value.", parse_mode='HTMl')
        else:
            update.effective_message.reply_text("Enter a vaild title/value.")
    except (IndexError, ValueError):
        update.effective_message.reply_text("Please use this format to fetch:\n/get Title 10", parse_mode='HTMl')

def cmd_rss_sub(update, context):
    # try if there are 2 arguments passed
    try:
        context.args[1]
    except IndexError:
        update.effective_message.reply_text(f"Please use this format to add:\n/sub Title https://www.rss-url.com", parse_mode='HTMl')
    else:
        sub_feed = ""
        try:
            # try if the url is a valid RSS feed
            rss_d = feedparser.parse(context.args[1])
            rss_d.entries[0]['title']
            title_rss =  f"<b>{rss_d.feed.title}</b> latest record:\n<b>{rss_d.entries[0]['title']}</b>\n{rss_d.entries[0]['link']}"
            postgres.write(context.args[0], context.args[1], str(rss_d.entries[0]['link']), str(rss_d.entries[0]['title']))
            sub_feed = f"<b>Subscribed!</b>\nTitle: {context.args[0]}\nFeed: {context.args[1]}"
            update.effective_message.reply_text(sub_feed, parse_mode='HTMl')
            update.effective_message.reply_text(title_rss, parse_mode='HTMl')
        except IndexError:
            update.effective_message.reply_text("The link doesn't seem to be a RSS feed or it's not supported!")

def cmd_rss_unsub(update, context):
    try:
        q = (context.args[0],)
        postgres.delete(q)
        update.effective_message.reply_text("If it exists in the database, it'll be removed.")
    except IndexError:
        update.effective_message.reply_text(f"Please use this format to remove:\n/unsub Title", parse_mode='HTMl')

def cmd_rss_unsuball(update, context):
    if rss_dict != {}:
        postgres.deleteall()
        update.effective_message.reply_text("Deleted all subscriptions.")
    else:
        update.effective_message.reply_text("No subscriptions.")

def init_feeds():
    for name, url_list in rss_dict.items():
        try:
            rss_d = feedparser.parse(url_list[0])
            postgres.update(str(rss_d.entries[0]['link']), name, str(rss_d.entries[0]['title']))
            LOGGER.info("Feed name: "+ name)
            LOGGER.info("Latest feed item: "+ rss_d.entries[0]['link'])
        except IndexError:
            LOGGER.info(f"There was an error while parsing this feed: {url_list[0]}")
            continue
    rss_load()
    LOGGER.info('Initiated feeds.')

def rss_monitor(context):
    for name, url_list in rss_dict.items():
        try:
            feed_info = ""
            # check whether the URL & title of the latest item is in the database
            rss_d = feedparser.parse(url_list[0])
            if (url_list[1] != rss_d.entries[0]['link'] and url_list[2] != rss_d.entries[0]['title']):
                feed_count = 0
                feed_titles = []
                feed_urls = []
                # check until a new item pops up
                while (url_list[1] != rss_d.entries[feed_count]['link'] and url_list[2] != rss_d.entries[feed_count]['title']):
                    feed_titles.insert(0, rss_d.entries[feed_count]['title'])
                    feed_urls.insert(0, rss_d.entries[feed_count]['link'])
                    feed_count += 1
                for x in range(len(feed_urls)):
                    feed_info = f"{CUSTOM_MESSAGES}\n<b>{feed_titles[x]}</b>\n{feed_urls[x]}"
                    context.bot.send_message(CHAT_ID, feed_info, parse_mode='HTMl')
                # overwrite the existing item with the latest item
                postgres.update(str(rss_d.entries[0]['link']), name, str(rss_d.entries[0]['title']))
        except IndexError:
            LOGGER.info(f"There was an error while parsing this feed: {url_list[0]}")
            continue
        else:
            LOGGER.info("Feed name: "+ name)
            LOGGER.info("Latest feed item: "+ rss_d.entries[0]['link'])
    rss_load()
    LOGGER.info('Database Updated.')

def main():

    updater = Updater(token=BOT_TOKEN, use_context=True)
    job_queue = updater.job_queue
    dp = updater.dispatcher
    bot.set_my_commands(botcmds)

    dp.add_handler(CommandHandler("start", cmd_rss_start))
    dp.add_handler(CommandHandler("help", cmd_rsshelp, filters=owner_filter))
    dp.add_handler(CommandHandler("list", cmd_rss_list, filters=owner_filter))
    dp.add_handler(CommandHandler("get", cmd_get, filters=owner_filter))
    dp.add_handler(CommandHandler("sub", cmd_rss_sub, filters=owner_filter))
    dp.add_handler(CommandHandler("unsub", cmd_rss_unsub, filters=owner_filter))
    dp.add_handler(CommandHandler("unsuball", cmd_rss_unsuball, filters=owner_filter))

    postgres.init()
    init_feeds()

    job_queue.run_repeating(rss_monitor, DELAY)

    updater.start_polling()
    updater.idle()
    conn.close()

if __name__ == '__main__':
    main()