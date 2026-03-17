import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
import storage
from pathlib import Path

app = FastAPI(title="O-social API")

# Habilitar CORS para o Next.js (rodando em :3000 por padrão)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PostSchema(BaseModel):
    id: int
    platform: str
    draft: str
    status: str
    tone: Optional[str] = None
    subreddit: Optional[str] = None
    created_at: str

@app.get("/posts", response_model=List[PostSchema])
def get_posts(status: Optional[str] = None):
    """Retorna todos os posts, opcionalmente filtrados por status."""
    if status:
        posts = storage.list_posts_by_status(status)
    else:
        # Pega os últimos 50 posts do banco
        with storage.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM posts ORDER BY created_at DESC LIMIT 50")
            columns = [column[0] for column in cursor.description]
            posts = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return posts

@app.get("/stats")
def get_stats():
    """Retorna estatísticas rápidas para o dashboard."""
    with storage.get_conn() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM posts WHERE status = 'PENDING'")
        pending = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM posts WHERE status = 'PUBLISHED'")
        published = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM posts WHERE status = 'REJECTED'")
        rejected = cursor.fetchone()[0]
        
    return {
        "pending": pending,
        "published": published,
        "rejected": rejected,
        "total": pending + published + rejected
    }

@app.get("/personas")
def get_personas():
    """Lê os arquivos de persona diponíveis."""
    prompts_dir = Path("prompts")
    personas = []
    if prompts_dir.exists():
        for file in prompts_dir.glob("*"):
            if file.suffix in [".md", ".txt"]:
                personas.append({
                    "name": file.name,
                    "content": file.read_text(encoding="utf-8")
                })
    return personas

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
