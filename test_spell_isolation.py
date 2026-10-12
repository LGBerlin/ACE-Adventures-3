import random,unittest
import game
class SpellIsolationRegression(unittest.TestCase):
 def test_mage_progression_cannot_mutate_other_mage_starting_spells(self):
  original={k:tuple(v) for k,v in game.SPELLS.items()}
  mage=game.character('Caster',20,'Mage',random.Random(1))
  school=mage['magic']
  game.award_experience(mage,600)
  self.assertEqual({k:tuple(v) for k,v in game.SPELLS.items()},original)
  another=game.character('Newcomer',20,'Mage',random.Random(1))
  self.assertEqual(another['moves'],list(original[school]))
  self.assertEqual(len(another['moves']),3)
 def test_paths_are_not_shared_mutable_lists(self):
  a=game.character('A',20,'Rogue',random.Random(1))
  b=game.character('B',20,'Rogue',random.Random(1))
  a['moves'].append('Temporary')
  self.assertNotIn('Temporary',b['moves'])
  self.assertNotIn('Temporary',game.MOVES[b['path']])
