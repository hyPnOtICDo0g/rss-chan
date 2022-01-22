import feedparser
from bot import updater, owner_filter, LOGGER, CHAT_ID, DELAY, CUSTOM_MESSAGES
from .dbhandler import postgres, rss_dict
from .utilhandler import utilities

from telegram.error import BadRequest
from telegram.ext import CommandHandler

# RSS Operations
def cmd_start(update, context):
    if owner_filter(update):
        update.effective_message.reply_text("Send me a link to a RSS feed.\nUse /help for further instructions.")
    else:
        update.effective_message.reply_text("Oops! not an Authorized user.")
        LOGGER.info('UID: {} - UN: {}'.format(update.message.chat.id, update.message.chat.username))

# displays the help message
def cmd_help(update, context):
    update.effective_message.reply_text(
        f'<b>Commands:</b>\n'
        f'• /help: <i>To get this message</i>\n'
        f'• /list: <i>List your subscriptions</i>\n'
        f'• /get TITLE 10: <i>Force fetch last n item(s)</i>\n'
        f'• /sub TITLE https://www.rss-url.com/feed: <i>Subscribe to a RSS feed</i>\n'
        f'• /unsub TITLE: <i>Removes the RSS subscription corresponding to it\'s title</i>\n'
        f'• /unsuball: <i>Removes all subscriptions</i>\n'
        f'• /template TITLE TEMPLATE: <i>Set a template to a specific RSS feed</i>\n',
            parse_mode='html'
    )


# lists subscribed feeds
def cmd_list(update, context):
    if bool(rss_dict):
        list_feed = "<b>Your subscriptions:</b>\n\n"+"".join(
            f"Title: <b>{title}</b>\nFeed: {feed_items[0]}\nTemplate: <b>{feed_items[3]}</b>\n\n"
            for title, feed_items in rss_dict.items()
        )
        update.effective_message.reply_text(list_feed, parse_mode='html')
    else:
        update.effective_message.reply_text("No subscriptions.")


# force fetches feed items of a RSS feed
def cmd_get(update, context):
    try:
        count = int(context.args[1])
        feed_url = postgres.find_one('link', (context.args[0],))
        if feed_url is not None and count > 0:
            try:
                msg = update.effective_message.reply_text(f"Getting <b>{count}</b> latest item(s), please wait!", parse_mode='html')
                rss_d = feedparser.parse(feed_url[0])
                rss_t = postgres.find_one('template', (context.args[0],))[0]
                item_info = "".join(
                    utilities.format_items(rss_d, item_num, rss_t)[1]+'\n\n'
                    for item_num in range(count)
                )
                msg.edit_text(item_info, parse_mode='html', disable_web_page_preview=True)
            except (IndexError, BadRequest):
                msg.edit_text("Parse depth exceeded. Try again with a lower value.")
        else:
            update.effective_message.reply_text("Enter a vaild title/value.")
    except (IndexError, ValueError):
        update.effective_message.reply_text('Please use this format to fetch:\n/get Title 10',
            parse_mode='html')


# validates and subscribes or updates a RSS feed
def cmd_sub(update, context):
    # try if there are two arguments passed
    try:
        context.args[1]
        # check if a given feed link already exists in the database
        if context.args[1] not in postgres.find_all('link'):
            try:
                rss_d = feedparser.parse(context.args[1])
                # try if the url is a valid RSS feed
                rss_d.entries[0]['title']
                # check if the given title already exists in the database
                if postgres.find_one('name', (context.args[0],)) is None:
                    postgres.write(
                        context.args[0], context.args[1],
                        rss_d.entries[0]['link'], rss_d.entries[0]['title'],
                        "item_name|new_line|item_link"
                    )

                    update.effective_message.reply_text(
                        f'<b>Subscribed!</b>\nTitle: {context.args[0]}\nFeed: {context.args[1]}',
                            parse_mode='html'
                    )
                else:
                    # update the feed URL & latest feed item
                    update.effective_message.reply_text("Feed URL updated.")
                    postgres.update_items(
                        context.args[1],  rss_d.entries[0]['link'],
                        context.args[0], rss_d.entries[0]['title']
                    )
                    postgres.rss_load()

                update.effective_message.reply_text(
                    f'<b>{rss_d.feed.title}</b> latest record:\n'
                    f'<b>{rss_d.entries[0]["title"]}</b>\n{rss_d.entries[0]["link"]}',
                        parse_mode='html', disable_web_page_preview=True
                )
            except IndexError:
                update.effective_message.reply_text("The link doesn't seem to be a RSS feed or it's region-blocked!")
        else:
            update.effective_message.reply_text("Existing URL found. Try again with an unique one.")
    except IndexError:
        update.effective_message.reply_text('Please use this format to add:\n/sub Title https://www.rss-url.com/feed',
            parse_mode='html')


# sets a template based on the keys available
def cmd_template(update, context):
    try:
        # check if a given title/template exists in the database
        if(postgres.find_one('name', (context.args[0],)) != None and postgres.find_one('template', (context.args[0],))[0] != context.args[1]):
            frmt = utilities.format_items(
                        feedparser.parse(postgres.find_one('link', (context.args[0],))[0]),
                        0,
                        context.args[1]
                    )
            # check if a given string is a valid template
            try:
                update.effective_message.reply_text(
                    f"<b>Template updated.</b> Your feed messages will look like:\n\n{frmt[1]}",
                    parse_mode='html',
                    disable_web_page_preview=True
                )
                postgres.update_one('template', (context.args[1], context.args[0]))
            except IndexError:
                update.effective_message.reply_text(frmt[0])
        else:
            update.effective_message.reply_text("Enter a valid title or a different template.")
    except IndexError:
        update.effective_message.reply_text(
            f'<b>Template Keys available:</b>\n\n'
            f'• <b>feed_name</b> - <i>RSS feed Name</i>\n'
            f'• <b>feed_link</b> - <i>RSS feed URL</i>\n'
            f'• <b>item_name</b> - <i>Feed item name</i>\n'
            f'• <b>item_link</b> - <i>Feed item URL</i>\n'
            f'• <b>item_description</b> - <i>Feed item description</i>\n'
            f'• <b>item_enclosures</b> - <i>Feed item enclosure URL</i>\n'
            f'• <b>white_space</b> - <i>A space character</i>\n'
            f'• <b>tab_space</b> - <i>A tab character</i>\n'
            f'• <b>new_line</b> - <i>A new line character</i>\n\n'
            f'<b>Usage</b>: <i>Each key must be separated by a <b>|</b></i>\n'
            f'<b>E.g. template</b>: <i>item_name|new_line|item_link</i>\n\n'
            f'<b>Formatted Feed</b>:\n\n<b>This is a sample item name.</b>\nhttps://www.rss-url.com/item\n\n',
                parse_mode='html'
        )

# deletes a specific RSS feed from the database
def cmd_unsub(update, context):
    try:
        postgres.delete((context.args[0],))
        update.effective_message.reply_text("If it exists in the database, it'll be removed.")
    except IndexError:
        update.effective_message.reply_text("Please use this format to remove:\n/unsub Title", parse_mode='html')


# clears the dict & resets the database
def cmd_unsuball(update, context):
    if bool(rss_dict):
        postgres.deleteall()
        update.effective_message.reply_text("Deleted all subscriptions.")
    else:
        update.effective_message.reply_text("No subscriptions.")

# writes the latest feed item to the database when deployed to prevent feed spam
def init_feeds():
    for name, feed_items in rss_dict.items():
        try:
            rss_d = feedparser.parse(feed_items[0])
            """
            updating the database with the feed URL is not required here.
            when a subscription is updated using the cmd_sub(), the feed properties
            have to be written to the database which contains three arguments.
            rather than writing a specific function, modifying update_items()
            seemed a bit less bloated.
            """
            postgres.update_items(feed_items[0], rss_d.entries[0]['link'], name, rss_d.entries[0]['title'])
            LOGGER.info(f"Feed name: {name} | Latest feed item: {rss_d.entries[0]['link']}")
        except IndexError:
            LOGGER.error(f"There was an error while parsing this feed: {feed_items[0]}")
            continue
    postgres.rss_load()
    LOGGER.info('Initiated feeds.')


# monitors new feed items and dumps them to a telegram chat
def rss_monitor(context):
    for name, feed_items in rss_dict.items():
        try:
            rss_d = feedparser.parse(feed_items[0])
            # check whether the latest item is present in the database
            if(feed_items[1] != rss_d.entries[0]['link'] and feed_items[2] != rss_d.entries[0]['title']):
                feed_count = 0
                feed_list = []
                # check until a new item pops up
                while(feed_items[1] != rss_d.entries[feed_count]['link'] and feed_items[2] != rss_d.entries[feed_count]['title']):
                    feed_list.insert(0, f'{CUSTOM_MESSAGES}\n'+utilities.format_items(rss_d, feed_count, feed_items[3])[1])
                    feed_count += 1
                for feed in feed_list:
                    context.bot.send_message(CHAT_ID, feed, parse_mode='html', disable_web_page_preview=True)
                # overwrite the existing item with the latest item
                postgres.update_items(feed_items[0], rss_d.entries[0]['link'], name, rss_d.entries[0]['title'])
        except IndexError:
            LOGGER.error(f"There was an error while parsing this feed: {feed_items[0]}")
            continue
        else:
            LOGGER.info(f"Feed name: {name} | Latest feed item: {rss_d.entries[0]['link']}")
    postgres.rss_load()
    LOGGER.info('Database Updated.')


def rss_init():
    job_queue = updater.job_queue
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", cmd_start))
    dp.add_handler(CommandHandler("help", cmd_help, filters=owner_filter))
    dp.add_handler(CommandHandler("list", cmd_list, filters=owner_filter))
    dp.add_handler(CommandHandler("get", cmd_get, filters=owner_filter))
    dp.add_handler(CommandHandler("template", cmd_template, filters=owner_filter))
    dp.add_handler(CommandHandler("sub", cmd_sub, filters=owner_filter))
    dp.add_handler(CommandHandler("unsub", cmd_unsub, filters=owner_filter))
    dp.add_handler(CommandHandler("unsuball", cmd_unsuball, filters=owner_filter))

    postgres.init()
    init_feeds()

    job_queue.run_repeating(rss_monitor, DELAY)
