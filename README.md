# Reddit Bots

This repository contains a collection of Reddit bots that I use to enhance my subreddits.

These bots have a few things in common, they all run on a `Raspberry Pi`, are scheduled with `crontab` and use the same config.py file.

Each bot is separated into their own folder. Feel free to rearrange them as you need.

To prevent duplicate actions most bots keep a local log of their actions in a .txt file.

## Requirements

Python 3 is used to develop and test all the bots. The bots use the following libraries.

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