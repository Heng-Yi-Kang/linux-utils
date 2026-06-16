# Linux Apps

Small desktop utilities for Linux.

## Apps

### Todo Popup

`todo/todo-popup` is a minimal GTK 4 todo window written in Python. It lets you add short todo items, mark them as done, and keeps the list between launches.

Data is stored at:

```text
~/.local/share/todo-popup.json
```

## Requirements

- Python 3
- GTK 4
- PyGObject / Python GObject introspection bindings

On Arch Linux:

```bash
sudo pacman -S python gtk4 python-gobject
```

On Debian or Ubuntu:

```bash
sudo apt install python3 python3-gi gir1.2-gtk-4.0
```

## Usage

Run the todo popup directly:

```bash
./todo/todo-popup
```

If the script is not executable:

```bash
chmod +x todo/todo-popup
./todo/todo-popup
```

## Installing Locally

To make the command available from your shell:

```bash
mkdir -p ~/.local/bin
ln -s "$(pwd)/todo/todo-popup" ~/.local/bin/todo-popup
```

Make sure `~/.local/bin` is in your `PATH`, then run:

```bash
todo-popup
```

## Notes

- The window is fixed size, borderless, and titled `Todo`.
- Press Enter in the input field or click `Add` to create a todo.
- Click `Done` next to an item to remove it from the list.
