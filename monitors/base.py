import json
import os
from pathlib import Path
from datetime import datetime

class BaseMonitor:
    def __init__(self, name: str, state_file: str = "monitor_state.json"):
        self.name = name
        self.state_dir = Path(__file__).parent.parent / ".antigravity" / "monitors"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_path = self.state_dir / state_file
        self.processed_ids = self._load_state()

    def _load_state(self) -> set:
        if self.state_path.exists():
            try:
                with open(self.state_path, "r") as f:
                    data = json.load(f)
                    return set(data.get(self.name, []))
            except Exception:
                return set()
        return set()

    def _save_state(self):
        state = {}
        if self.state_path.exists():
            try:
                with open(self.state_path, "r") as f:
                    state = json.load(f)
            except Exception:
                pass
        
        state[self.name] = list(self.processed_ids)
        with open(self.state_path, "w") as f:
            json.dump(state, f, indent=2)

    def is_processed(self, item_id: str) -> bool:
        return item_id in self.processed_ids

    def mark_as_processed(self, item_id: str):
        self.processed_ids.add(item_id)
        self._save_state()

    def log(self, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{self.name}] {message}")
