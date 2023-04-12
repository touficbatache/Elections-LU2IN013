import unittest
import tkinter as tk
from tooltip import Tooltip


class TestTooltip(unittest.TestCase):
    def setUp(self) -> None:
        self.window = tk.Toplevel(tk.Tk())
        self.widget = tk.Label(self.window, text="label")
        Tooltip(self.widget)

    def test_tooltip_attributes(self):
        return

    def tearDown(self):
        return
