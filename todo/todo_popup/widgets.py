import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Pango


def create_todo_list():
	listbox = Gtk.ListBox()
	listbox.add_css_class("todo-list")
	listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
	return listbox


def clear_listbox(listbox):
	while child := listbox.get_first_child():
		listbox.remove(child)


def create_empty_row(message):
	label = Gtk.Label(label=message)
	label.add_css_class("empty-state")
	label.set_wrap(True)
	label.set_justify(Gtk.Justification.CENTER)
	label.set_xalign(0.5)

	row = Gtk.ListBoxRow()
	row.add_css_class("empty-row")
	row.set_selectable(False)
	row.set_activatable(False)
	row.set_child(label)
	return row


def append_todo_row(listbox, todo, completed, on_toggle, on_delete):
	row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
	row_box.add_css_class("todo-row-content")

	checkbox = Gtk.CheckButton()
	checkbox.set_active(completed)
	checkbox.set_tooltip_text("Restore todo" if completed else "Complete todo")
	checkbox.add_css_class("todo-check")

	label = Gtk.Label(label=todo)
	label.set_xalign(0)
	label.set_hexpand(True)
	label.set_wrap(True)
	label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
	label.add_css_class("todo-label")

	if completed:
		attrs = Pango.AttrList()
		attrs.insert(Pango.attr_strikethrough_new(True))
		label.set_attributes(attrs)
		label.add_css_class("completed-label")

	delete_button = Gtk.Button.new_from_icon_name("user-trash-symbolic")
	delete_button.set_tooltip_text("Delete todo")
	delete_button.add_css_class("delete-button")
	delete_button.add_css_class("flat")
	delete_button.set_focus_on_click(False)

	row_box.append(checkbox)
	row_box.append(label)
	row_box.append(delete_button)

	checkbox.connect("toggled", lambda _button: on_toggle())
	delete_button.connect("clicked", lambda _button: on_delete())

	row = Gtk.ListBoxRow()
	row.add_css_class("todo-row")
	row.set_child(row_box)
	listbox.append(row)


def refresh_todo_lists(todos, active_listbox, completed_listbox, on_complete, on_restore, on_delete):
	clear_listbox(active_listbox)
	clear_listbox(completed_listbox)

	if todos["active"]:
		for index, todo in enumerate(todos["active"]):
			append_todo_row(
				active_listbox,
				todo,
				False,
				lambda index=index: on_complete(index),
				lambda index=index: on_delete("active", index),
			)
	else:
		active_listbox.append(create_empty_row("Nothing active. Add a todo to get started."))

	if todos["completed"]:
		for index, todo in enumerate(todos["completed"]):
			append_todo_row(
				completed_listbox,
				todo,
				True,
				lambda index=index: on_restore(index),
				lambda index=index: on_delete("completed", index),
			)
	else:
		completed_listbox.append(create_empty_row("Completed todos will appear here."))
