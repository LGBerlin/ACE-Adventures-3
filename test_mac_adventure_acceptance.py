"""Mac graphical acceptance test of the actual illustrated adventure window.

This runs in the desktop session before packaging. It must not silently skip on
macOS: a Mac runner unable to create a Tk window cannot certify a GUI release.
"""
import sys,tempfile,unittest,random
from pathlib import Path
from unittest.mock import patch

class AdventureWindowAcceptance(unittest.TestCase):
    def test_campaign_to_story_and_all_paper_panels(self):
        try:
            import tkinter as tk
            import app,game,story
            probe=tk.Tk();probe.withdraw();probe.update_idletasks();probe.destroy()
        except Exception as exc:
            if sys.platform=='darwin':raise AssertionError('Mac Tk GUI unavailable') from exc
            self.skipTest('No graphical desktop')
        with tempfile.TemporaryDirectory() as temp,patch.object(app,'DATA',Path(temp)):
            window=app.App()
            try:
                campaign=game.new_campaign('Acceptance',2)
                for name,cls in (('Ada','Fighter'),('Bryn','Mage')):
                    game.add_hero(campaign,game.character(name,24,cls,random.Random(len(name))))
                game.start(campaign)
                story.ensure(campaign)
                window.c=campaign
                window._adventure()
                window.update_idletasks()
                for tab in ('Record','Pack','Abilities','Journal','Story Tree'):
                    window._panel(tab)
                    window.update_idletasks()
                for step in ('elder','tavern','mira','square','well','runes','forest'):
                    story.select(campaign,step)
                window._adventure()
                window.update_idletasks()
                game.save(Path(temp),campaign)
                loaded=game.load_all(Path(temp))
                self.assertTrue(loaded)
                self.assertEqual(loaded[0]['id'],campaign['id'])
                self.assertEqual(len(loaded[0]['characters']),2)
            finally:
                window.destroy()
