import json
import os
import sys
from datetime import datetime

TEAM_DIR = ".antigravity/team"


def init_team():
    """Inicializa a infraestrutura da equipe."""
    os.makedirs(f"{TEAM_DIR}/mailbox", exist_ok=True)
    os.makedirs(f"{TEAM_DIR}/locks", exist_ok=True)
    tasks_path = f"{TEAM_DIR}/tasks.json"
    if not os.path.exists(tasks_path):
        with open(tasks_path, "w") as f:
            json.dump({"tasks": [], "members": []}, f, indent=2)
    if not os.path.exists(f"{TEAM_DIR}/broadcast.msg"):
        with open(f"{TEAM_DIR}/broadcast.msg", "w") as f:
            f.write("")
    print("✓ Infraestrutura 'Equipe Gamaliel' pronta.")


def assign_task(title, assigned_to, deps=[]):
    """Atribui uma nova tarefa com suporte a dependências."""
    path = f"{TEAM_DIR}/tasks.json"
    with open(path, "r+") as f:
        data = json.load(f)
        task = {
            "id": len(data["tasks"]) + 1,
            "title": title,
            "status": "PENDING",
            "plan_approved": False,
            "assigned_to": assigned_to,
            "dependencies": deps,
            "created_at": datetime.utcnow().isoformat(),
        }
        data["tasks"].append(task)
        f.seek(0)
        f.truncate()
        json.dump(data, f, indent=2)
    print(f"✓ Tarefa {task['id']} ({title}) atribuída a {assigned_to}.")


def update_task_status(task_id, new_status):
    """Atualiza o status de uma tarefa pelo ID."""
    path = f"{TEAM_DIR}/tasks.json"
    valid_statuses = {"PENDING", "IN_PROGRESS", "BLOCKED", "COMPLETED"}
    if new_status not in valid_statuses:
        print(f"✗ Status inválido. Use: {valid_statuses}")
        return
    with open(path, "r+") as f:
        data = json.load(f)
        for task in data["tasks"]:
            if task["id"] == int(task_id):
                task["status"] = new_status
                task["updated_at"] = datetime.utcnow().isoformat()
                print(f"✓ Tarefa {task_id} atualizada para {new_status}.")
                break
        else:
            print(f"✗ Tarefa {task_id} não encontrada.")
        f.seek(0)
        f.truncate()
        json.dump(data, f, indent=2)


def list_tasks():
    """Exibe todas as tarefas com seus estados."""
    path = f"{TEAM_DIR}/tasks.json"
    with open(path, "r") as f:
        data = json.load(f)
    if not data["tasks"]:
        print("Nenhuma tarefa registrada.")
        return
    print(f"\n{'ID':<5} {'Status':<15} {'Agente':<20} {'Título'}")
    print("-" * 70)
    for t in data["tasks"]:
        deps = f" [deps: {t['dependencies']}]" if t["dependencies"] else ""
        approved = " ✅" if t.get("plan_approved") else ""
        print(f"{t['id']:<5} {t['status']:<15} {t['assigned_to']:<20} {t['title']}{deps}{approved}")


def broadcast(sender, text):
    """Envia uma mensagem para todos os membros da equipe."""
    msg = {
        "de": sender,
        "tipo": "BROADCAST",
        "timestamp": datetime.utcnow().isoformat(),
        "mensagem": text,
    }
    with open(f"{TEAM_DIR}/broadcast.msg", "a") as f:
        f.write(json.dumps(msg, ensure_ascii=False) + "\n")
    print(f"✓ Mensagem global enviada por {sender}.")


def send_message(sender, receiver, text):
    """Envia uma mensagem para a caixa de entrada de um agente específico."""
    msg = {
        "de": sender,
        "timestamp": datetime.utcnow().isoformat(),
        "mensagem": text,
    }
    with open(f"{TEAM_DIR}/mailbox/{receiver}.msg", "a") as f:
        f.write(json.dumps(msg, ensure_ascii=False) + "\n")
    print(f"✓ Mensagem enviada para {receiver}.")


def lock_file(filename, agent):
    """Cria um semáforo para evitar edição simultânea de um arquivo."""
    lock_path = f"{TEAM_DIR}/locks/{filename.replace('/', '_')}.lock"
    if os.path.exists(lock_path):
        with open(lock_path) as f:
            holder = f.read()
        print(f"✗ Arquivo já bloqueado por: {holder}")
        return False
    with open(lock_path, "w") as f:
        f.write(f"{agent} @ {datetime.utcnow().isoformat()}")
    print(f"✓ Lock adquirido em '{filename}' por {agent}.")
    return True


def unlock_file(filename):
    """Remove o semáforo de um arquivo."""
    lock_path = f"{TEAM_DIR}/locks/{filename.replace('/', '_')}.lock"
    if os.path.exists(lock_path):
        os.remove(lock_path)
        print(f"✓ Lock removido de '{filename}'.")
    else:
        print(f"✗ Nenhum lock encontrado para '{filename}'.")


def approve_plan(task_id):
    """Gamaliel aprova o plano de um agente."""
    path = f"{TEAM_DIR}/tasks.json"
    with open(path, "r+") as f:
        data = json.load(f)
        for task in data["tasks"]:
            if task["id"] == int(task_id):
                task["plan_approved"] = True
                task["updated_at"] = datetime.utcnow().isoformat()
                print(f"✓ Plano da tarefa {task_id} aprovado por Gamaliel.")
                break
        else:
            print(f"✗ Tarefa {task_id} não encontrada.")
        f.seek(0)
        f.truncate()
        json.dump(data, f, indent=2)


# ─── Seed: Popula as tarefas da Fase 1 (MVP) ─────────────────────────────────

def seed_phase1():
    """Adiciona todas as tarefas da Fase 1 (MVP) ao tasks.json."""
    tasks = [
        ("Definir estrutura de pastas e contratos de módulo", "Arquiteto", []),
        ("Orchestrator básico — trigger, contexto, Claude API", "Backend", [1]),
        ("Prompts de persona: X e Reddit", "Backend", [1]),
        ("Bot Telegram — fila de aprovação (aprovar/rejeitar/regerar)", "Backend", [2, 3]),
        ("Publisher X — post simples e thread via X API v2", "Backend", [4]),
        ("Publisher Reddit — comentário em post existente via PRAW", "Backend", [4]),
        ("Storage SQLite — schema de logs e histórico", "Backend", [1]),
        ("Revisão de segurança: credenciais, rate limits, auditabilidade", "Neo", [5, 6, 7]),
    ]
    for title, agent, deps in tasks:
        assign_task(title, agent, deps)
    print("\n✓ Fase 1 (MVP) semeada com sucesso!")


# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python team_manager.py <comando> [args]")
        print("Comandos: init, seed, list, assign, update, approve, broadcast, msg, lock, unlock")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "init":
        init_team()
    elif cmd == "seed":
        seed_phase1()
    elif cmd == "list":
        list_tasks()
    elif cmd == "assign":
        # python team_manager.py assign "Título" "Agente" [dep1,dep2]
        title = sys.argv[2]
        agent = sys.argv[3]
        deps = [int(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 else []
        assign_task(title, agent, deps)
    elif cmd == "update":
        update_task_status(sys.argv[2], sys.argv[3])
    elif cmd == "approve":
        approve_plan(sys.argv[2])
    elif cmd == "broadcast":
        broadcast(sys.argv[2], sys.argv[3])
    elif cmd == "msg":
        send_message(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "lock":
        lock_file(sys.argv[2], sys.argv[3])
    elif cmd == "unlock":
        unlock_file(sys.argv[2])
    else:
        print(f"✗ Comando desconhecido: {cmd}")
