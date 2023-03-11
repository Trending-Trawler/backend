import asyncpraw

from settings import settings


def login(reddit_id, reddit_secret):
    try:
        reddit = asyncpraw.Reddit(
            client_id=reddit_id,
            client_secret=reddit_secret,
            user_agent="ThreadTrawler",
        )

        print("Logged in to Reddit successfully!")
        return reddit
    except Exception as e:
        return e


def chose_comments(thread_id):
    topn = 10
    comments = []
    for top_level_comment in thread_id.comments:
        if len(comments) == topn:
            break
        if isinstance(top_level_comment, asyncpraw.models.MoreComments):
            continue
        comments.append(top_level_comment)

    chosen_comments = comments
    print(f"{len(chosen_comments)} comments are chosen")
    return chosen_comments


async def get_comments(thread_url):
    reddit_client = login(
        settings.reddit_client_id, settings.reddit_client_secret.get_secret_value()
    )
    thread_id = await reddit_client.submission(url=thread_url)
    return chose_comments(thread_id)
