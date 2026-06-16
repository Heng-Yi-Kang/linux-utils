import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


def create_todo_list():
	return Gtk.ListBox()


def clear_listbox(listbox):
	while child := listbox.get_first_child():
		listbox.remove(child)


def append_todo_row(listbox, todo):
	row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

	label = Gtk.Label(label=todo)
	label.set_xalign(0)
	label.set_hexpand(True)

	row_box.append(label)

	row = Gtk.ListBoxRow()
	row.set_child(row_box)
	listbox.append(row)


def refresh_todo_lists(todos, active_listbox, completed_listbox):
	clear_listbox(active_listbox)
	clear_listbox(completed_listbox)

	for todo in todos["active"]:
		append_todo_row(active_listbox, todo)

	for todo in todos["completed"]:
		append_todo_row(completed_listbox, todo)
