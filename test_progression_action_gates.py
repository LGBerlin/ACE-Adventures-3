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
 def test_every_advanced_spell_remains_locked_at_level_one(self):
  for school in game.SPELLS:
   hero=game.character('Mage',22,'Mage',random.Random(4))
   hero['magic']=school
   hero['moves']=list(game.SPELLS[school])
   c=game.new_campaign('School lock',1);game.add_hero(c,hero);game.start(c)
   for entry in spell_catalog.catalog(school):
    if entry['level']==1:continue
    with self.subTest(school=school,ability=entry['name']):
     with self.assertRaisesRegex(ValueError,'not unlocked'):
      game.action(c,'I cast '+entry['name'],random.Random(1))
     self.assertEqual(c['turn'],0)
 def test_every_advanced_technique_remains_locked_at_level_one(self):
  for cls in ('Fighter','Rogue','Vessel'):
   for path in game.PATHS[cls]:
    hero=game.character('Tester',22,cls,random.Random(4))
    hero['path']=path
    hero['moves']=list(game.MOVES[path])
    c=game.new_campaign('Path lock',1);game.add_hero(c,hero);game.start(c)
    for entry in technique_catalog.catalog(path):
     with self.subTest(path=path,ability=entry['name']):
      with self.assertRaisesRegex(ValueError,'not unlocked'):
       game.action(c,'I use '+entry['name'],random.Random(1))
      self.assertEqual(c['turn'],0)
 def test_ordinary_guard_does_not_match_another_class_ability(self):
  h=game.character('Aster',23,'Rogue',random.Random(4))
  c=game.new_campaign('Guard action',1);game.add_hero(c,h);game.start(c)
  game.encounter(c,random.Random(2))
  result=game.action(c,'I guard against the enemy attack',random.Random(3))
  self.assertIn('Guard stance',result['result'])
 def test_cross_class_explicit_spells_rejected(self):
  h=game.character('Aster',23,'Fighter',random.Random(4))
  c=game.new_campaign('No borrowed magic',1);game.add_hero(c,h);game.start(c)
  with self.assertRaisesRegex(ValueError,'not available'):
   game.action(c,'I cast Healing Wave',random.Random(2))
 def test_newly_unlocked_technique_accepted(self):
  hero=game.character('F',20,'Fighter',random.Random(4));c=game.new_campaign('T',1);game.add_hero(c,hero);game.start(c)
  game.award_experience(hero,150)
  technique=technique_catalog.catalog(hero['path'])[0]['name']
  self.assertIn(technique,hero['moves'])
  game.action(c,'I use '+technique,random.Random(1))
  self.assertEqual(c['turn'],1)
