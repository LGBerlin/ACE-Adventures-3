import copy,json,tempfile,unittest
from pathlib import Path
import game,story,update_addons

class ReliabilityTests(unittest.TestCase):
    def setup_campaign(self):
        c=game.new_campaign('Reliability',2)
        for name,cls in [('Edda','Fighter'),('Sol','Mage')]:game.add_hero(c,game.character(name,24,cls))
        game.start(c)
        return c
    def test_saved_campaign_recovers_from_corrupt_primary(self):
        with tempfile.TemporaryDirectory() as folder:
            c=self.setup_campaign();game.save(folder,c)
            c['history'].append('Save number two');game.save(folder,c)
            primary=Path(folder)/'campaigns'/(c['id']+'.json')
            primary.write_text('{truncated',encoding='utf8')
            restored=game.load_all(folder)
            self.assertEqual(len(restored),1)
            self.assertEqual(restored[0]['id'],c['id'])
    def test_prevent_symlink_asset_escape(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);outside=root/'outside';outside.mkdir()
            (root/'addons').mkdir()
            (root/'addons'/'versions').symlink_to(outside,target_is_directory=True)
            import hashlib
            b=b'data';u='https://example.test/v/data'
            m={'version':'2.0','files':[{'path':'assets/item.dat','url':u,'sha256':hashlib.sha256(b).hexdigest()}]}
            with self.assertRaises(ValueError):update_addons.apply(root,m,lambda _:b,'https://example.test/v')
            self.assertFalse((outside/'2.0').exists())
    def test_quest_progression_and_persistence(self):
        with tempfile.TemporaryDirectory() as folder:
            c=self.setup_campaign()
            for choice in ['elder','tavern','mira','square','well','runes','forest','encounter']:
                story.select(c,choice)
            game.save(folder,c)
            reopened=game.load_all(folder)[0]
            self.assertEqual(reopened['quest']['stage'],3)
            self.assertIsNotNone(reopened['enemy'])
            self.assertEqual(len(reopened['characters']),2)
            self.assertIn('clues',reopened['director'])
    def test_active_character_can_switch_in_combat(self):
        c=self.setup_campaign();game.encounter(c)
        c['active']=1
        result=game.action(c,'attack with my staff')
        self.assertEqual(result['hero'],'Sol')
if __name__=='__main__':unittest.main()