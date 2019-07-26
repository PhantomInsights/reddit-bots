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