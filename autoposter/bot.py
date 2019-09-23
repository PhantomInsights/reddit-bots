"""
Takes the top 3 Google News and posts them to Reddit.
"""

import xml.etree.ElementTree as ET

import praw
import requests

import config

LOG_FILE = "./processed_urls.txt"
NEWS_URL = "https://news.google.com/rss/search?q=ecatepec&hl=es-419&gl=MX&ceid=MX:es-419"


def load_log():
    """Loads the log file and creates it if it doesn't exist.

    Returns
    -------
    list
        A list of urls.

    """

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as temp_file:
            return temp_file.read().splitlines()

    except FileNotFoundError:
        with open(LOG_FILE, "w", encoding="utf-8") as temp_file:
            return []


def update_log(url):
    """Updates the log file.

    Parameters
    ----------
    url : str
        The url to log.

    """

    with open(LOG_FILE, "a", encoding="utf-8") as temp_file:
        temp_file.write(url + "\n")


def init_bot():
    """Reads the RSS feed."""

    # We create the Reddit instance.
    reddit = praw.Reddit(client_id=config.APP_ID, client_secret=config.APP_SECRET,
                         user_agent=config.USER_AGENT, username=config.REDDIT_USERNAME,
                         password=config.REDDIT_PASSWORD)

    with requests.get(NEWS_URL) as response:

        root = ET.fromstring(response.text)

        # Only read first 3 links.
        for item in root.findall(".//item")[0:3]:
            
            log = load_log()

            title = item.find("title").text.split(" - ")[0].strip()
            url = item.find("link").text

            if url not in log and title not in log:

                reddit.subreddit(config.SUBREDDIT).submit(
                    title=title, url=url)

                update_log(url)
                update_log(title)
                print("Posted:", url)


if __name__ == "__main__":

    init_bot()
