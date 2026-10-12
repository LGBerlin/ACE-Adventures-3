import random,unittest
import game,technique_catalog,spell_catalog
class ProgressionActionGateTests(unittest.TestCase):
 def test_all_nonmage_advanced_names_locked_at_level_one(self):
  for cls in ('Fighter','Rogue','Vessel'):
   hero=game.character('A',20,cls,random.Random(4))
   c=game.new_campaign('Test',1);game.add_hero(c,hero);game.start(c)
   future=technique_catalog.catalog(hero['path'])[0]['name']
   with self.assertRaisesRegex(ValueError,'not unlocked'):
    game.action(c,'I use '+future,random.Random(1))
   self.assertEqual(c['turn'],0)
 def test_mage_advanced_names_locked(self):
  hero=game.character('M',20,'Mage',random.Random(4))
  c=game.new_campaign('Test',1);game.add_hero(c,hero);game.start(c)
  with self.assertRaisesRegex(ValueError,'not unlocked'):
   game.action(c,'I cast '+spell_catalog.catalog(hero['magic'])[0]['name']+' and '+spell_catalog.catalog(hero['magic'])[-1]['name'],random.Random(1))
 def test_newly_unlocked_technique_accepted(self):
  hero=game.character('F',20,'Fighter',random.Random(4));c=game.new_campaign('T',1);game.add_hero(c,hero);game.start(c)
  game.award_experience(hero,150)
  technique=technique_catalog.catalog(hero['path'])[0]['name']
  self.assertIn(technique,hero['moves'])
  game.action(c,'I use '+technique,random.Random(1))
  self.assertEqual(c['turn'],1)
