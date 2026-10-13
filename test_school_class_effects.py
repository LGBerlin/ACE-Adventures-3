"""Cross-school and cross-class combat effects test the actual text action path."""
import random
import unittest
import game
import interaction

class SchoolAndClassEffects(unittest.TestCase):
 class Fixed:
  def randint(self,a,b):return b
 def make(self,cls,school=None,path=None):
  c=game.new_campaign('Effect acceptance',1)
  h=game.character('Hero',25,cls,random.Random(3))
  if school:
   h['magic']=school
   h['moves']=list(game.SPELLS[school])
  if path:
   h['path']=path
   h['moves']=list(game.MOVES[path])
  game.add_hero(c,h);game.start(c)
  c['enemy']={'name':'Training golem','hp':120,'max_hp':120,'ac':10}
  h['mana']=max(12,h['mana'])
  h['max_mana']=max(12,h['max_mana'])
  return c,h
 def test_fire_hit_improves_damage(self):
  c,h=self.make('Mage','Fire')
  r=interaction.perform(c,'I cast Flame Flick',self.Fixed())
  self.assertIn('Flames intensify',r['result'])
  self.assertLess(c['enemy']['hp'],120)
 def test_lightning_stops_reaction(self):
  c,h=self.make('Mage','Lightning')
  before=h['hp']
  r=interaction.perform(c,'I cast Static Shock',self.Fixed())
  self.assertIn('shock interrupts',r['result'])
  self.assertEqual(h['hp'],before)
  self.assertFalse(c['enemy'].get('staggered'))
 def test_blood_drains_health(self):
  c,h=self.make('Mage','Blood')
  h['hp']=h['max_hp']-8
  r=interaction.perform(c,'I cast Sanguine Strike',self.Fixed())
  self.assertIn('restores 2 HP',r['result'])
  self.assertGreater(h['hp'],h['max_hp']-8-4)
 def test_dark_weakening_reduces_retaliation(self):
  c,h=self.make('Mage','Dark')
  r=interaction.perform(c,'I cast Dark Pulse',self.Fixed())
  self.assertIn('Shadows weaken',r['result'])
  self.assertFalse(c['enemy'].get('weakened'))
 def test_assassin_class_effect(self):
  c,h=self.make('Rogue',path='Assassin')
  r=interaction.perform(c,'I use Backstab',self.Fixed())
  self.assertIn('weak point',r['result'])
 def test_unauthorized_school_cannot_borrow_lightning_effect(self):
  c,h=self.make('Mage','Fire')
  with self.assertRaises(ValueError):
   interaction.perform(c,'I cast Static Shock',self.Fixed())
  self.assertEqual(c['turn'],0)
if __name__=='__main__':unittest.main()
