<p align="center"><img src="https://raw.githubusercontent.com/hyPnOtICDo0g/rss-chan/main/images/rss-chan.png" width="250"></a></p>

<h4 align="center">A telegram RSS feed reader bot, made in python using feedparser.</h4>

<p align="center">
<a href="https://github.com/hyPnOtICDo0g/rss-chan/blob/main/LICENSE" alt="GitHub"><img src="https://img.shields.io/badge/License-GPLv3-blue.svg" ></a>
<a alt="GitHub repo size"><img src="https://img.shields.io/github/repo-size/hyPnOtICDo0g/rss-chan"></a>
<a href="https://github.com/hyPnOtICDo0g/rss-chan/stargazers" alt="GitHub stars"><img src="https://img.shields.io/github/stars/hyPnOtICDo0g/rss-chan?style=social" ></a>
<a href="https://github.com/hyPnOtICDo0g/rss-chan/network/members" alt="GitHub forks"><img src="https://img.shields.io/github/forks/hyPnOtICDo0g/rss-chan?style=social" ></a>
<hr>

# About

A self-hosted telegram bot that dumps posts from a RSS feed to a telegram chat.

This project is inspired by [BoKKeR](https://github.com/BoKKeR)'s telegram [bot](https://github.com/BoKKeR/RSS-to-Telegram-Bot) and [ayrat555](https://github.com/ayrat555)'s [el_monitorro](https://github.com/ayrat555/el_monitorro) bot written in Rust.

>**Note**: *The previous version was a complete refactor of BoKKeR's code, which also addresses a couple of issues in his repo with many bug fixes and features of my own. They've been integrated with the current version. Head over to the [changelog](https://github.com/hyPnOtICDo0g/rss-chan/wiki/Changelog) section for more.*

# Deploy

Instructions to deploy to **Heroku** or **self-host** resides in the [wiki](https://github.com/hyPnOtICDo0g/rss-chan/wiki).

# Usage

The bot uses a `TITLE <-> URL` mechanism so that the user doesn't have to mess with the feed **URL** every time, instead use a **TITLE** to perform a task.

>**Commands**:  
>• **/help**: To get the help message  
• **/list**: List your subscriptions  
• **/get** TITLE 10: Force fetch last n item(s)  
• **/sub** TITLE https://www.rss-url.com/feed: Subscribe to a RSS feed  
• **/unsub** TITLE: Removes the RSS subscription corresponding to it's title  
• **/unsuball**: Removes all subscriptions  
• **/template** TITLE TEMPLATE: Set a template to a specific RSS feed

# Credits

Projects used in the making:

* [feedparser](https://github.com/kurtmckee/feedparser)
* [psycopg2](https://github.com/psycopg/psycopg2)
* [python-dotenv](https://github.com/theskumar/python-dotenv)
* [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)

Others:

* Repo logo designed by [mamewmy / Freepik](https://www.freepik.com/free-vector/young-girl-thinking-face-wondering-cartoon-illustration_11652601.htm)
* RSS logo by [Freepik](https://www.freepik.com) from [Flaticon](https://www.flaticon.com/free-icon/rss_1051311)
