import random
import unittest
import game
import atlas
import story

class AtlasTests(unittest.TestCase):
    def setUp(self):
        self.c=game.new_campaign("Map",1)
        game.add_hero(self.c,game.character("Mira",25,"Mage",random.Random(2)))
        game.start(self.c)
    def test_coordinates_and_current_location(self):
        state=atlas.state(self.c)
        self.assertEqual(state["current"],"square")
        self.assertEqual(len(state["nodes"]),5)
        self.assertTrue(next(n for n in state["nodes"] if n["id"]=="square")["current"])
    def test_locked_routes(self):
        with self.assertRaises(ValueError):atlas.travel(self.c,"forest")
        self.assertEqual(self.c["location"],"square")
    def test_travel_via_authoritative_story(self):
        atlas.travel(self.c,"tavern")
        self.assertEqual(self.c["location"],"tavern")
        self.assertEqual(atlas.state(self.c)["current"],"tavern")
    def test_combat_blocks_travel(self):
        self.c["enemy"]={"name":"Wisp","hp":15,"ac":12}
        with self.assertRaises(ValueError):atlas.travel(self.c,"tavern")
if __name__=="__main__":unittest.main()
