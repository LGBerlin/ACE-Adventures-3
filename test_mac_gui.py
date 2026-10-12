"""Live desktop smoke checks: run on the macOS build runner.

Unlike syntax tests, these instantiate the real illustrated Tk application.
"""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    import tkinter as tk
except ImportError:
    tk=None

class LiveDesktopTests(unittest.TestCase):
    @unittest.skipUnless(tk is not None, 'Tk unavailable')
    def test_actual_illustrated_window_and_navigation(self):
        try:
            probe=tk.Tk()
            probe.withdraw()
            probe.update_idletasks()
            probe.destroy()
        except (tk.TclError,RuntimeError) as exc:
            self.skipTest('No graphical desktop: '+str(exc))
        import app
        with tempfile.TemporaryDirectory() as temp, patch.object(app,'DATA',Path(temp)):
            window=app.App()
            try:
                self.assertIn('ACE Adventures',window.title())
                window.update_idletasks()
                window._new()
                window.update_idletasks()
                self.assertIsNone(window.c)
                window._connections()
                window.update_idletasks()
                dialogs=[child for child in window.winfo_children() if isinstance(child,tk.Toplevel)]
                self.assertTrue(dialogs,'AI Connections must open a real window')
                for child in dialogs:child.destroy()
                window._home()
                window.update_idletasks()
            finally:
                window.destroy()
if __name__=='__main__':unittest.main()
