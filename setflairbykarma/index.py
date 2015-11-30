# By Dany Caissy
# https://github.com/DanyCaissy/

import logging # To log errors or otherwise
import collections # Ordered dictionary
import sqlite3
import datetime

import praw

import credentials  # Contains my personal credentials, you don't need to include this
import karma_for_user # Calculates karma of a user within a specific subreddit


'''USER CONFIGURATION'''

# This configuration is based on this submission: https://www.reddit.com/r/cscareerquestions/comments/3qg1ns/
SUBREDDIT_NAME = 'cscareerquestions' # Subreddit in which you want to assign flairs
SUBMISSION_ID = '3qg1ns' # Submission that will be monitored, flair will only be set on people with top-level comments

# This is the flair (text and/or css) assigned to a user if they reach X Karma
# EX: A user with 1500 karma would be assigned the css flair "over-1000-karma"
CSS_BY_KARMA = {500: {'flair_text': None, 'flair_css_class': 'over-500-karma'},
                1000: {'flair_text': None, 'flair_css_class': 'over-1000-karma'},
                3000: {'flair_text': None, 'flair_css_class': 'over-3000-karma'},
                5000: {'flair_text': None, 'flair_css_class': 'over-5000-karma'},
                10000: {'flair_text': None, 'flair_css_class': 'over-10000-karma'},
                20000: {'flair_text': None, 'flair_css_class': 'over-20000-karma'}}

# Ordered in ascending order
CSS_BY_KARMA = collections.OrderedDict(sorted(CSS_BY_KARMA.items()))

# Choose what to assign to the user once they reach X karma
ASSIGN_FLAIR_TEXT = False
ASSIGN_FLAIR_CSS_CLASS = True

# When flair is assigned, decide if you want a confirmation comment and if so, what it should say
CONFIRMATION_COMMENT = True
CONFIRMATION_COMMENT_TEXT = 'Your flair has been assigned! Your calculated karma was {0}.'

# Which types of karma you want to include, obviously if both are set to False, karma will always be 0
INCLUDE_SUBMISSION_KARMA = True
INCLUDE_COMMENT_KARMA = True

def get_flair_info_for_karma(karma):

    """
    Returns a dictionary containing information about which flair should be assigned to the user depending on their karma
    """

    # Default flair_info if we find no match
    flair_info = {'flair_text': None, 'flair_css_class': None}

    # Key = Karma, Value = Flair_info dictionary
    for dic_karma, dic_flair_object in CSS_BY_KARMA.items():

        # If karma is enough for this level, set it as such
        if karma > dic_karma:
            flair_info = dic_flair_object
        else:
            break

    return flair_info


def set_flair_for_user_subreddit(username, subreddit, comment=None):

    """
    All main operations required to set the flair of a user in a specific subreddit
    """

    logging.info('Setting flair for user:' + username)

    try:
        user = reddit_instance.get_redditor(username)
    except Exception as e:
        logging.debug('User is not found anymore:')
        logging.exception(e)

    # Here we calculate the karma for this specific user depending on the configuration that was defined
    total_karma = karma_for_user.get_total_karma_for_user(SUBREDDIT_NAME, user, INCLUDE_SUBMISSION_KARMA, INCLUDE_COMMENT_KARMA)
    logging.info('Karma: ' + str(total_karma))

    flair_info = get_flair_info_for_karma(total_karma)
    logging.info(flair_info)

    redditor_current_flair = subreddit.get_flair(user)
    flair_css_class = redditor_current_flair['flair_css_class']
    flair_text = redditor_current_flair['flair_text']

    if ASSIGN_FLAIR_TEXT:
        flair_text = flair_info['flair_text']

    if ASSIGN_FLAIR_CSS_CLASS:
        flair_css_class = flair_info['flair_css_class']

    subreddit.set_flair(username, flair_css_class=flair_css_class, flair_text=flair_text)

    if comment is not None and CONFIRMATION_COMMENT:
        comment.reply (CONFIRMATION_COMMENT_TEXT.format(total_karma))


if __name__ == '__main__':

    '''LOGGING'''
    LOG_FILENAME = 'log.out'
    logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%m-%d %H:%M',)

    '''AUTHENTICATION'''
    # Set these to your own credentials
    reddit_instance = praw.Reddit(credentials.user_agent)
    reddit_instance.set_oauth_app_info(credentials.app_id, credentials.app_secret, credentials.app_refresh)
    reddit_instance.refresh_access_information(credentials.app_refresh)

    '''OPENING DATABASE'''
    sql = sqlite3.connect('sql.db')
    cur = sql.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS last_date(last_timestamp int)')

    '''GET THE NEWEST TIMESTAMP'''
    cur.execute('SELECT * FROM last_date')
    last_date_record = cur.fetchone()
    if last_date_record:
        saved_timestamp = last_date_record[0]
    else:
        saved_timestamp = 0

    i = datetime.datetime.now()
    print (i.isoformat() + ' - Timestamp:' + str(saved_timestamp))
    logging.info('Timestamp:' + str(saved_timestamp))

    newest_timestamp = saved_timestamp

    '''LOGIC'''
    subreddit = reddit_instance.get_subreddit(SUBREDDIT_NAME)

    submission = reddit_instance.get_submission(submission_id=SUBMISSION_ID)

    submission.replace_more_comments(limit=None, threshold=0)
    all_comments = submission.comments

    for comment in all_comments:

        author_name = str(comment.author)
        comment_timestamp = int(comment.created)

        if comment_timestamp > newest_timestamp:  # Save the newest timestamp which will be saved into the database
            newest_timestamp = comment_timestamp

        if comment_timestamp > saved_timestamp:  # Only if we didn't already process this post

            try:
                set_flair_for_user_subreddit(author_name, subreddit, comment)
            except Exception as e:
                logging.exception(e)

    '''UPDATE WITH LATEST TIMESTAMP'''
    # This avoids reading the same comments again in the future
    cur.execute('DELETE FROM last_date')
    cur.execute('INSERT INTO last_date VALUES(?)', [newest_timestamp])
    sql.commit()