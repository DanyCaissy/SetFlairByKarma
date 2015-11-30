
def get_submission_karma_for_user(subreddit, user):

    """
    Obtain submission karma for user in the specified subreddit
    """

    karma = 0
    submitted_posts = user.get_submitted(limit=None)
    for post in submitted_posts:

        subreddit_name = post.subreddit.display_name

        if subreddit_name == subreddit:
            karma += post.score

    return karma


def get_comment_karma_for_user(subreddit, user):

    """
    Obtain comment karma for user in the specified subreddit
    """

    karma = 0
    user_comments = user.get_comments(sort='top', limit=None)
    for comment in user_comments:

        if str(comment.subreddit) == subreddit:
            karma += comment.score

    return karma


def get_total_karma_for_user(subreddit, user, include_submission_karma, include_comment_karma):

    """
    Obtain karma from either or both sources
    """

    total_karma = 0

    if (include_submission_karma):
        total_karma += get_submission_karma_for_user(subreddit, user)

    if (include_comment_karma):
        total_karma += get_comment_karma_for_user(subreddit, user)

    return total_karma
