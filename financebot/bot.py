"""
This bot performs a bit of web scraping to get current values
of several currency pairs and financial instruments.
"""

import time
from datetime import datetime, timedelta

import praw
import requests
from bs4 import BeautifulSoup
from xlrd import open_workbook

import config

HEADERS = {"User-Agent": "FinanceBot v0.2"}

INVESTING_DICT = {
    "USD/MXN": "https://mx.investing.com/currencies/usd-mxn",
    "EUR/MXN": "https://mx.investing.com/currencies/eur-mxn",
    "GBP/MXN": "https://mx.investing.com/currencies/gbp-mxn",
    "BTC/MXN": "https://www.investing.com/crypto/bitcoin/btc-mxn",
    "IPC (BMV)": "https://mx.investing.com/indices/ipc"
}

BANXICO1_URL = "https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?sector=22&accion=consultarCuadro&idCuadro=CF107&locale=es&formatoXLS.x=1&fechaInicio={}&fechaFin={}"
BANXICO2_URL = "https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?accion=consultarCuadro&idCuadro=CF114&formatoXLS.x=1&fechaInicio={}&fechaFin={}"


def init_bot():
    """Inits the bot."""

    # We create the Reddit instance.
    reddit = praw.Reddit(client_id=config.APP_ID, client_secret=config.APP_SECRET,
                         user_agent=config.USER_AGENT, username=config.REDDIT_USERNAME,
                         password=config.REDDIT_PASSWORD)

    # Load the pre-existing sirebar text.
    sidebar_text = open("sidebar.txt", "r", encoding="utf-8").read()

    # Start the Markdown table with 3 columns.
    table_text = """\n\n| | | |\n| --- | --- | --- |\n"""

    # We iterate over INVESTING_DICT and call the same function.
    for k, v in INVESTING_DICT.items():

        temp_data = get_investing_data(k, v)

        # Add the data to the Markdown table.
        table_text += "| {} | {} | {} |\n".format(
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
    """Gets data from Banxico Excel archives.
    It first downloads the Excel files and then reads
    cell values from the specified rows.

    Returns
    -------
    list
        A list of several financial instruments.

    """

    # The Excel files are behind a simple GET request.
    # Two of the parameters are UNIX timestamps.
    now = datetime.now()
    now_ts = int(now.timestamp()) * 1000

    last_21_days = now - timedelta(days=21)
    last_21_days_ts = int(last_21_days.timestamp()) * 1000

    last_120_days = now - timedelta(days=120)
    last_120_days_ts = int(last_120_days.timestamp()) * 1000

    # With our timestamps ready we download both files.
    with requests.get(BANXICO1_URL.format(last_21_days_ts, now_ts)) as response:
        with open("./banxico1.xls", "wb") as temp_file:
            temp_file.write(response.content)

    with requests.get(BANXICO2_URL.format(last_120_days_ts, now_ts)) as response:
        with open("./banxico2.xls", "wb") as temp_file:
            temp_file.write(response.content)

    # We open both files and start extracting the values we need.
    book1 = open_workbook("banxico1.xls")
    sheet1 = book1.sheet_by_index(0)

    book2 = open_workbook("banxico2.xls")
    sheet2 = book2.sheet_by_index(0)

    data_list = list()

    data_list.append(["CETES 1 mes", "+{}%".format(find_value(sheet1, 14))])
    data_list.append(["CETES 3 meses", "+{}%".format(find_value(sheet1, 18))])
    data_list.append(["CETES 6 meses", "+{}%".format(find_value(sheet1, 22))])
    data_list.append(["CETES 1 año", "+{}%".format(find_value(sheet2, 15))])

    data_list.append(["BONOS 3 años", "+{}%".format(find_value(sheet1, 48))])
    data_list.append(["BONOS 5 años", "+{}%".format(find_value(sheet1, 52))])
    data_list.append(["BONOS 10 años", "+{}%".format(find_value(sheet2, 30))])
    data_list.append(["BONOS 20 años", "+{}%".format(find_value(sheet2, 31))])
    data_list.append(["BONOS 30 años", "+{}%".format(find_value(sheet2, 32))])

    data_list.append(
        ["UDIBONOS 3 años", "+{}% (más inflación)".format(find_value(sheet1, 73))])

    data_list.append(
        ["UDIBONOS 10 años", "+{}% (más inflación)".format(find_value(sheet1, 81))])

    data_list.append(
        ["UDIBONOS 30 años", "+{}% (más inflación)".format(find_value(sheet2, 25))])

    return data_list


def find_value(sheet, row):
    """Finds the best available value.

    Parameers
    ---------
    sheet : workbook.sheet
        An Excel sheet.

    row : int
        The row where the value is located.

    Returns
    -------
    string
        The cell value that wasn't 'N/E' (not eligible).

    """

    # We first try looking in the fifth column and keep falling
    # back until we go to the third column.
    if sheet.cell_value(rowx=row, colx=4) != "N/E":
        return sheet.cell_value(rowx=row, colx=4)
    elif sheet.cell_value(rowx=row, colx=3) != "N/E":
        return sheet.cell_value(rowx=row, colx=3)
    elif sheet.cell_value(rowx=row, colx=2) != "N/E":
        return sheet.cell_value(rowx=row, colx=2)


if __name__ == "__main__":

    init_bot()
