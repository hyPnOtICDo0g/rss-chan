from telegram import Bot
from .modules.rsshandler import rss_init
from bot import BOT_TOKEN, updater

def main():
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
    bot.set_my_commands(botcmds)
    rss_init()

main()
updater.start_polling()
updater.idle()