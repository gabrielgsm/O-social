"""
publishers/reddit.py — Publisher para Reddit
Posta comentários em threads existentes via PRAW com retry e rate limiting.
"""
import os
import time
import praw
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from dotenv import load_dotenv

load_dotenv()


def _get_reddit() -> praw.Reddit:
    return praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        username=os.getenv("REDDIT_USERNAME"),
        password=os.getenv("REDDIT_PASSWORD"),
        user_agent=os.getenv("REDDIT_USER_AGENT", "PlanoEduBot/1.0"),
    )


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=4, max=60),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def _post_comment(submission, text: str):
    """Posta o comentário com retry + backoff exponencial."""
    comment = submission.reply(text)
    return str(comment.id)


def publish_reddit(draft: str, subreddit: str = "brasil",
                   submission_url: str = None, submission_id: str = None) -> str:
    """
    Posta um comentário em um post Reddit existente.

    Precisa de submission_url OU submission_id.
    Retorna o ID do comentário publicado.
    """
    reddit = _get_reddit()

    if submission_url:
        submission = reddit.submission(url=submission_url)
    elif submission_id:
        submission = reddit.submission(id=submission_id)
    else:
        raise ValueError("Forneça submission_url ou submission_id para publicar no Reddit.")

    print(f"📤 Publicando comentário em r/{subreddit} — post: {submission.title[:60]}…")
    comment_id = _post_comment(submission, draft)
    print(f"  ✓ Comentário publicado: id={comment_id}")

    # Taxa mínima de espera para respeitar rate limits do Reddit
    time.sleep(2)
    return comment_id
