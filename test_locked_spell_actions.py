import random,unittest
import game,spell_catalog

class LockedSpellActionTests(unittest.TestCase):
 def test_advanced_spell_cannot_be_used_before_unlock(self):
  c=game.new_campaign('Progression',1)
  h=game.character('Caster',20,'Mage',random.Random(6))
  game.add_hero(c,h);game.start(c)
  name=spell_catalog.catalog(h['magic'])[3]['name']
  with self.assertRaisesRegex(ValueError,'not unlocked'):
   game.action(c,'I cast '+name,random.Random(3))
  self.assertEqual(c['turn'],0)
 def test_unlocked_spell_can_be_attempted(self):
  c=game.new_campaign('Progression',1)
  h=game.character('Caster',20,'Mage',random.Random(6))
  game.add_hero(c,h);game.start(c)
  game.award_experience(h,1200)
  name=spell_catalog.catalog(h['magic'])[3]['name']
  self.assertIn(name,h['moves'])
  result=game.action(c,'I cast '+name,random.Random(3))
  self.assertTrue(1<=result['roll']<=20)
