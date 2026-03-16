"""
orchestrator.py — Motor Central de Orquestração
Recebe triggers, monta contexto, chama Claude API e envia para aprovação.
"""
import os
import argparse
import json
from pathlib import Path
from dotenv import load_dotenv
import httpx
import storage
from publishers.x import publish_x
from publishers.reddit import publish_reddit

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
MODEL = "anthropic/claude-3.5-sonnet"
MAX_TOKENS = 1024

PROMPTS_DIR = Path(__file__).parent / "prompts"


def load_persona(platform: str) -> str:
    mapping = {"x": "persona_x.txt", "reddit": "persona_reddit.txt"}
    path = PROMPTS_DIR / mapping.get(platform, "persona_x.txt")
    return path.read_text(encoding="utf-8")


def build_user_prompt(platform: str, topic: str, tone: str,
                      subreddit: str = None, recent_drafts: list[str] = None) -> str:
    lines = []

    if platform == "x":
        lines.append(f"Gere um post para o X (Twitter) sobre o seguinte tema:")
        lines.append(f"  Tema: {topic}")
        lines.append(f"  Tom desejado: {tone}")
        if recent_drafts:
            lines.append("\nÚltimos posts publicados (evite repetir temas):")
            for i, d in enumerate(recent_drafts[:5], 1):
                lines.append(f"  {i}. {d[:120]}…")
        lines.append("\nInstruções:")
        lines.append("- Se o conteúdo couber em 280 caracteres, gere um post único.")
        lines.append("- Se precisar de mais espaço, gere uma thread separando cada tweet com a linha '---TWEET---'.")
        lines.append("- Siga rigorosamente as regras de formato da persona.")

    elif platform == "reddit":
        lines.append(f"Gere um comentário para o Reddit.")
        lines.append(f"  Subreddit alvo: r/{subreddit or 'brasil'}")
        lines.append(f"  Contexto do post original: {topic}")
        lines.append(f"  Tom desejado: {tone}")
        lines.append("\nInstruções:")
        lines.append("- Comece agregando valor genuíno. Mencione o PlanoEdu APENAS se for naturalmente relevante.")
        lines.append("- Comprimento ideal: 3–6 parágrafos.")
        lines.append("- Use formatação Reddit básica quando útil.")

    return "\n".join(lines)


def generate_draft(platform: str, topic: str, tone: str = "reflexivo",
                   subreddit: str = None) -> dict:
    """Chama a OpenRouter API e retorna o rascunho gerado."""
    persona = load_persona(platform)
    recent = storage.get_recent_drafts(platform, limit=10)
    user_prompt = build_user_prompt(platform, topic, tone, subreddit, recent)

    print(f"⚙  Gerando rascunho para [{platform}] — tema: {topic[:60]}…")

    response = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://github.com/PlanoEdu/O-social",  # Opcional para OpenRouter
            "X-Title": "O-Social Automation",
        },
        json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": persona},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": MAX_TOKENS,
        },
        timeout=60.0
    )

    if response.status_code != 200:
        print(f"✗ Erro na API do OpenRouter ({response.status_code}): {response.text}")
        raise RuntimeError(f"OpenRouter API error: {response.text}")

    result = response.json()
    draft = result["choices"][0]["message"]["content"].strip()
    usage = result.get("usage", {})

    prompt_context = json.dumps({
        "platform": platform, "topic": topic, "tone": tone,
        "model": MODEL, "input_tokens": usage.get("prompt_tokens"),
        "output_tokens": usage.get("completion_tokens")
    }, ensure_ascii=False)

    post_id = storage.create_post(
        platform=platform,
        draft=draft,
        prompt_used=user_prompt,
        context=prompt_context,
        tone=tone,
        subreddit=subreddit,
    )

    print(f"✓ Rascunho gerado — post_id={post_id}")
    print(f"\n{'─'*60}\n{draft}\n{'─'*60}\n")

    return {"post_id": post_id, "draft": draft, "platform": platform, "subreddit": subreddit}


def approve_and_publish(post_id: int):
    """Aprova e publica um rascunho. Chamado pelo bot Telegram ou CLI."""
    post = storage.get_post(post_id)
    if not post:
        print(f"✗ Post {post_id} não encontrado.")
        return

    if post["status"] != "PENDING":
        print(f"✗ Post {post_id} não está PENDING (status atual: {post['status']}).")
        return

    storage.update_post_status(post_id, "APPROVED")
    platform = post["platform"]
    draft = post["draft"]

    if DRY_RUN:
        print(f"🔵 DRY RUN — publicação simulada no {platform}.")
        storage.update_post_status(post_id, "PUBLISHED", platform_id="dry-run-id")
        return

    try:
        if platform == "x":
            platform_id = publish_x(draft)
        elif platform == "reddit":
            platform_id = publish_reddit(
                draft,
                subreddit=post.get("subreddit", "brasil"),
            )
        else:
            raise ValueError(f"Plataforma desconhecida: {platform}")

        storage.update_post_status(post_id, "PUBLISHED", platform_id=platform_id)
        print(f"✅ Publicado! platform_id={platform_id}")

    except Exception as e:
        print(f"✗ Erro ao publicar post {post_id}: {e}")
        storage.update_post_status(post_id, "PENDING")  # recoloca para revisão


def reject_post(post_id: int):
    storage.update_post_status(post_id, "REJECTED")
    print(f"✗ Post {post_id} rejeitado.")


# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    storage.init_db()
    storage.expire_old_drafts()

    parser = argparse.ArgumentParser(description="Social Media Automation Engine — Orchestrator")
    sub = parser.add_subparsers(dest="cmd")

    gen = sub.add_parser("generate", help="Gera um novo rascunho")
    gen.add_argument("--platform", required=True, choices=["x", "reddit"])
    gen.add_argument("--topic", required=True, help="Tema ou contexto do conteúdo")
    gen.add_argument("--tone", default="reflexivo",
                     choices=["reflexivo", "educacional", "provocativo", "empático"])
    gen.add_argument("--subreddit", default="brasil", help="Subreddit alvo (apenas Reddit)")
    gen.add_argument("--dry-run", action="store_true", help="Não publica, só gera")

    pub = sub.add_parser("publish", help="Aprova e publica um rascunho pelo ID")
    pub.add_argument("--id", type=int, required=True)

    rej = sub.add_parser("reject", help="Rejeita um rascunho pelo ID")
    rej.add_argument("--id", type=int, required=True)

    lst = sub.add_parser("list", help="Lista rascunhos pendentes")

    args = parser.parse_args()

    if args.cmd == "generate":
        if args.dry_run:
            os.environ["DRY_RUN"] = "true"
        result = generate_draft(args.platform, args.topic, args.tone, args.subreddit)
        print(f"\nPara aprovar e publicar: python orchestrator.py publish --id {result['post_id']}")

    elif args.cmd == "publish":
        approve_and_publish(args.id)

    elif args.cmd == "reject":
        reject_post(args.id)

    elif args.cmd == "list":
        pending = storage.list_pending_posts()
        if not pending:
            print("Nenhum rascunho pendente.")
        else:
            for p in pending:
                print(f"[{p['id']}] {p['platform']:6} | {p['tone']:14} | {p['created_at'][:16]} | {p['draft'][:80]}…")
    else:
        parser.print_help()
