# Reddit Bots

This repository contains a collection of Reddit bots that I use to enhance my subreddits.

These bots have a few things in common, they all run on a `Raspberry Pi`, are scheduled with `crontab` and use the same config.py file.

Each bot is separated into their own folder. Feel free to rearrange them as you need.

To prevent duplicate actions most bots keep a local log of their actions in a .txt file.

## Requirements

Python 3 is used to develop and test all the bots. The bots use the following libraries.

* BeautifulSoup - Used to perform web scraping.
* PRAW - Makes the use of the REddit API very easy.
* Requests - Used to make GET requests.

## AutoPoster

This bot grabs the top 3 links from a Google News RSS feed and posts them to an specific subreddit.

It is scheduled to run every 6 hours.

`0 */6 * * * cd /home/pi/Documents/autoposter && python3 bot.py`

## FinanceBot

This bot grabs data from 2 websites, the first one it performs web scraping and gets 3 values from each currency pair it requests.

From the other site it reads a JSON feed and applies some light formatting.

This bot works on both old and new Reddit. For old Reddit it updates the sidebar and for new Reddit it updates an specific sidebar text widget.

New Reddit widgets don't show their id's on the API so we need to iterate over all of them until we find the desired one.

A sidebar.txt file is included which can contain your subreddit introduction, rules and other important information. The contents of this file are then appended with a `Markdown` table and a footer.

It is scheduled to run every 3 hours.

`0 */3 * * * cd /home/pi/Documents/financebot && python3 bot.py`

## StickyBot

This bot creates discussion threads, stickies them and after a day it unstickies them.

The bot starts by reading the system arguments which are:

* The file path
* Action - sticky/unsticky
* Day - monday/wednesday/friday

From there it calls the respective function.

I implemented  a simple templating system where the post text is read from a .txt file and then replaces placeholder variables, for example:

template_file.txt

```
Hey there, today is %TODAY% this is some example post.
```

Python code

```python
text = open("template_file.txt").read().replace("%TODAY%", today_variable)
```


Currently there are 3 discussions:

* Monday - This submission contains the 3 top posts from last week. It gets posted and stickied every Monday at 9 am and gets unsticked every Tuesday at 9 pm.
* Wednesday - This submission takes a random politician from a predefined pool and asks the users what they thing about them. It gets posted and stickied every Wednesday at 9 am and gets unsticked every Thursday at 9 pm.
* Friday - Casual discussion. It gets posted and stickied every Friday at 9 am and gets unsticked every Saturday at 9 pm.

```
0 9 * * 1 cd /home/pi/Documents/stickybot && python3 bot.py sticky monday
0 21 * * 2 cd /home/pi/Documents/stickybot && python3 bot.py unsticky monday

0 9 * * 3 cd /home/pi/Documents/stickybot && python3 bot.py sticky wednesday
0 21 * * 4 cd /home/pi/Documents/stickybot && python3 bot.py unsticky wednesday

0 9 * * 5 cd /home/pi/Documents/stickybot && python3 bot.py sticky friday
0 21 * * 6 cd /home/pi/Documents/stickybot && python3 bot.py unsticky friday
```

## Conclusion

Enhancing the features of the subreddits I manage with these bots has been a positive experience for me and their communities.

I hope you find them useful and inspire you to create your own bots. Also feel free to use them on your own subreddits.

[![Become a Patron!](https://c5.patreon.com/external/logo/become_a_patron_button.png)](https://www.patreon.com/bePatron?u=20521425)