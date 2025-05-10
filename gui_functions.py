
# gui_functions.py
# Utility functions for clearing and resetting GUI screens.

def clear_screen(root):
    """Remove all widgets from the root window."""
    for widget in root.winfo_children():
        widget.destroy()
