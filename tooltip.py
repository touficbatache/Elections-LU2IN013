from tkinter import *


class Tooltip(object):
    def __init__(self, widget):
        self.widget = widget
        self.window = None
        self.id = None
        self.x = self.y = 0
        self.text = None

    def show(self, text):
        """Display text in tooltip window""" ""
        self.text = text

        if self.window or not self.text:
            return

        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() + 27

        self.window = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(
            tw,
            text=self.text,
            justify=LEFT,
            background="#ffffff",
            relief=SOLID,
            borderwidth=1,
            font=("Mistral", "13", "normal"),
        )
        label.pack(ipadx=4)

    def hide(self):
        tw = self.window
        self.window = None
        if tw:
            tw.destroy()


def bind_tooltip(widget, text):
    tooltip = Tooltip(widget)

    def enter(event):
        tooltip.show(text)

    def leave(event):
        tooltip.hide()

    widget.bind("<Enter>", enter)
    widget.bind("<Leave>", leave)
