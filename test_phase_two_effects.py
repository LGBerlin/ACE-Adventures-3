"""Phase 2 visual-effects coverage and actual battle canvas integration."""
import random,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import battle_effects,visual_mapping,game

class EffectCoverage(unittest.TestCase):
 def test_every_school_effect_draws_and_is_bounded(self):
  class Canvas:
   def __init__(self):self.shapes=[]
   def create_oval(self,*a,**kw):self.shapes.append('oval')
   def create_line(self,*a,**kw):self.shapes.append('line')
   def create_polygon(self,*a,**kw):self.shapes.append('polygon')
   def create_text(self,*a,**kw):self.shapes.append('text')
  for school,effect in visual_mapping.MAGIC_EFFECTS.items():
   canvas=Canvas()
   self.assertTrue(battle_effects.paint(canvas,effect,100,100,4),school)
   self.assertGreaterEqual(len(canvas.shapes),5)
   self.assertLessEqual(len(canvas.shapes),5)
  self.assertFalse(battle_effects.paint(Canvas(),'fictional_ai_command',100,100))
 def test_normal_spell_cue_never_changes_game_state(self):
  hero=game.character('Iris',25,'Mage',random.Random(2))
  hero['magic']='Fire';hero['moves']=list(game.SPELLS['Fire'])
  before=(hero['hp'],hero['mana'],list(hero['moves']))
  v=visual_mapping.cue_for(hero,{'action':'I cast '+hero['moves'][0],'degree':'Success'})
  self.assertEqual(v['effect'],visual_mapping.MAGIC_EFFECTS['Fire'])
  self.assertEqual(before,(hero['hp'],hero['mana'],hero['moves']))
if __name__=='__main__':unittest.main()
