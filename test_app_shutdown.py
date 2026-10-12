import unittest
from unittest.mock import patch
import tkinter as tk
import app
class AppShutdownTests(unittest.TestCase):
 def test_repeated_create_destroy_cancels_timers(self):
  try:
   with patch.object(app.ai_connections,'all_statuses',return_value={}):
    for _ in range(3):
     win=app.App()
     win.withdraw()
     win.update_idletasks()
     self.assertIsNotNone(win._poll_job)
     win.destroy()
     self.assertIsNone(win._poll_job)
     self.assertTrue(win._closing)
  except tk.TclError as e:
   self.skipTest('No graphical display: '+str(e))
