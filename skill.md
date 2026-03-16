# Skill: Equipe Gamaliel (Multi-Agente)

Esta habilidade permite ao Antigravity coordenar uma equipe de agentes inteligentes trabalhando em paralelo no mesmo projeto, replicando a funcionalidade de "Agent Teams" do Claude Code.

## Configuração do Ambiente
A equipe utiliza uma pasta oculta na raiz do projeto para se comunicar:
- `.antigravity/team/tasks.json` → Lista mestra de tarefas, estados e dependências.
- `.antigravity/team/mailbox/` → Mensagens individuais (.msg).
- `.antigravity/team/broadcast.msg` → Mensagens globais para toda a equipe.
- `.antigravity/team/locks/` → Semáforos para evitar edição simultânea de arquivos.

## Papéis da Equipe
1. **Diretor (Gamaliel)**: O líder. Divide o problema, atribui papéis e aprova planos.
2. **Arquiteto**: Define a estrutura e padrões antes de codificar.
3. **Especialista (Frontend/Backend/DB)**: Executa tarefas técnicas específicas.
4. **Marketer**: Criação de marca, logos, copywriting e design de landing pages.
5. **Pesquisador**: Busca de informações, documentação e análise de mercado.
6. **Revisor (Neo)**: Busca falhas, bugs e problemas de segurança.

## Protocolo de Orquestração Avançada

### 1. Modo de Planejamento (Gatekeeping)
Antes de realizar mudanças significativas, cada agente deve enviar um **Plano de Ação** para a caixa de entrada do Gamaliel.
- O agente permanece no modo `READ_ONLY` ou `PLANNING` até que Gamaliel responda com uma mensagem de `APPROVED`.

### 2. Mensagens e Difusão (Broadcast)
- **Mensagem Direta**: Coordenação 1 a 1 entre especialistas.
- **Broadcast**: Gamaliel pode escrever em `broadcast.msg` para dar novas diretrizes a toda a equipe simultaneamente.

### 3. Sincronização de Tarefas e Dependências
- As tarefas em `tasks.json` podem ter uma lista de `dependencies`. Uma IA não deve reivindicar uma tarefa se suas dependências não estiverem com o estado `COMPLETED`.

## Regras Críticas
- NUNCA editar um arquivo se houver um .lock ativo em `.antigravity/team/locks/`.
- Ao concluir uma tarefa, o agente deve liberar seus "locks" e notificar o Gamaliel.

---

## 3. Script de Orquestração (team_manager.py)
*Este script automatiza o gerenciamento das tarefas e a comunicação. Salve-o como `team_manager.py`.*

```python
import json
import os
import sys

TEAM_DIR = ".antigravity/team"

def init_team():
    """Inicializa a infraestrutura da equipe."""
    os.makedirs(f"{TEAM_DIR}/mailbox", exist_ok=True)
    os.makedirs(f"{TEAM_DIR}/locks", exist_ok=True)
    tasks_path = f"{TEAM_DIR}/tasks.json"
    if not os.path.exists(tasks_path):
        with open(tasks_path, 'w') as f:
            json.dump({"tasks": [], "members": []}, f, indent=2)
    if not os.path.exists(f"{TEAM_DIR}/broadcast.msg"):
        with open(f"{TEAM_DIR}/broadcast.msg", 'w') as f: f.write("")
    print("✓ Infraestrutura 'Equipe Gamaliel' pronta.")

def assign_task(title, assigned_to, deps=[]):
    """Atribui uma nova tarefa com suporte a dependências."""
    path = f"{TEAM_DIR}/tasks.json"
    with open(path, 'r+') as f:
        data = json.load(f)
        task = {
            "id": len(data["tasks"]) + 1,
            "title": title,
            "status": "PENDING",
            "plan_approved": False,
            "assigned_to": assigned_to,
            "dependencies": deps
        }
        data["tasks"].append(task)
        f.seek(0)
        json.dump(data, f, indent=2)
    print(f"✓ Tarefa {task['id']} ({title}) atribuída a {assigned_to}.")

def broadcast(sender, text):
    """Envia uma mensagem para todos os membros da equipe."""
    msg = {"de": sender, "tipo": "BROADCAST", "mensagem": text}
    with open(f"{TEAM_DIR}/broadcast.msg", 'a') as f:
        f.write(json.dumps(msg) + "\n")
    print(f"✓ Mensagem global enviada por {sender}.")

def send_message(sender, receiver, text):
    """Envia uma mensagem para a caixa de entrada de um agente específico."""
    msg = {"de": sender, "mensagem": text}
    with open(f"{TEAM_DIR}/mailbox/{receiver}.msg", 'a') as f:
        f.write(json.dumps(msg) + "\n")
    print(f"✓ Mensagem enviada para {receiver}.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "init": init_team()
```

---

## 4. Como usar
1. **Ative o Líder**: Peça ao Antigravity: *"Use a habilidade Equipe Gamaliel para inicializar este projeto"*.
2. **Divida o trabalho**: **Gamaliel** dividirá o trabalho. Abra terminais novos para cada agente (Frontend, Marketer, etc.).
3. **Fluxo de Planejamento**: Os agentes enviam seus planos ao Gamaliel antes de começar. Uma equipe bem coordenada é imbatível.

---
