"""
This bot automates the process of making posts and sticky/unsticking them.
"""


import random
import sys
from datetime import datetime
import os
import praw

import config

MONDAY_FILE = "./monday.txt"
WEDNESDAY_FILE = "./wednesday.txt"
FRIDAY_FILE = "./friday.txt"

MONDAY_TEMPLATE_FILE = "./templates/monday_template.txt"
WEDNESDAY_TEMPLATE_FILE = "./templates/wednesday_template.txt"
FRIDAY_TEMPLATE_FILE = "./templates/friday_template.txt"

POLITICIANS_FILE = "./politicians.txt"
PROCESSED_POLITICIANS_FILE = "./processed_politicians.txt"


def init_bot():
    """Inits the bot, reads the system arguments and chooses the correct function."""

    # We create the Reddit instance.
    reddit = praw.Reddit(client_id=config.APP_ID, client_secret=config.APP_SECRET,
                         user_agent=config.USER_AGENT, username=config.REDDIT_USERNAME,
                         password=config.REDDIT_PASSWORD)

    # Check if we have the 3 required arguments.
    if len(sys.argv) == 3:

        method = sys.argv[1]
        day = sys.argv[2]

        if method == "sticky":
            if day == "monday":
                post_monday(reddit)
            elif day == "wednesday":
                post_wednesday(reddit)
            elif day == "friday":
                post_friday(reddit)

        elif method == "unsticky":
            if day == "monday":
                unsticky_post(reddit, MONDAY_FILE)
            elif day == "wednesday":
                unsticky_post(reddit, WEDNESDAY_FILE)
            elif day == "friday":
                unsticky_post(reddit, FRIDAY_FILE)


def post_monday(reddit):
    """Posts and stickies the Monday discussion.

    Parameters
    ----------
    reddi : Reddit
        A Reddit instance.

    """

    posts_text = ""

    # Take the top 3 posts from last week and add them to the submission text.
    for submission in reddit.subreddit(config.SUBREDDIT).top("week", limit=3):
        posts_text += "* [{}](https://redd.it/{})\n".format(
            submission.title, submission.id)

    title = "¿Qué sucedió en tu estado la semana pasada? Semana {}".format(
        datetime.now().strftime("%V"))

    text = open(MONDAY_TEMPLATE_FILE, "r",
                encoding="utf-8").read().replace("%POSTS_LIST%", posts_text)

    current_submission = reddit.subreddit(config.SUBREDDIT).submit(
        title=title, selftext=text)

    # Submit the text, sticky it and update the log.
    current_submission = reddit.subreddit(config.SUBREDDIT).submit(
        title=title, selftext=text)

    reddit.submission(current_submission).mod.sticky()
    update_log(MONDAY_FILE, current_submission.id)


def post_wednesday(reddit):
    """Posts and stickies the Wednesday discussion.

    A random politician is taken from a pool of available
    people.

    Parameters
    ----------
    reddi : Reddit
        A Reddit instance.

    """

    politicians = open(POLITICIANS_FILE, "r",
                       encoding="utf-8").read().splitlines()

    for item in load_processed_politicians():
        politicians.remove(item)

    # If our pool is empty we reset the file and try again.
    if len(politicians) == 0:
        os.remove(PROCESSED_POLITICIANS_FILE)
        post_wednesday(reddit)

    selected_politician = random.choice(politicians)

    title = "Discusión Semanal - {}".format(selected_politician)

    text = open(WEDNESDAY_TEMPLATE_FILE, "r",
                encoding="utf-8").read().replace("%POLITICIAN%", selected_politician)

    # Submit the text, sticky it and update the log.
    current_submission = reddit.subreddit(config.SUBREDDIT).submit(
        title=title, selftext=text)

    reddit.submission(current_submission).mod.sticky()
    update_log(WEDNESDAY_FILE, current_submission.id)
    update_processed_politicians(selected_politician)


def post_friday(reddit):
    """Posts and stickies the Friday discussion.

    Parameters
    ----------
    reddi : Reddit
        A Reddit instance.

    """

    title = "¿Qué planes tienes para este fin de semana?"
    text = open(FRIDAY_TEMPLATE_FILE, "r", encoding="utf-8").read()

    # Submit the text, sticky it and update the log.
    current_submission = reddit.subreddit(config.SUBREDDIT).submit(
        title=title, selftext=text)

    reddit.submission(current_submission).mod.sticky()
    update_log(FRIDAY_FILE, current_submission.id)


def update_log(file_name, post_id):
    """Updates the processed posts log with the given post id.

    Parameters
    ----------
    post_id : str
        A Reddit post id.

    """

    with open(file_name, "w", encoding="utf-8") as log_file:
        log_file.write(post_id)


def unsticky_post(reddit, file_name):
    """Unstickies the specified day post.

    Parameters
    ----------
    reddit : Reddit
        A Reddit instance.

    file_name : str
        The file name to read the post id from.

    """

    with open(file_name, "r", encoding="utf-8") as temp_file:
        post_id = temp_file.read().strip()
        reddit.submission(post_id).mod.sticky(state=False)


def load_processed_politicians():
    """Load the names of the politicians that have been
    already posted.
    """

    try:
        with open(PROCESSED_POLITICIANS_FILE, "r", encoding="utf-8") as temp_file:
            return temp_file.read().splitlines()

    except FileNotFoundError:
        with open(PROCESSED_POLITICIANS_FILE, "w", encoding="utf-8") as temp_file:
            return []


def update_processed_politicians(politician):
    """Updates the processed posts log with the given post id.

    Parameters
    ----------
    politican : str
        A politician name.

    """

    with open(PROCESSED_POLITICIANS_FILE, "a", encoding="utf-8") as temp_file:
        temp_file.write(politician + "\n")


if __name__ == "__main__":

    init_bot()
