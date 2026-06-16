import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk

from .actions import add_todo_text, complete_todo, delete_todo
from .storage import load_todos, save_todos
from .widgets import create_todo_list, refresh_todo_lists


class TodoApp(Gtk.Application):
	def __init__(self):
		super().__init__(application_id="com.yikang.todo.popup")
		self.todos = load_todos()

	def do_activate(self):
		window = Gtk.ApplicationWindow(application=self)
		window.set_title("Todo")
		window.set_default_size(320, 420)
		window.set_resizable(False)
		window.set_decorated(False)

		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
		box.set_margin_top(12)
		box.set_margin_bottom(12)
		box.set_margin_start(12)
		box.set_margin_end(12)

		entry = Gtk.Entry()
		entry.set_placeholder_text("Add new todo...")

		notebook = Gtk.Notebook()
		active_listbox = create_todo_list()
		completed_listbox = create_todo_list()
		notebook.append_page(active_listbox, Gtk.Label(label="Active"))
		notebook.append_page(completed_listbox, Gtk.Label(label="Completed"))

		def refresh():
			refresh_todo_lists(self.todos, active_listbox, completed_listbox)

		def add_todo(_):
			if add_todo_text(self.todos, entry.get_text()):
				save_todos(self.todos)
				entry.set_text("")
				refresh()

		entry.connect("activate", add_todo)

		def delete_selected():
			if notebook.get_current_page() == 0:
				selected_row = active_listbox.get_selected_row()
				if selected_row:
					delete_todo(self.todos, "active", selected_row.get_index())
			else:
				selected_row = completed_listbox.get_selected_row()
				if selected_row:
					delete_todo(self.todos, "completed", selected_row.get_index())
			if selected_row:
				save_todos(self.todos)
				refresh()

		def complete_selected():
			if notebook.get_current_page() != 0:
				return False
			selected_row = active_listbox.get_selected_row()
			if not selected_row:
				return False
			complete_todo(self.todos, selected_row.get_index())
			save_todos(self.todos)
			refresh()
			return True

		def key_pressed(controller, keyval, keycode, state):
			if window.get_focus() == entry:
				return False
			if keyval in (Gdk.KEY_Delete, Gdk.KEY_BackSpace, Gdk.KEY_d):
				delete_selected()
				return True
			if keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter, Gdk.KEY_space):
				return complete_selected()
			return False

		key_controller = Gtk.EventControllerKey()
		key_controller.connect("key-pressed", key_pressed)
		window.add_controller(key_controller)

		box.append(entry)
		box.append(notebook)

		window.set_child(box)
		refresh()
		window.present()

	def do_shutdown(self):
		save_todos(self.todos)
		super().do_shutdown()


def main():
	app = TodoApp()
	return app.run()
