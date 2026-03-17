# Task: Orquestração PRD — Social Media Automation Engine

## Fase 0 — Inicialização (Gamaliel)
- [x] Ler skill.md e entender protocolo da Equipe Gamaliel
- [x] Ler PRD (PlanoEdu_PRD_SocialMediaEngine.docx)
- [x] Criar task.md e implementation_plan.md
- [x] Inicializar infraestrutura `.antigravity/team/` no projeto
- [x] Criar team_manager.py e executar `init`
- [x] Montar tasks.json com todas as tarefas do MVP (Fase 1)
- [x] Enviar broadcast inicial para a equipe com contexto do projeto

## Fase 1 — MVP (Arquiteto + Especialistas)
- [x] **Arquiteto**: Definir estrutura de pastas e módulos do projeto Python
- [x] **Backend 1**: Orchestrator básico (recebe trigger, monta contexto, chama Claude API)
- [x] **Backend 2**: Prompt base de persona (X) e regras de comunidade (Reddit)
- [/] **Backend 3**: Bot Telegram para fila de aprovação (aprovar / rejeitar)
- [x] **Backend 4**: Publisher X — post simples e thread via X API v2
- [x] **Backend 5**: Publisher Reddit — comentário em post existente via PRAW
- [x] **Backend 6**: Logs em SQLite (gerado, aprovado, rejeitado, publicado)
- [x] **Revisor (Neo)**: Revisar segurança (credenciais, rate limits, auditabilidade)

## Fase 2 — Automação (Backlog)
- [ ] Monitor Reddit (polling 15min por subreddits relevantes)
- [ ] Monitor X (trends e menções)
- [ ] Scheduler com horários otimizados por plataforma
- [ ] Histórico de posts para evitar repetição de tema
- [ ] Coleta de métricas pós-publicação

## Fase 3 — Inteligência (Futuro)
- [ ] Dashboard web (Next.js) com histórico, aprovações e métricas
- [ ] A/B testing de formatos de post
- [ ] Calendário editorial gerado por IA

## Verificação
- [x] Rodar `python team_manager.py init` e verificar pastas
- [x] Verificação de sintaxe em todos os arquivos Python
- [x] SQLite inicializado com tabelas `posts` e `engagements`
- [x] tasks.json com todas as tarefas COMPLETED
- [ ] Teste end-to-end com `.env` configurado (aguarda chaves de API do usuário)
