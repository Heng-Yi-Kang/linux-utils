import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk

from .actions import add_todo_text, complete_todo, delete_todo, restore_todo
from .storage import load_todos, save_todos
from .widgets import create_todo_list, refresh_todo_lists


APP_CSS = """
window.todo-window {
	background: @window_bg_color;
	color: @window_fg_color;
}

.app-shell {
	background: @window_bg_color;
	padding: 18px;
}

.title-label {
	font-size: 22px;
	font-weight: 700;
}

.count-label,
.empty-state {
	color: alpha(currentColor, 0.62);
}

.count-label {
	font-size: 12px;
	font-weight: 600;
}

.input-row {
	background: alpha(currentColor, 0.045);
	border: 1px solid alpha(currentColor, 0.10);
	border-radius: 10px;
	padding: 4px;
}

.todo-entry {
	background: transparent;
	border: 0;
	box-shadow: none;
	min-height: 40px;
}

.todo-entry:focus {
	box-shadow: inset 0 -2px #0d9488;
}

.add-button {
	border-radius: 8px;
	min-height: 36px;
	min-width: 36px;
	color: #0d9488;
}

.segment-row {
	background: alpha(currentColor, 0.055);
	border-radius: 10px;
	padding: 3px;
}

.segment-button {
	border-radius: 8px;
	font-weight: 600;
	min-height: 34px;
}

.segment-button:checked {
	background: #0d9488;
	color: white;
}

.list-frame {
	background: alpha(currentColor, 0.035);
	border: 1px solid alpha(currentColor, 0.08);
	border-radius: 12px;
	padding: 6px;
}

.todo-list {
	background: transparent;
}

.todo-row {
	border-radius: 9px;
	margin: 2px;
}

.todo-row:selected {
	background: alpha(#0d9488, 0.16);
}

.todo-row-content {
	padding: 8px 9px;
}

.todo-label {
	font-size: 14px;
}

.completed-label {
	color: alpha(currentColor, 0.55);
}

.todo-check check:checked {
	background: #0d9488;
	border-color: #0d9488;
}

.delete-button {
	border-radius: 7px;
	color: alpha(currentColor, 0.55);
	min-height: 30px;
	min-width: 30px;
}

.delete-button:hover {
	background: alpha(#ef4444, 0.12);
	color: #dc2626;
}

.empty-row {
	margin: 24px 8px;
}

.empty-state {
	font-size: 13px;
	padding: 24px 18px;
}
"""


class TodoApp(Gtk.Application):
	def __init__(self):
		super().__init__(application_id="com.yikang.todo.popup")
		self.todos = load_todos()

	def do_startup(self):
		Gtk.Application.do_startup(self)
		display = Gdk.Display.get_default()
		if display:
			provider = Gtk.CssProvider()
			provider.load_from_data(APP_CSS.encode())
			Gtk.StyleContext.add_provider_for_display(
				display,
				provider,
				Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
			)

	def do_activate(self):
		window = Gtk.ApplicationWindow(application=self)
		window.add_css_class("todo-window")
		window.set_title("Todo")
		window.set_default_size(380, 520)
		window.set_resizable(False)
		window.set_decorated(False)

		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
		box.add_css_class("app-shell")

		header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
		title = Gtk.Label(label="Todo")
		title.add_css_class("title-label")
		title.set_xalign(0)
		title.set_hexpand(True)
		count_label = Gtk.Label()
		count_label.add_css_class("count-label")
		header.append(title)
		header.append(count_label)

		entry = Gtk.Entry()
		entry.add_css_class("todo-entry")
		entry.set_placeholder_text("Add new todo")
		entry.set_hexpand(True)

		add_button = Gtk.Button.new_from_icon_name("list-add-symbolic")
		add_button.add_css_class("add-button")
		add_button.add_css_class("flat")
		add_button.set_tooltip_text("Add todo")

		input_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
		input_row.add_css_class("input-row")
		input_row.append(entry)
		input_row.append(add_button)

		active_button = Gtk.ToggleButton()
		active_button.add_css_class("segment-button")
		active_button.set_hexpand(True)
		active_button.set_active(True)
		completed_button = Gtk.ToggleButton()
		completed_button.add_css_class("segment-button")
		completed_button.set_hexpand(True)

		segment_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
		segment_row.add_css_class("segment-row")
		segment_row.append(active_button)
		segment_row.append(completed_button)

		stack = Gtk.Stack()
		stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
		stack.set_vexpand(True)
		active_listbox = create_todo_list()
		completed_listbox = create_todo_list()

		active_scroller = Gtk.ScrolledWindow()
		active_scroller.add_css_class("list-frame")
		active_scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
		active_scroller.set_child(active_listbox)

		completed_scroller = Gtk.ScrolledWindow()
		completed_scroller.add_css_class("list-frame")
		completed_scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
		completed_scroller.set_child(completed_listbox)

		stack.add_named(active_scroller, "active")
		stack.add_named(completed_scroller, "completed")

		def selected_list_name():
			return stack.get_visible_child_name()

		def set_visible_list(name):
			stack.set_visible_child_name(name)
			active_button.set_active(name == "active")
			completed_button.set_active(name == "completed")

		active_button.connect("clicked", lambda _button: set_visible_list("active"))
		completed_button.connect("clicked", lambda _button: set_visible_list("completed"))

		def refresh():
			active_count = len(self.todos["active"])
			completed_count = len(self.todos["completed"])
			count_label.set_text(f"{active_count} active")
			active_button.set_label(f"Active {active_count}")
			completed_button.set_label(f"Completed {completed_count}")
			refresh_todo_lists(
				self.todos,
				active_listbox,
				completed_listbox,
				complete_at,
				restore_at,
				delete_at,
			)

		def add_todo(_widget=None):
			if add_todo_text(self.todos, entry.get_text()):
				save_todos(self.todos)
				entry.set_text("")
				set_visible_list("active")
				refresh()

		entry.connect("activate", add_todo)
		add_button.connect("clicked", add_todo)

		def complete_at(index):
			complete_todo(self.todos, index)
			save_todos(self.todos)
			refresh()

		def restore_at(index):
			restore_todo(self.todos, index)
			save_todos(self.todos)
			refresh()

		def delete_at(list_name, index):
			delete_todo(self.todos, list_name, index)
			save_todos(self.todos)
			refresh()

		def delete_selected():
			selected_row = None
			if selected_list_name() == "active":
				selected_row = active_listbox.get_selected_row()
				if selected_row:
					delete_at("active", selected_row.get_index())
			else:
				selected_row = completed_listbox.get_selected_row()
				if selected_row:
					delete_at("completed", selected_row.get_index())
			return selected_row is not None

		def toggle_selected():
			if selected_list_name() == "active":
				selected_row = active_listbox.get_selected_row()
				if not selected_row:
					return False
				complete_at(selected_row.get_index())
				return True
			selected_row = completed_listbox.get_selected_row()
			if not selected_row:
				return False
			restore_at(selected_row.get_index())
			return True

		def key_pressed(controller, keyval, keycode, state):
			if window.get_focus() == entry:
				return False
			if keyval in (Gdk.KEY_Delete, Gdk.KEY_BackSpace, Gdk.KEY_d):
				return delete_selected()
			if keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter, Gdk.KEY_space):
				return toggle_selected()
			return False

		key_controller = Gtk.EventControllerKey()
		key_controller.connect("key-pressed", key_pressed)
		window.add_controller(key_controller)

		box.append(header)
		box.append(input_row)
		box.append(segment_row)
		box.append(stack)

		window.set_child(box)
		refresh()
		window.present()
		entry.grab_focus()

	def do_shutdown(self):
		save_todos(self.todos)
		Gtk.Application.do_shutdown(self)


def main():
	app = TodoApp()
	return app.run()
