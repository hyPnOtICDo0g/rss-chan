import os
from pathlib import Path

import feedparser
import logging
from dotenv import load_dotenv

import psycopg2
from psycopg2 import Error

from telegram import Bot
from telegram.ext import Updater, CommandHandler, MessageFilter

# Init 

rss_dict = {}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
LOGGER = logging.getLogger(__name__)

# Prevent unauthorised access to the bot

class OwnerFilter(MessageFilter):
    def filter(self, message):
        return bool(message.from_user.id == OWNER_ID)

owner_filter = OwnerFilter()

# Config

load_dotenv('config.env')

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
    INIT_FEEDS = getConfig('INIT_FEEDS')    
    CUSTOM_MESSAGES = getConfig('CUSTOM_MESSAGES')    
except:
    pass


# Bot Commands

bot = Bot(BOT_TOKEN)
botcmds = [
        (f'help','To get this message'),
        (f'list','List your subscriptions'),
        (f'get','Force fetch last n feed(s)'),
        (f'sub','Subscribe to a RSS feed'),
        (f'unsub','Remove a specific subscription'),
        (f'unsuball','Remove all subscriptions')
    ]  

# Postgresql

def init_postgres():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        c = conn.cursor()
        c.execute("CREATE TABLE rss (name text, link text, last text)")
        conn.commit()
        conn.close()
        LOGGER.info("Database Created.")
    except psycopg2.errors.DuplicateTable:
        LOGGER.info("Database already exists.")
        rss_load()

def postgres_load_all():
    conn = psycopg2.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute("SELECT * FROM rss")
    rows = c.fetchall()
    conn.close()
    return rows

def postgres_write(name, link, last):
    conn = psycopg2.connect(DATABASE_URL)
    c = conn.cursor()
    q = [(name), (link), (last)]
    c.execute("INSERT INTO rss (name, link, last) VALUES(%s, %s, %s)", q)
    conn.commit()
    conn.close()
    rss_load()

def postgres_update(last, name):
    conn = psycopg2.connect(DATABASE_URL)
    c = conn.cursor()
    q = [(last), (name)]
    c.execute("UPDATE rss SET last=%s WHERE name=%s", q)
    conn.commit()
    conn.close()

def postgres_find(q):
    conn = psycopg2.connect(DATABASE_URL)
    c = conn.cursor()
    # check the database for the latest feed
    c.execute("SELECT link FROM rss WHERE name = %s", q)
    feedurl = c.fetchone()
    conn.close()
    return feedurl

def postgres_delete(q):
    conn = psycopg2.connect(DATABASE_URL)
    c = conn.cursor()
    try:
        c.execute("DELETE FROM rss WHERE name = %s", q)
        conn.commit()
        conn.close()
    except psycopg2.errors.UndefinedTable:
        pass
    rss_load()

def postgres_deleteall():
    # clear database & dictionary
    conn = psycopg2.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute("TRUNCATE TABLE rss")
    conn.commit()
    conn.close()
    rss_dict.clear()
    LOGGER.info('Database deleted.')
    

# RSS

def rss_load():
    # if the dict is not empty, empty it.
    if bool(rss_dict):
        rss_dict.clear()

    for row in postgres_load_all():
        rss_dict[row[0]] = (row[1], row[2])

def cmd_rss_start(update, context):
    if owner_filter(update):
        update.effective_message.reply_text(f"Send me a link to a RSS feed.\nUse /help for further instructions.")
    else:
        update.effective_message.reply_text("Oops! not a Authorized user.")
        LOGGER.info('UID: {} - UN: {} - MSG: {}'.format(update.message.chat.id, update.message.chat.username, update.message.text))

def cmd_rsshelp(update, context):
    help_string=f"""
<b>Commands:</b> 
• /help: <i>To get this message</i>
• /list: <i>List your subscriptions</i>
• /get Title 10: <i>Force fetch last n feed(s)</i>
• /sub Title https://www.rss-url.com: <i>Subscribe to a RSS feed</i>
• /unsub Title: <i>Removes the RSS subscription corresponding to it's title</i>
• /unsuball: <i>Removes all subscriptions</i>
"""
    update.effective_message.reply_text(help_string, parse_mode='HTMl')

def cmd_rss_list(update, context):
    listfeed = ""
    if bool(rss_dict) is False:
        update.effective_message.reply_text("No subscriptions.")
    else:
        for title, url_list in rss_dict.items():
            listfeed +=f"Title: {title}\nFeed: {url_list[0]}\n\n"
        update.effective_message.reply_text(f"<b>Your subscriptions:</b>\n\n" + listfeed, parse_mode='HTMl')

def cmd_get(update, context):
    try:
        count = context.args[1]
        q = (context.args[0],)
        feedurl = postgres_find(q)
        if  feedurl != None:
            feedinfo = ""
            try:
                if int(context.args[1]) > 0:
                    feed_num = int(context.args[1])
                else:
                    raise Exception  
            except (ValueError, Exception):
                update.effective_message.reply_text("Enter a value > 0.")
                LOGGER.error("You trolling? Study Math doofus.")
            else:
                msg = update.effective_message.reply_text(f"Getting the last <b>{count}</b> feed(s), please wait!", parse_mode='HTMl')
                for num_feeds in range(feed_num):
                    rss_d = feedparser.parse(feedurl[0])
                    feedinfo +=f"<b>{rss_d.entries[num_feeds]['title']}</b>\n{rss_d.entries[num_feeds]['link']}\n\n"
                msg.edit_text(feedinfo, parse_mode='HTMl')    
        else:
            update.effective_message.reply_text("No such feed found.")
    except IndexError:
        update.effective_message.reply_text("Please use this format to fetch:\n/get Title 10", parse_mode='HTMl')

def cmd_rss_sub(update, context):
    addfeed = ""
    # try if there are 2 arguments passed
    try:
        context.args[1]
    except IndexError:
        update.effective_message.reply_text(f"Please use this format to add:\n/sub Title https://www.rss-url.com", parse_mode='HTMl')
    else:
        try:
            # try if the url is a valid RSS feed
            rss_d = feedparser.parse(context.args[1])
            rss_d.entries[0]['title']
            title_rss =  f"<b>{rss_d.feed.title}</b> latest record:\n<b>{rss_d.entries[0]['title']}</b>\n{rss_d.entries[0]['link']}"    
            postgres_write(context.args[0], context.args[1], str(rss_d.entries[0]['link']))
            addfeed = f"<b>Subscribed!</b>\nTitle: {context.args[0]}\nFeed: {context.args[1]}"
            update.effective_message.reply_text(addfeed, parse_mode='HTMl')
            update.effective_message.reply_text(title_rss, parse_mode='HTMl')
        except IndexError:
            update.effective_message.reply_text("The link doesn't seem to be a RSS feed or it's not supported!")

def cmd_rss_unsub(update, context):
    try:
        q = (context.args[0],)        
        postgres_delete(q)
        update.effective_message.reply_text("If it exists in the database, it'll be removed.")
    except IndexError:
        update.effective_message.reply_text(f"Please use this format to remove:\n/unsub Title", parse_mode='HTMl')                

def cmd_rss_unsuball(update, context):
    if rss_dict != {}:
        postgres_deleteall()
        update.effective_message.reply_text("Deleted all subscriptions.")
    else:
        update.effective_message.reply_text("No subscriptions.")

def init_feeds():
    if INIT_FEEDS == "True":
        for name, url_list in rss_dict.items():
            rss_d = feedparser.parse(url_list[0])
            postgres_update(str(rss_d.entries[0]['link']), name)
            LOGGER.info("Feed name: "+ name)
            LOGGER.info("Latest feed url: "+ rss_d.entries[0]['link'])
        rss_load()
        LOGGER.info('Initiated feeds.')

def rss_monitor(context):
    feed_info = ""
    for name, url_list in rss_dict.items():
        feed_count = 0
        feed_titles = []
        feed_urls = []
        # check whether the latest feed's url is in the database
        rss_d = feedparser.parse(url_list[0])
        if (url_list[1] != rss_d.entries[0]['link']):
            # check until a new feed pops up
            while (url_list[1] != rss_d.entries[feed_count]['link']):
                feed_titles.insert(0, rss_d.entries[feed_count]['title'])
                feed_urls.insert(0, rss_d.entries[feed_count]['link'])
                feed_count += 1
            for x in range(len(feed_urls)):
                feed_info = f"{CUSTOM_MESSAGES}\n<b>{feed_titles[x]}</b>\n{feed_urls[x]}"
                context.bot.send_message(CHAT_ID, feed_info, parse_mode='HTMl')
        # overwrite the existing feed with the latest feed
        postgres_update(str(rss_d.entries[0]['link']), name)
        LOGGER.info("Feed name: "+ name)
        LOGGER.info("Latest feed url: "+ rss_d.entries[0]['link'])
    rss_load()
    LOGGER.info('Database Loaded.')

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

    init_postgres()
    init_feeds()

    job_queue.run_repeating(rss_monitor, DELAY)

    updater.start_polling()
    updater.idle()
    conn.close()

if __name__ == '__main__':
    main()