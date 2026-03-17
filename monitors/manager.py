import time
import argparse
from monitors.reddit_monitor import RedditMonitor
from monitors.x_monitor import XMonitor

def run_monitors(limit_per_monitor: int = 5):
    print("🚀 Iniciando execução de todos os monitores...")
    
    # Reddit
    try:
        reddit = RedditMonitor()
        subs = ["Teachers", "brasil", "edtech", "ensinobasico", "professores"]
        keys = ["IA", "AI", "BNCC", "educação", "software", "SaaS", "escola"]
        reddit.scan_subreddits(subs, keys, limit=limit_per_monitor)
    except Exception as e:
        print(f"❌ Erro no monitor Reddit: {e}")

    # X (Twitter)
    try:
        x = XMonitor()
        x_keys = ["#BNCC", "IA na educação", "SaaS Brasil", "automação", "fazer SaaS"]
        x.scan_keywords(x_keys, limit=limit_per_monitor)
    except Exception as e:
        print(f"❌ Erro no monitor X: {e}")

    print("✅ Execução finalizada.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor Manager — O-social")
    parser.add_argument("--limit", type=int, default=5, help="Limite de posts por monitor")
    parser.add_argument("--interval", type=int, help="Se definido, roda em loop a cada X segundos")
    
    args = parser.parse_args()
    
    if args.interval:
        print(f"🕒 Rodando em modo contínuo (intervalo: {args.interval}s)...")
        while True:
            run_monitors(args.limit)
            time.sleep(args.interval)
    else:
        run_monitors(args.limit)
