import json
import os

TODO_FILE = os.path.expanduser("~/.local/share/todo-popup.json")


def ensure_storage_dir():
	os.makedirs(os.path.dirname(TODO_FILE), exist_ok=True)


def load_todos():
	ensure_storage_dir()
	if not os.path.exists(TODO_FILE):
		return {"active": [], "completed": []}
	with open(TODO_FILE, "r", encoding="utf-8") as f:
		data = json.load(f)
	if isinstance(data, list):
		return {"active": data, "completed": []}
	return {
		"active": data.get("active", []),
		"completed": data.get("completed", []),
	}


def save_todos(todos):
	ensure_storage_dir()
	with open(TODO_FILE, "w", encoding="utf-8") as f:
		json.dump(todos, f, indent=2)
