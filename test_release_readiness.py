"""Release blockers: real GUI startup and quest progression cannot be bypassed."""
import unittest
from unittest.mock import patch
import tkinter as tk
import game,story

class QuestSafety(unittest.TestCase):
    def sample(self):
        c=game.new_campaign('Validation',1)
        game.add_hero(c,game.character('Arlen',24,'Fighter'))
        game.start(c);story.ensure(c)
        return c
    def test_progression_requires_guardian_defeat(self):
        c=self.sample()
        story.select(c,'elder');story.select(c,'tavern');story.select(c,'mira')
        story.select(c,'square');story.select(c,'well');story.select(c,'runes')
        story.select(c,'forest');story.select(c,'encounter')
        self.assertEqual(c['quest']['stage'],3)
        self.assertIsNotNone(c['enemy'])
        # A noncombat action does not complete the encounter.
        game.action(c,'I observe the stonework')
        self.assertEqual(c['quest']['stage'],3)
        self.assertIsNotNone(c['enemy'])
        with self.assertRaises(ValueError):story.select(c,'elder')
    def test_unearned_elder_cannot_end_quest(self):
        c=self.sample();story.select(c,'elder')
        with self.assertRaises(ValueError):story.select(c,'elder')

class GuiSmoke(unittest.TestCase):
    def test_window_startup_and_campaign_ui(self):
        try:
            import app
            with patch.object(app,'DATA',__import__('pathlib').Path(self.id().replace('.','_'))):
                window=app.App();window.withdraw();window.update()
                window._new();window.update()
                window._connections();window.update()
                window.destroy()
        except tk.TclError as exc:
            self.skipTest('No graphics display: '+str(exc))

if __name__=='__main__':unittest.main()