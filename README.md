<p align="center"><img src="https://raw.githubusercontent.com/hyPnOtICDo0g/rss-chan/master/images/rss-chan.png" width="300"></a></p> 

<h4 align="center">A telegram RSS feed reader bot, made in python using feedparser.</h4>

<p align="center">
<a href="https://github.com/hyPnOtICDo0g/rss-chan/blob/master/LICENSE" alt="GitHub"><img src="https://img.shields.io/badge/License-GPLv3-blue.svg" ></a>
<a alt="GitHub repo size"><img src="https://img.shields.io/github/repo-size/hyPnOtICDo0g/rss-chan"></a>
<a href="https://github.com/hyPnOtICDo0g/rss-chan/stargazers" alt="GitHub stars"><img src="https://img.shields.io/github/stars/hyPnOtICDo0g/rss-chan?style=social" ></a>
<a href="https://github.com/hyPnOtICDo0g/rss-chan/network/members" alt="GitHub forks"><img src="https://img.shields.io/github/forks/hyPnOtICDo0g/rss-chan?style=social" ></a>
<hr>


# About

A self-hosted telegram bot that dumps posts from RSS feeds to a telegram chat.  

I decided to go with [BoKKeR](https://github.com/BoKKeR)'s repo as a base for my modifications, since he had already implemented the basic logic for parsing & sending feeds.

The (heavily) modified code addresses a few issues in his repo with some new features of my own. Head over to the [changelog]() section for more.

# Deploy

Instructions to deploy the bot to **Heroku**/locally resides in the [wiki]().

# Usage

The bot uses a `Title <-> URL` mechanism so that the user doesn't have to mess with the feed **URL** every-time, instead use a **Title** to perform a task.

>**Commands**:  
>• **/help**: To get the help message  
• **/list**: List your subscriptions  
• **/get** Title 10: Force fetch last n feed(s)  
• **/sub** Title https://www.rss-url.com: Subscribe to a RSS feed  
• **/unsub** Title: Removes the RSS subscription corresponding to it's title  
• **/unsuball**: Removes all subscriptions  

# Credits

Projects used in the making:

* [feedparser](https://github.com/kurtmckee/feedparser)
* [psycopg2](https://github.com/psycopg/psycopg2)
* [python-dotenv](https://github.com/theskumar/python-dotenv)
* [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
* [RSS-to-Telegram-Bot](https://github.com/BoKKeR/RSS-to-Telegram-Bot)

Others:

* Repo logo [Designed by mamewmy / Freepik](https://www.freepik.com/free-vector/young-girl-thinking-face-wondering-cartoon-illustration_11652601.htm)
* RSS logo made by [Freepik](https://www.freepik.com) from [Flaticon](www.flaticon.com)