import os
import tweepy
from dotenv import load_dotenv
from monitors.base import BaseMonitor
import orchestrator

load_dotenv()

class XMonitor(BaseMonitor):
    def __init__(self):
        super().__init__("x")
        bearer_token = os.getenv("X_BEARER_TOKEN")
        
        if bearer_token:
            self.client = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)
        else:
            # Fallback para Consumer Keys se o Bearer não estiver no .env
            self.client = tweepy.Client(
                consumer_key=os.getenv("X_API_KEY"),
                consumer_secret=os.getenv("X_API_SECRET"),
                access_token=os.getenv("X_ACCESS_TOKEN"),
                access_token_secret=os.getenv("X_ACCESS_TOKEN_SECRET"),
                wait_on_rate_limit=True,
            )

    def scan_keywords(self, keywords: list, limit: int = 10):
        # Constrói a query para o X
        query = "(" + " OR ".join(keywords) + ") -is:retweet lang:pt"
        self.log(f"Searching X with query: {query}")
        
        try:
            response = self.client.search_recent_tweets(
                query=query,
                max_results=limit,
                tweet_fields=["created_at", "text", "public_metrics"]
            )
            
            if response.data:
                for tweet in response.data:
                    if self.is_processed(str(tweet.id)):
                        continue
                    
                    # Filtro básico de engajamento (ex: pelo menos 1 like ou RT)
                    metrics = tweet.public_metrics
                    engagement = metrics['like_count'] + metrics['retweet_count']
                    
                    self.log(f"Found tweet {tweet.id}: {tweet.text[:50]}... (Eng: {engagement})")
                    
                    # Trigger draft generation
                    try:
                        orchestrator.generate_draft(
                            platform="x",
                            topic=f"Tweet no X: {tweet.text}",
                            tone="reflexivo"
                        )
                        self.mark_as_processed(str(tweet.id))
                        self.log(f"Draft triggered for tweet {tweet.id}")
                    except Exception as e:
                        self.log(f"Error generating draft for tweet: {e}")
            else:
                self.log("No new tweets found.")
                
        except Exception as e:
            self.log(f"Error searching X: {e}")

if __name__ == "__main__":
    # Test execution
    monitor = XMonitor()
    keys = ["BNCC", "IA na educação", "SaaS Brasil", "automação de processos"]
    monitor.scan_keywords(keys)
