import tkinter as tk
"""
source: 
https://blog.finxter.com/5-best-ways-to-display-a-message-when-hovering-over-something-with-mouse-cursor-in-tkinter-python/
"""


class CustomTooltip:

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.tooltip_window = None

    def enter(self, event=None):
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tooltip_window, text=self.text, justify='left',
                         background='#ffffff', relief='solid', borderwidth=1,
                         font=("tahoma", "12", "normal"))
        label.pack(ipadx=1)

    def leave(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()