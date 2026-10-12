"""Regression: multi-party quest resumes mid-encounter without advancing incorrectly."""
import tempfile
import unittest
import game, story

class MultiPartyJourney(unittest.TestCase):
    def test_two_heroes_save_resume_and_guardian_gate(self):
        with tempfile.TemporaryDirectory() as root:
            campaign=game.new_campaign('Two Heroes', 2)
            game.add_hero(campaign, game.character('Arlen', 25, 'Fighter'))
            game.add_hero(campaign, game.character('Lyra', 32, 'Mage'))
            game.start(campaign)
            for step in ('elder','tavern','mira','square','well','runes','forest','encounter'):
                story.select(campaign,step)
            self.assertIsNotNone(campaign['enemy'])
            game.save(root,campaign)
            reopened=game.load_all(root)
            self.assertEqual(len(reopened),1)
            restored=reopened[0]
            self.assertEqual(restored['quest']['stage'],3)
            self.assertEqual(len(restored['characters']),2)
            restored['active']=1
            result=game.action(restored,'I observe the guardian from behind a tree')
            self.assertIn('roll',result)
            self.assertEqual(restored['quest']['stage'],3)
            self.assertIsNotNone(restored['enemy'])
            game.save(root,restored)
            again=game.load_all(root)[0]
            self.assertEqual(again['active'],1)
            self.assertIsNotNone(again['enemy'])

if __name__=='__main__':unittest.main()