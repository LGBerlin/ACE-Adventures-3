import random
import unittest
import game

class ArchetypeRules(unittest.TestCase):
    def test_cleric_is_support_mage_not_vessel(self):
        hero={'class':'Mage','magic':'Support','path':'Spellweaver'}
        self.assertEqual(game.display_archetype(hero),'Cleric')
        self.assertIn('Support',game.SPELLS)
        self.assertNotIn('Cleric',game.PATHS)
    def test_ranger_is_rogue_path(self):
        self.assertIn('Ranger',game.PATHS['Rogue'])
        self.assertNotIn('Ranger',game.PATHS)
        self.assertEqual(game.display_archetype({'class':'Rogue','path':'Ranger'}),'Ranger')
    def test_only_four_character_creation_classes(self):
        self.assertEqual(set(game.PATHS),{'Fighter','Rogue','Mage','Vessel'})
    def test_real_roulette_mage_support_and_rogue_ranger(self):
        class ChosenRandom(random.Random):
            def choices(self,population,weights=None,k=1):
                return [population[1] if 'Ranger' in population else population[0]]
            def choice(self,sequence):
                return 'Support' if 'Support' in sequence else sequence[0]
        rogue=game.character('Tess',24,'Rogue',ChosenRandom(1))
        self.assertEqual(rogue['path'],'Ranger')
        self.assertEqual(game.display_archetype(rogue),'Ranger')
        mage=game.character('Iris',25,'Mage',random.Random(5))
        mage['magic']='Support'
        self.assertEqual(game.display_archetype(mage),'Cleric')
