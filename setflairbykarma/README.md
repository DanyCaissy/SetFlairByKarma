SetFlairByKarma
======

This bot allows you to assign flair to users in your subreddit based on their karma. You can assign both their flair_text and their flair_css.
_______

###How does it work?

You can run the bot as often as you wish, I run it every 30 minutes, it works the following way:

1- Loops through the comments in a defined thread (EX: https://www.reddit.com/r/cscareerquestions/comments/3qg1ns/meta_changes_to_user_flair_please_read/)

2- If a comment hasn't already been read in the past, calculate that user's karma (link, comment or both) and assign the corresponding flair (text, css or both)

3- [Optional] Your bot can reply to the user to let them know their flair has been set.

4- Saves the date of the last comment that was processed in a sqlite database to ensure we don't ever process the same comment twice


_______
###Requirements

1- Be a moderator of a subreddit with permission to modify user flair.

2- You will need to create an app to obtain the information necessary for the credentials.py file (see [this](https://github.com/DanyCaissy/Reddit/blob/master/README.md) if you don't know what this file is for), [this tutorial](http://praw.readthedocs.org/en/stable/pages/oauth.html) will show you how. You will need the following permissions: "modflair identity submit edit".

3- On your server, you will need Python installed as well as [praw](http://praw.readthedocs.org/en/stable/index.html#installation).

4- Once the bot is ready, create a thread asking your users to post if they want their flair to be set-up, the bot will assign their flair the next time it is ran.

5- Use a scheduler (such as CRON) to run the script periodically.
