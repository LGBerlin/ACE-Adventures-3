import random,unittest
import game
from character_consistency import CLASSES,validate_character,validate_definitions
class CharacterConsistencyTests(unittest.TestCase):
 def test_class_and_path_definitions(self):
  self.assertEqual(validate_definitions(),[])
  self.assertEqual(set(CLASSES),set(game.PATHS))
 def test_every_class_roulette_is_valid_across_seeds(self):
  for cls in CLASSES:
   for i in range(100):
    hero=game.character('Tester',20,cls,random.Random(i))
    self.assertEqual(validate_character(hero),[],f'{cls}: {i}')
    self.assertIn(hero['path'],game.PATHS[cls])
 def test_wrong_path_detected(self):
  hero=game.character('Tester',21,'Rogue',random.Random(8))
  hero['path']='Paladin'
  self.assertIn('Path does not belong to selected class',validate_character(hero))
 def test_wrong_magic_detected(self):
  hero=game.character('Tester',21,'Mage',random.Random(4))
  hero['magic']='Undefined'
  self.assertIn('Unknown magic affinity',validate_character(hero))
