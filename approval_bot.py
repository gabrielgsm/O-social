"""
approval_bot.py — Bot Telegram para Fila de Aprovação
O founder recebe rascunhos e pode Aprovar / Rejeitar / Regerar com um toque.
"""
import os
import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes
)
from dotenv import load_dotenv
import storage
import orchestrator

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID", "0"))

logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=os.getenv("LOG_LEVEL", "INFO"),
)
logger = logging.getLogger(__name__)


# ─── Formatação de rascunho ───────────────────────────────────────────────────

def format_draft_message(post: dict) -> str:
    platform_emoji = "🐦" if post["platform"] == "x" else "🤖"
    tone_map = {
        "reflexivo": "💭", "educacional": "📚",
        "provocativo": "🔥", "empático": "🤝"
    }
    tone_icon = tone_map.get(post.get("tone", ""), "")
    subreddit_line = f"\n📍 *Subreddit:* r/{post['subreddit']}" if post.get("subreddit") else ""
    expires = post.get("expires_at", "")[:16] if post.get("expires_at") else "—"

    return (
        f"{platform_emoji} *Novo Rascunho — {post['platform'].upper()}*\n"
        f"{subreddit_line}\n"
        f"{tone_icon} *Tom:* {post.get('tone', '—')}\n"
        f"🕐 *Expira em:* {expires} UTC\n"
        f"🆔 *ID:* `{post['id']}`\n"
        f"{'─' * 30}\n\n"
        f"{post['draft']}"
    )


def approval_keyboard(post_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Aprovar e Publicar", callback_data=f"approve:{post_id}"),
            InlineKeyboardButton("❌ Rejeitar", callback_data=f"reject:{post_id}"),
        ],
        [
            InlineKeyboardButton("🔁 Regerar", callback_data=f"regenerate:{post_id}"),
        ]
    ])


# ─── Handlers ────────────────────────────────────────────────────────────────

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 *Social Media Bot — PlanoEdu*\n\n"
        "Comandos disponíveis:\n"
        "/pending — Lista rascunhos aguardando aprovação\n"
        "/generate x <tema> — Gera rascunho para X\n"
        "/generate reddit <tema> — Gera rascunho para Reddit",
        parse_mode="Markdown"
    )


async def list_pending(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    posts = storage.list_pending_posts()
    if not posts:
        await update.message.reply_text("✅ Nenhum rascunho pendente.")
        return

    for post in posts:
        msg = format_draft_message(post)
        await update.message.reply_text(
            msg,
            parse_mode="Markdown",
            reply_markup=approval_keyboard(post["id"]),
        )


async def generate_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """
    /generate x Sobre automação de processos
    /generate reddit Preciso de ajuda com BNCC
    """
    args = ctx.args
    if len(args) < 2:
        await update.message.reply_text(
            "Uso: /generate <plataforma> <tema>\n"
            "Exemplo: /generate x Sobre automação de processos"
        )
        return

    platform = args[0].lower()
    if platform not in ("x", "reddit"):
        await update.message.reply_text("Plataforma inválida. Use 'x' ou 'reddit'.")
        return

    topic = " ".join(args[1:])
    await update.message.reply_text(f"⚙️ Gerando rascunho para *{platform}*…", parse_mode="Markdown")

    try:
        result = orchestrator.generate_draft(platform=platform, topic=topic)
        post = storage.get_post(result["post_id"])
        msg = format_draft_message(post)
        await update.message.reply_text(
            msg,
            parse_mode="Markdown",
            reply_markup=approval_keyboard(post["id"]),
        )
    except Exception as e:
        logger.exception("Erro ao gerar rascunho")
        await update.message.reply_text(f"❌ Erro: {e}")


async def handle_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action, post_id_str = query.data.split(":", 1)
    post_id = int(post_id_str)
    post = storage.get_post(post_id)

    if not post:
        await query.edit_message_text("⚠️ Post não encontrado.")
        return

    if action == "approve":
        await query.edit_message_text(f"⏳ Publicando post #{post_id}…")
        try:
            orchestrator.approve_and_publish(post_id)
            updated = storage.get_post(post_id)
            pid = updated.get("platform_id", "—")
            await query.edit_message_text(
                f"✅ *Publicado!*\n🆔 Post #{post_id}\n📌 platform_id: `{pid}`",
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.exception("Erro ao publicar")
            await query.edit_message_text(f"❌ Erro ao publicar: {e}")

    elif action == "reject":
        orchestrator.reject_post(post_id)
        await query.edit_message_text(f"❌ Post #{post_id} rejeitado.")

    elif action == "regenerate":
        await query.edit_message_text(f"🔁 Regerando post #{post_id}…")
        try:
            # Regera com mesmo contexto do post original
            import json
            ctx_data = json.loads(post.get("context") or "{}")
            result = orchestrator.generate_draft(
                platform=post["platform"],
                topic=ctx_data.get("topic", "Mesmo tema do post rejeitado"),
                tone=post.get("tone", "reflexivo"),
                subreddit=post.get("subreddit"),
            )
            orchestrator.reject_post(post_id)  # Rejeita o antigo
            new_post = storage.get_post(result["post_id"])
            msg = format_draft_message(new_post)
            await ctx.bot.send_message(
                chat_id=CHAT_ID,
                text=msg,
                parse_mode="Markdown",
                reply_markup=approval_keyboard(new_post["id"]),
            )
            await query.edit_message_text(f"🔁 Novo rascunho gerado (ID: {new_post['id']}). Verifique a mensagem acima.")
        except Exception as e:
            logger.exception("Erro ao regerar")
            await query.edit_message_text(f"❌ Erro ao regerar: {e}")


# ─── Notificação proativa ─────────────────────────────────────────────────────

async def notify_new_draft(app: Application, post_id: int):
    """Chamado externamente (pelo orchestrator) para enviar rascunho ao Telegram."""
    post = storage.get_post(post_id)
    if not post:
        return
    msg = format_draft_message(post)
    await app.bot.send_message(
        chat_id=CHAT_ID,
        text=msg,
        parse_mode="Markdown",
        reply_markup=approval_keyboard(post_id),
    )


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    storage.init_db()
    storage.expire_old_drafts()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("pending", list_pending))
    app.add_handler(CommandHandler("generate", generate_command))
    app.add_handler(CallbackQueryHandler(handle_callback))

    logger.info("🤖 Bot de aprovação iniciado…")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
