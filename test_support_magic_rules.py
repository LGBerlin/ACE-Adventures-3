import random,unittest
import game,interaction
class SupportMagicRulesTests(unittest.TestCase):
 def setUp(self):
  self.c=game.new_campaign('Support',1)
  hero=game.character('Iris',24,'Mage',random.Random(5))
  hero['magic']='Support'
  hero['moves']=list(game.SPELLS['Support'])
  game.add_hero(self.c,hero);game.start(self.c)
  self.h=hero
 def test_healing_is_real_and_does_not_roll(self):
  self.h['hp']=self.h['max_hp']-8
  old_mana=self.h['mana']
  result=interaction.perform(self.c,'I cast Healing Wave')
  self.assertFalse(result['roll_required'])
  self.assertEqual(self.h['hp'],self.h['max_hp']-2)
  self.assertEqual(self.h['mana'],old_mana-4)
 def test_full_health_rejects_healing_without_mana_loss(self):
  old_mana=self.h['mana']
  with self.assertRaises(ValueError):interaction.perform(self.c,'I cast Healing Wave')
  self.assertEqual(self.h['mana'],old_mana)
 def test_protective_aura_applies_one_hit_ward(self):
  result=interaction.perform(self.c,'I cast Protective Aura')
  self.assertFalse(result['roll_required'])
  self.assertEqual(self.h['statuses']['ward'],2)
  hp=self.h['hp']
  self.assertEqual(game._apply_incoming(self.h,3),1)
  self.assertEqual(self.h['hp'],hp-1)
  self.assertNotIn('ward',self.h['statuses'])
 def test_blood_drain_heals_on_successful_hit(self):
  self.h['magic']='Blood'
  self.h['moves']=list(game.SPELLS['Blood'])
  self.h['hp']=self.h['max_hp']-10
  self.c['enemy']={'name':'Wolf','hp':100,'ac':12}
  class High:
   def randint(self,minimum,maximum):return maximum
  result=game.action(self.c,'I cast Blood Drain',High())
  self.assertIn('Blood Drain restores',result['result'])
  self.assertGreater(self.h['hp'],self.h['max_hp']-10-4)
 def test_non_support_character_cannot_use_support_magic(self):
  self.h['magic']='Fire'
  with self.assertRaises(ValueError):game.cast_utility(self.c,'Healing Wave')
