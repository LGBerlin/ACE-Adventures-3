import unittest,random,tempfile
from pathlib import Path
import game
class Tests(unittest.TestCase):
 def test_complete_session(self):
  c=game.new_campaign('A Quest',2)
  game.add_hero(c,game.character('A',20,'Mage',random.Random(1)))
  game.add_hero(c,game.character('B',21,'Fighter',random.Random(2)))
  game.start(c);game.choose_location(c,'tavern');game.encounter(c,random.Random(4))
  result=game.action(c,'I attack with my weapon',random.Random(1));self.assertTrue(1<=result['roll']<=20)
  with tempfile.TemporaryDirectory() as tmp:
   game.save(tmp,c);restored=game.load_all(tmp)[0]
   self.assertEqual(restored['characters'][0]['name'],'A')
   self.assertEqual(restored['location'],'tavern')
   self.assertEqual(restored['turn'],1)
 def test_no_reroll(self):
  c=game.new_campaign('Solo',1);game.add_hero(c,game.character('C',20,'Rogue'))
  with self.assertRaises(ValueError):game.add_hero(c,game.character('D',20,'Rogue'))
 def test_incomplete_party(self):
  c=game.new_campaign('Duet',2);game.add_hero(c,game.character('A',20,'Vessel'))
  with self.assertRaises(ValueError):game.start(c)
 def test_invalid_magic(self):
  c=game.new_campaign('Quest',1);game.add_hero(c,game.character('A',20,'Fighter',random.Random(5)));game.start(c)
  with self.assertRaises(ValueError):game.action(c,'I cast fireball',random.Random(4))
if __name__=='__main__':unittest.main()