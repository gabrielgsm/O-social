"""
publishers/x.py — Publisher para X (Twitter)
Publica posts simples e threads via X API v2 (tweepy).
"""
import os
import time
import tweepy
from dotenv import load_dotenv

load_dotenv()

TWEET_SEPARATOR = "---TWEET---"
MAX_TWEET_LEN = 280
THREAD_DELAY = 2  # segundos entre tweets de uma thread


def _get_client() -> tweepy.Client:
    return tweepy.Client(
        bearer_token=os.getenv("X_BEARER_TOKEN"),
        consumer_key=os.getenv("X_API_KEY"),
        consumer_secret=os.getenv("X_API_SECRET"),
        access_token=os.getenv("X_ACCESS_TOKEN"),
        access_token_secret=os.getenv("X_ACCESS_TOKEN_SECRET"),
        wait_on_rate_limit=True,
    )


def _split_thread(draft: str) -> list[str]:
    """Divide o rascunho em tweets individuais."""
    if TWEET_SEPARATOR in draft:
        tweets = [t.strip() for t in draft.split(TWEET_SEPARATOR) if t.strip()]
    else:
        # Tenta quebrar em 280 chars por parágrafo se necessário
        if len(draft) <= MAX_TWEET_LEN:
            tweets = [draft]
        else:
            # Quebra por parágrafo
            paragraphs = [p.strip() for p in draft.split("\n\n") if p.strip()]
            tweets = []
            current = ""
            for para in paragraphs:
                if len(current) + len(para) + 2 <= MAX_TWEET_LEN:
                    current = (current + "\n\n" + para).strip() if current else para
                else:
                    if current:
                        tweets.append(current)
                    current = para
            if current:
                tweets.append(current)

    # Garante limite de caracteres
    validated = []
    for t in tweets:
        if len(t) > MAX_TWEET_LEN:
            # Trunca com reticências
            t = t[:MAX_TWEET_LEN - 1] + "…"
        validated.append(t)

    return validated


def publish_x(draft: str) -> str:
    """
    Publica um tweet ou thread no X.
    Retorna o ID do primeiro tweet publicado.
    """
    client = _get_client()
    tweets = _split_thread(draft)

    print(f"📤 Publicando no X: {len(tweets)} tweet(s)…")

    first_id = None
    reply_to = None

    for i, tweet_text in enumerate(tweets):
        kwargs = {"text": tweet_text}
        if reply_to:
            kwargs["in_reply_to_tweet_id"] = reply_to

        response = client.create_tweet(**kwargs)
        tweet_id = str(response.data["id"])
        print(f"  ✓ Tweet {i+1}/{len(tweets)} publicado: id={tweet_id}")

        if first_id is None:
            first_id = tweet_id
        reply_to = tweet_id

        if i < len(tweets) - 1:
            time.sleep(THREAD_DELAY)

    return first_id
