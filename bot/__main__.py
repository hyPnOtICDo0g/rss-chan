from telegram import Bot
from .modules.rsshandler import rss_init
from bot import BOT_TOKEN, updater

def main():
    # Bot Commands
    bot = Bot(BOT_TOKEN)
    botcmds = [
            ('help','To get this message'),
            ('list','List your subscriptions'),
            ('get','Force fetch last n item(s)'),
            ('sub','Subscribe to a RSS feed'),
            ('unsub','Remove a specific subscription'),
            ('unsuball','Remove all subscriptions'),
            ('template', 'Set a template to a specific RSS feed')
        ]
    bot.set_my_commands(botcmds)
    rss_init()

main()
updater.start_polling()
updater.idle()
