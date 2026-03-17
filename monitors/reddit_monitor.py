import os
import praw
from dotenv import load_dotenv
from monitors.base import BaseMonitor
import orchestrator

load_dotenv()

class RedditMonitor(BaseMonitor):
    def __init__(self):
        super().__init__("reddit")
        self.reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            username=os.getenv("REDDIT_USERNAME"),
            password=os.getenv("REDDIT_PASSWORD"),
            user_agent=os.getenv("REDDIT_USER_AGENT", "PlanoEduMonitor/1.0"),
        )

    def scan_subreddits(self, subreddits: list, keywords: list, limit: int = 10):
        for sub_name in subreddits:
            self.log(f"Scanning r/{sub_name}...")
            try:
                subreddit = self.reddit.subreddit(sub_name)
                # Pega tanto os 'new' quanto os 'hot'
                for submission in subreddit.hot(limit=limit):
                    if self.is_processed(submission.id):
                        continue
                    
                    text_to_check = (submission.title + " " + submission.selftext).lower()
                    if any(k.lower() in text_to_check for k in keywords):
                        self.log(f"Found relevant post: {submission.title[:50]}...")
                        
                        # Trigger draft generation
                        try:
                            orchestrator.generate_draft(
                                platform="reddit",
                                topic=f"Post no Reddit: {submission.title}\n\nConteúdo: {submission.selftext[:500]}",
                                tone="empático",
                                subreddit=sub_name
                            )
                            self.mark_as_processed(submission.id)
                            self.log(f"Draft triggered for {submission.id}")
                        except Exception as e:
                            self.log(f"Error generating draft: {e}")
                            
            except Exception as e:
                self.log(f"Error scanning r/{sub_name}: {e}")

if __name__ == "__main__":
    # Test execution
    monitor = RedditMonitor()
    subs = ["Teachers", "brasil", "edtech"]
    keys = ["IA", "AI", "BNCC", "educação", "software", "SaaS"]
    monitor.scan_subreddits(subs, keys)
