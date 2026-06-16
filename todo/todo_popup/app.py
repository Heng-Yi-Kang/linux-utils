import os
from pathlib import Path

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk

from .actions import add_todo_text, complete_todo, delete_todo, restore_todo
from .storage import load_todos, save_todos
from .widgets import create_todo_list, refresh_todo_lists


ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
THEME_SYSTEM = "system"
THEME_LIGHT = "light"
THEME_DARK = "dark"
THEME_VALUES = {THEME_SYSTEM, THEME_LIGHT, THEME_DARK}

DEFAULT_THEME_CONFIG = {
	"TODO_THEME": THEME_SYSTEM,
	"TODO_LIGHT_FG": "#111827",
	"TODO_LIGHT_MUTED_ALPHA": "0.66",
	"TODO_LIGHT_SUBTLE_ALPHA": "0.56",
	"TODO_DARK_FG": "#f8fafc",
	"TODO_DARK_MUTED_ALPHA": "0.72",
	"TODO_DARK_SUBTLE_ALPHA": "0.62",
}


def parse_env_file(path):
	values = {}
	if not path.exists():
		return values

	for line in path.read_text(encoding="utf-8").splitlines():
		line = line.strip()
		if not line or line.startswith("#") or "=" not in line:
			continue
		key, value = line.split("=", 1)
		key = key.strip()
		value = value.strip().strip("\"'")
		if key:
			values[key] = value
	return values


def load_theme_config():
	env_file_values = parse_env_file(ENV_PATH)
	config = DEFAULT_THEME_CONFIG | env_file_values
	for key in DEFAULT_THEME_CONFIG:
		if key in os.environ:
			config[key] = os.environ[key]

	config["TODO_THEME"] = config["TODO_THEME"].strip().lower()
	if config["TODO_THEME"] not in THEME_VALUES:
		config["TODO_THEME"] = THEME_SYSTEM
	return config


def build_theme_css(config):
	theme = config["TODO_THEME"]
	light_fg = config["TODO_LIGHT_FG"]
	dark_fg = config["TODO_DARK_FG"]

	if theme == THEME_DARK:
		base_fg = dark_fg
		media_css = ""
	elif theme == THEME_LIGHT:
		base_fg = light_fg
		media_css = ""
	else:
		base_fg = light_fg
		media_css = f"""
@media (prefers-color-scheme: dark) {{
	window.todo-window {{
		--todo-fg: {dark_fg};
		--todo-muted-fg: alpha({dark_fg}, {config["TODO_DARK_MUTED_ALPHA"]});
		--todo-subtle-fg: alpha({dark_fg}, {config["TODO_DARK_SUBTLE_ALPHA"]});
	}}
}}
"""

	base_muted_alpha = config["TODO_DARK_MUTED_ALPHA"] if theme == THEME_DARK else config["TODO_LIGHT_MUTED_ALPHA"]
	base_subtle_alpha = config["TODO_DARK_SUBTLE_ALPHA"] if theme == THEME_DARK else config["TODO_LIGHT_SUBTLE_ALPHA"]

	return f"""
window.todo-window {{
	--todo-fg: {base_fg};
	--todo-muted-fg: alpha({base_fg}, {base_muted_alpha});
	--todo-subtle-fg: alpha({base_fg}, {base_subtle_alpha});
	background: @window_bg_color;
	color: var(--todo-fg);
}}

window.todo-window:backdrop {{
	color: var(--todo-fg);
}}
{media_css}
""" + """
.app-shell {
	background: @window_bg_color;
	color: var(--todo-fg);
	padding: 18px;
}

.title-label {
	color: var(--todo-fg);
	font-size: 22px;
	font-weight: 700;
}

.count-label,
.empty-state {
	color: var(--todo-muted-fg);
}

.count-label {
	font-size: 12px;
	font-weight: 600;
}

.input-row {
	background: alpha(currentColor, 0.045);
	border: 1px solid alpha(currentColor, 0.10);
	border-radius: 10px;
	color: var(--todo-fg);
	padding: 4px;
}

.todo-entry {
	background: transparent;
	border: 0;
	box-shadow: none;
	color: var(--todo-fg);
	min-height: 40px;
}

.todo-entry placeholder {
	color: var(--todo-subtle-fg);
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

.content-overlay {
	background: transparent;
}

.dock-row {
	background: alpha(@window_bg_color, 0.86);
	border: 1px solid alpha(currentColor, 0.12);
	border-radius: 18px;
	box-shadow: 0 10px 28px alpha(black, 0.20);
	color: var(--todo-fg);
	padding: 6px;
}

.dock-button {
	border-radius: 13px;
	color: var(--todo-fg);
	font-weight: 600;
	min-height: 44px;
	min-width: 112px;
	padding: 0 12px;
}

.dock-button:checked {
	background: #0d9488;
	color: white;
}

.dock-button:hover {
	background: alpha(currentColor, 0.08);
}

.dock-button:checked:hover {
	background: #0f766e;
}

.dock-button-content {
	padding: 2px 0;
}

.dock-label {
	font-size: 12px;
}

.list-frame {
	background: alpha(currentColor, 0.035);
	border: 1px solid alpha(currentColor, 0.08);
	border-radius: 12px;
	color: var(--todo-fg);
	padding: 6px;
}

.todo-list {
	background: transparent;
	color: var(--todo-fg);
}

.todo-row {
	border-radius: 9px;
	color: var(--todo-fg);
	margin: 2px;
}

.todo-row:selected {
	background: alpha(#0d9488, 0.16);
}

.todo-row-content {
	padding: 8px 9px;
}

.todo-label {
	color: var(--todo-fg);
	font-size: 14px;
}

.completed-label {
	color: var(--todo-subtle-fg);
}

.todo-check check:checked {
	background: #0d9488;
	border-color: #0d9488;
}

.delete-button {
	border-radius: 7px;
	color: var(--todo-subtle-fg);
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
		self.theme_config = load_theme_config()
		self.todos = load_todos()

	def do_startup(self):
		Gtk.Application.do_startup(self)
		if self.theme_config["TODO_THEME"] != THEME_SYSTEM:
			settings = Gtk.Settings.get_default()
			if settings:
				settings.set_property(
					"gtk-application-prefer-dark-theme",
					self.theme_config["TODO_THEME"] == THEME_DARK,
				)
		display = Gdk.Display.get_default()
		if display:
			provider = Gtk.CssProvider()
			provider.load_from_data(build_theme_css(self.theme_config).encode())
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

		def create_dock_button(icon_name, tooltip):
			button = Gtk.ToggleButton()
			button.add_css_class("dock-button")
			button.set_hexpand(True)
			button.set_tooltip_text(tooltip)

			content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
			content.add_css_class("dock-button-content")
			content.set_halign(Gtk.Align.CENTER)
			content.set_valign(Gtk.Align.CENTER)

			icon = Gtk.Image.new_from_icon_name(icon_name)
			icon.set_pixel_size(20)
			label = Gtk.Label()
			label.add_css_class("dock-label")

			content.append(icon)
			content.append(label)
			button.set_child(content)
			return button, label

		active_button, active_dock_label = create_dock_button("view-list-symbolic", "Show active todos")
		active_button.set_active(True)
		completed_button, completed_dock_label = create_dock_button(
			"emblem-ok-symbolic",
			"Show completed todos",
		)

		dock_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
		dock_row.add_css_class("dock-row")
		dock_row.set_halign(Gtk.Align.CENTER)
		dock_row.set_valign(Gtk.Align.END)
		dock_row.set_margin_bottom(12)
		dock_row.append(active_button)
		dock_row.append(completed_button)

		stack = Gtk.Stack()
		stack.add_css_class("content-stack")
		stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
		stack.set_vexpand(True)
		stack.set_margin_bottom(74)
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

		content_overlay = Gtk.Overlay()
		content_overlay.add_css_class("content-overlay")
		content_overlay.set_vexpand(True)
		content_overlay.set_child(stack)
		content_overlay.add_overlay(dock_row)

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
			active_dock_label.set_text(f"Active {active_count}")
			completed_dock_label.set_text(f"Done {completed_count}")
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
		box.append(content_overlay)

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
