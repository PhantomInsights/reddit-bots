"""
This script consumes data from Wikipedia and a Google RSS feed.
Then it fills a template with that data and updates a Reddit submission.
"""

import xml.etree.ElementTree as ET
from datetime import datetime

import praw
import requests
from bs4 import BeautifulSoup

import config

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0"}


def main():
    """Starts getting the data."""

    chronology = get_chronology()
    links = get_latest_news()
    table = get_table()

    # Prepare the footer with the current date and time.
    now = datetime.now()
    footer = "\nÚltima actualización: {:%d-%m-%Y a las %H:%M:%S}".format(now)

    template = open("./template.txt", "r", encoding="utf-8").read()

    submission_text = template.format(chronology, links, table, footer)

    # We create the Reddit instance.
    reddit = praw.Reddit(client_id=config.APP_ID, client_secret=config.APP_SECRET,
                         user_agent=config.USER_AGENT, username=config.REDDIT_USERNAME,
                         password=config.REDDIT_PASSWORD)

    reddit.submission("faw77h").edit(submission_text)
    reddit.submission("fbjtoy").edit(submission_text)


def get_latest_news():
    """Reads a RSS feed and extracts the latest 15 news headlines and links.

    Returns
    -------
    str
        A Markdown formatted string containing news titles and urls.

    """

    url = "https://news.google.com/rss/search?q=méxico+coronavirus&hl=es-419&gl=MX"
    links_string = ""

    with requests.get(url, headers=HEADERS) as response:

        root = ET.fromstring(response.text)

        # Only read the first 15 links.
        for item in root.findall(".//item")[:15]:

            title = item.find("title").text.strip()
            url = item.find("link").text
            links_string += "* [{}]({})\n".format(title, url)

    return links_string


def get_table():
    """Gets the epidemiology table from Wikipedia.

    Returns
    -------
    str
        A Markdown formatted table containing the values from each country.

    """

    # This dict contains the requested countries by the community.
    countries = {
        "Mexico": "México",
        "United States": "EE. UU.",
        "Pakistan": "Pakistán",
        "Italy": "Italia",
        "Japan": "Japón",
        "China": "China",
        "Spain": "España",
        "Iran": "Irán",
        "South Korea": "Corea del Sur",
        "Brazil": "Brasil",
        "Ecuador": "Ecuador",
        "Argentina": "Argentina",
        "Chile": "Chile",
        "Philippines": "Filipinas",
        "France": "Francia",
        "Germany": "Alemania"
    }

    url = "https://en.m.wikipedia.org/wiki/2019%E2%80%9320_coronavirus_outbreak"
    table_text = "| País | Casos Confirmados | Fallecidos ^\(%) | Recuperados ^\(%) |\n| -- | -- | -- | -- |\n"

    with requests.get(url, headers=HEADERS) as response:

        soup = BeautifulSoup(response.text, "html.parser")
        [tag.extract() for tag in soup("sup")]

        for row in soup.find_all("table")[2].find_all("th"):

            for k, v in countries.items():

                if k in row.text:
                    tds = row.parent.find_all("td")

                    cases = int(tds[0].text.replace(",", "").strip())
                    deaths = int(tds[1].text.replace(",", "").strip())
                    recoveries = int(tds[2].text.replace(",", "").strip())

                    table_text += "| {} | {:,} | {:,} ^{}% | {:,} ^{}% |\n".format(
                        v,
                        cases,
                        deaths,
                        round(deaths / cases * 100, 2),
                        recoveries,
                        round(recoveries / cases * 100, 2)
                    )

                    break

    # Add the totals rows.
    last_row = soup.find("tr", "sortbottom").find_all("th")
    cases = int(last_row[1].text.replace(",", "").strip())
    deaths = int(last_row[2].text.replace(",", "").strip())
    recoveries = int(last_row[3].text.replace(",", "").strip())

    table_text += "| __{}__ | __{:,}__ | __{:,} ^{}%__ | __{:,} ^{}%__ |\n".format(
        "Global",
        cases,
        deaths,
        round(deaths / cases * 100, 2),
        recoveries,
        round(recoveries / cases * 100, 2)
    )

    return table_text


def get_chronology():
    """Gets the chronology for the specified url.

    Returns
    -------
    str
        A Markdown formatted string containing paragraphs of chronology.

    """

    url = "https://es.m.wikipedia.org/wiki/Pandemia_de_COVID-19_de_2020_en_Mexico"
    chronology_text = ""

    with requests.get(url, headers=HEADERS) as response:

        soup = BeautifulSoup(response.text, "html.parser")
        [tag.extract() for tag in soup("sup")]

        # First we look for the chronology section.
        chronology = soup.find(
            "span", {"id": "Cronología"}).find_next("section")

        # Then we segment it on the H3 tags.
        for item in chronology.find_all("h4"):

            # We create a paragraphs list.
            paragraphs = list()

            for subitem in item.next_siblings:

                # We only add the paragraphs to our list, if we find an h4 tag
                # we break the loop since it means we are in the next day.
                if subitem.name == "h4":
                    break
                elif subitem.name == "p":
                    paragraphs.append(
                        "> " + subitem.text.replace("\t", "").replace("\n", " ").strip() + "\n\n")

            # Clean up and formatting.
            item_title = item.text.replace(
                "\n", "").replace("Editar", "").strip()

            chronology_text += "#### {}\n\n{}".format(
                item_title, "".join(paragraphs))

    return chronology_text


if __name__ == "__main__":

    main()
