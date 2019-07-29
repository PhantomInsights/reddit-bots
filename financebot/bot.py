"""
This bot performs a bit of web scraping to get current values
of several currency pairs and financial instruments.
"""

import time
from datetime import datetime

import praw
import requests
from bs4 import BeautifulSoup

import config

HEADERS = {"User-Agent": "FinanceBot v0.1"}

INVESTING_DICT = {
    "USD/MXN": "https://mx.investing.com/currencies/usd-mxn",
    "EUR/MXN": "https://mx.investing.com/currencies/eur-mxn",
    "GBP/MXN": "https://mx.investing.com/currencies/gbp-mxn",
    "BTC/MXN": "https://www.investing.com/crypto/bitcoin/btc-mxn",
    "IPC (MMV)": "https://mx.investing.com/indices/ipc"
}

CETES_URL = "https://www.cetesdirecto.com/sites/cetes/ticker.json"


def init_bot():
    """Inits the bot."""

    # We create the Reddit instance.
    reddit = praw.Reddit(client_id=config.APP_ID, client_secret=config.APP_SECRET,
                         user_agent=config.USER_AGENT, username=config.REDDIT_USERNAME,
                         password=config.REDDIT_PASSWORD)

    # Load the pre-existing sirebar text.
    sidebar_text = open("sidebar.txt", "r", encoding="utf-8").read()

    # Start the Markdown table with 3 columns.
    table_text = """| | | |\n| --- | --- | --- |\n"""

    # We iterate over INVESTING_DICT and call the same function.
    for k, v in INVESTING_DICT.items():

        temp_data = get_investing_data(k, v)

        # Add the data to the Markdown table.
        table_text += "\n\n| {} | {} | {} |\n".format(
            temp_data[0], temp_data[1], temp_data[2])

        time.sleep(1)

    # We add the rest of financial instruments.
    for item in get_cetes():
        table_text += "| {} | | {} |\n".format(item[0], item[1])

    # Prepare the footer with the current date and time.
    now = datetime.now()
    footer = "\nÚltima actualización: {:%d-%m-%Y a las %H:%M:%S}".format(now)

    # Update the sidebar on old Reddit.
    reddit.subreddit(
        config.SUBREDDIT).wiki["config/sidebar"].edit(sidebar_text + table_text + footer)

    # Update a sidebar text widget on new Reddit.
    for widget in reddit.subreddit(config.SUBREDDIT).widgets.sidebar:

        if widget.shortName == "Indicadores Financieros":
            widget.mod.update(text=table_text + footer)
            break


def get_investing_data(name, url):
    """Performs web scraping and gets 3 values from investing.com

    Parameters
    ----------
    name : str
        The name of the currency pair.

    url : str
        The url to scrape.

    Returns
    -------
    tuple
         A Tuple containing 3 values.

    """

    with requests.get(url, headers=HEADERS) as response:

        soup = BeautifulSoup(response.text, "html.parser")

        latest_data = soup.find(
            "div", {"class": "top bold inlineblock"}).text.strip().split()

        price = latest_data[0]
        percentage = latest_data[2]

        return (name, price, percentage)


def get_cetes():
    """Gets data from Cetesdirecto JSON feed.

    Returns
    -------
    list
        A list of several financial instruments.

    """

    cetes_list = list()

    with requests.get(CETES_URL, headers=HEADERS) as response:

        for item in response.json()["datos"]:

            kind = item["tipo"].replace(
                "&ntilde;", "ñ").replace(":", "").strip()

            percentage = item["porcentaje"]
            cetes_list.append([kind, percentage, ""])

        return cetes_list


if __name__ == "__main__":

    init_bot()
