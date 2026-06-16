def add_todo_text(todos, text):
	text = text.strip()
	if not text:
		return False
	todos["active"].append(text)
	return True


def delete_todo(todos, list_name, index):
	del todos[list_name][index]


def complete_todo(todos, index):
	item = todos["active"].pop(index)
	todos["completed"].append(item)


def restore_todo(todos, index):
	item = todos["completed"].pop(index)
	todos["active"].append(item)
