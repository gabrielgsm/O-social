# Social Media Automation Engine — PlanoEdu

Motor de automação de conteúdo para X (Twitter) e Reddit, usando Claude API e aprovação via Telegram.

## Arquitetura

```
Trigger (CLI / Cron)
       ↓
orchestrator.py  →  Claude API  →  Rascunho
       ↓
approval_bot.py (Telegram)
       ↓
publishers/x.py  ou  publishers/reddit.py
       ↓
storage.py (SQLite — auditoria completa)
```

## Setup

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar variáveis de ambiente
cp .env.example .env
# Edite o .env com suas chaves de API

# 3. Inicializar banco de dados
python storage.py

# 4. Inicializar infraestrutura da equipe (opcional)
python team_manager.py init
```

## Uso — Orchestrator CLI

```bash
# Gerar rascunho para X (sem publicar)
python orchestrator.py generate --platform x --topic "O que aprendi tentando automatizar meu negócio" --dry-run

# Gerar e publicar via aprovação Telegram
python orchestrator.py generate --platform x --topic "Decisões de arquitetura"

# Gerar para Reddit
python orchestrator.py generate --platform reddit --topic "Título do post que vou comentar" --subreddit brasil

# Listar rascunhos pendentes
python orchestrator.py list

# Aprovar e publicar pelo ID
python orchestrator.py publish --id 1

# Rejeitar pelo ID
python orchestrator.py reject --id 1
```

## Uso — Bot Telegram

```bash
python approval_bot.py
```

No Telegram:
- `/start` — Menu inicial
- `/pending` — Lista rascunhos aguardando aprovação
- `/generate x <tema>` — Gera rascunho para X
- `/generate reddit <tema>` — Gera rascunho para Reddit

## Variáveis de Ambiente Necessárias

| Variável | Descrição |
|---|---|
| `ANTHROPIC_API_KEY` | Chave da Claude API |
| `X_API_KEY` / `X_API_SECRET` | Credenciais X API v2 |
| `X_ACCESS_TOKEN` / `X_ACCESS_TOKEN_SECRET` | OAuth X |
| `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET` | App Reddit |
| `REDDIT_USERNAME` / `REDDIT_PASSWORD` | Conta Reddit |
| `TELEGRAM_BOT_TOKEN` | Token do BotFather |
| `TELEGRAM_CHAT_ID` | Seu chat ID no Telegram |
| `DRY_RUN` | `true` para simular sem publicar |

## Estrutura de Arquivos

```
O-social/
├── orchestrator.py       # Motor central
├── approval_bot.py       # Bot Telegram
├── storage.py            # SQLite
├── team_manager.py       # Equipe Gamaliel
├── prompts/
│   ├── persona_x.txt     # Persona para X
│   └── persona_reddit.txt
├── publishers/
│   ├── x.py              # X API v2
│   └── reddit.py         # PRAW
├── .env.example
├── requirements.txt
└── social.db             # Banco de dados (gerado automaticamente)
```

## Roadmap

- **Fase 2**: Monitors Reddit + X, Scheduler automático, histórico anti-repetição
- **Fase 3**: Dashboard web (Next.js), A/B testing de formatos, calendário editorial por IA
