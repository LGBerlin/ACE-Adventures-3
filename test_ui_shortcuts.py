"""Static navigation shortcuts work without the Dungeon Master."""
import unittest
import ui_shortcuts

class NativeShortcutTests(unittest.TestCase):
    def test_all_panel_shortcuts(self):
        self.assertEqual(set(ui_shortcuts.PANELS),set('123456789'))
        self.assertEqual(len(set(ui_shortcuts.PANELS.values())),9)
        self.assertEqual(ui_shortcuts.panel_for_key('1'),'Record')
        self.assertEqual(ui_shortcuts.panel_for_key('9'),'Shop')

    def test_combat_restricts_travel_and_trade(self):
        for key in ('6','8','9'):
            self.assertIsNone(ui_shortcuts.panel_for_key(key,True))
        for key in ('1','2','3','4','5','7'):
            self.assertIsNotNone(ui_shortcuts.panel_for_key(key,True))

    def test_unmapped_keys_are_not_panels(self):
        for key in ('0','q','F1'):
            self.assertIsNone(ui_shortcuts.panel_for_key(key))

if __name__=='__main__':
    unittest.main()
