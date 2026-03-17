"""
storage.py — Camada de persistência SQLite
Responsável por registrar todo o ciclo de vida dos posts:
gerado → aprovado/rejeitado → publicado
"""
import sqlite3
import os
from datetime import datetime, timedelta
from contextlib import contextmanager
from typing import Optional, List

DB_PATH = os.getenv("DB_PATH", "social.db")


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Cria as tabelas se não existirem."""
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS posts (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                platform    TEXT NOT NULL CHECK(platform IN ('x', 'reddit')),
                draft       TEXT NOT NULL,
                prompt_used TEXT,
                context     TEXT,
                tone        TEXT,
                status      TEXT NOT NULL DEFAULT 'PENDING'
                            CHECK(status IN ('PENDING','APPROVED','REJECTED','PUBLISHED','EXPIRED')),
                subreddit   TEXT,
                created_at  TEXT NOT NULL DEFAULT (datetime('now')),
                approved_at TEXT,
                published_at TEXT,
                expires_at  TEXT,
                platform_id  TEXT   -- ID do tweet/post após publicação
            );

            CREATE TABLE IF NOT EXISTS engagements (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id     INTEGER NOT NULL REFERENCES posts(id),
                likes       INTEGER DEFAULT 0,
                retweets    INTEGER DEFAULT 0,
                comments    INTEGER DEFAULT 0,
                collected_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE INDEX IF NOT EXISTS idx_posts_status   ON posts(status);
            CREATE INDEX IF NOT EXISTS idx_posts_platform ON posts(platform);
            CREATE INDEX IF NOT EXISTS idx_posts_created  ON posts(created_at);
        """)
    print("✓ Banco de dados inicializado.")


# ─── Posts ────────────────────────────────────────────────────────────────────

def create_post(platform: str, draft: str, prompt_used: str = None,
                context: str = None, tone: str = None,
                subreddit: str = None, expiry_hours: int = 24) -> int:
    """Cria um novo rascunho de post e retorna o ID."""
    expires_at = (datetime.utcnow() + timedelta(hours=expiry_hours)).isoformat()
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO posts (platform, draft, prompt_used, context, tone, subreddit, expires_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (platform, draft, prompt_used, context, tone, subreddit, expires_at)
        )
        return cur.lastrowid


def get_post(post_id: int) -> Optional[dict]:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
        return dict(row) if row else None


def update_post_status(post_id: int, status: str, platform_id: str = None):
    """Atualiza status de um post. Registra timestamps relevantes."""
    now = datetime.utcnow().isoformat()
    approved_at  = now if status == "APPROVED"  else None
    published_at = now if status == "PUBLISHED" else None
    with get_conn() as conn:
        conn.execute(
            """UPDATE posts
               SET status = ?,
                   platform_id  = COALESCE(?, platform_id),
                   approved_at  = COALESCE(?, approved_at),
                   published_at = COALESCE(?, published_at)
               WHERE id = ?""",
            (status, platform_id, approved_at, published_at, post_id)
        )


def expire_old_drafts():
    """Expira rascunhos que ultrapassaram o prazo de aprovação."""
    with get_conn() as conn:
        cur = conn.execute(
            """UPDATE posts SET status = 'EXPIRED'
               WHERE status = 'PENDING'
               AND expires_at < datetime('now')"""
        )
        if cur.rowcount:
            print(f"⏰ {cur.rowcount} rascunho(s) expirado(s).")


def list_pending_posts(platform: str = None) -> List[dict]:
    """Retorna rascunhos pendentes de aprovação."""
    query = "SELECT * FROM posts WHERE status = 'PENDING'"
    params = []
    if platform:
        query += " AND platform = ?"
        params.append(platform)
    query += " ORDER BY created_at ASC"
    with get_conn() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]


def get_recent_drafts(platform: str, limit: int = 10) -> List[str]:
    """Retorna os últimos rascunhos para evitar repetição de tema."""
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT draft FROM posts
               WHERE platform = ? AND status IN ('PUBLISHED','APPROVED')
               ORDER BY created_at DESC LIMIT ?""",
            (platform, limit)
        ).fetchall()
        return [r["draft"] for r in rows]


def list_posts_by_status(status: str) -> List[dict]:
    """Retorna todos os posts com um status específico."""
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM posts WHERE status = ? ORDER BY created_at DESC", (status,)).fetchall()
        return [dict(r) for r in rows]


# ─── Engajamento ──────────────────────────────────────────────────────────────

def record_engagement(post_id: int, likes: int, retweets: int, comments: int):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO engagements (post_id, likes, retweets, comments)
               VALUES (?, ?, ?, ?)""",
            (post_id, likes, retweets, comments)
        )


# ─── CLI utilitário ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    print("\nPosts recentes:")
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM posts ORDER BY created_at DESC LIMIT 20").fetchall()
        for r in rows:
            print(f"  [{r['id']}] {r['platform']:6} | {r['status']:10} | {r['created_at'][:16]} | {r['draft'][:60]}…")
