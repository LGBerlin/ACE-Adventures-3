"""Advanced abilities must unlock with new names and distinct visual signatures."""
import random
import unittest
import game
import visual_mapping
import spell_catalog
import technique_catalog

class AbilityEvolutionTests(unittest.TestCase):
    def test_every_magic_school_evolves_name_and_appearance(self):
        for school in game.SPELLS:
            hero=game.character('Iris',24,'Mage',random.Random(3))
            hero['magic']=school
            hero['moves']=list(game.SPELLS[school])
            game.award_experience(hero,10000)
            for _ in range(5):game.award_experience(hero,10000)
            entries=spell_catalog.catalog(school)
            for level,tier in ((5,2),(12,3),(20,4)):
                entry=next(e for e in entries if e['level']==level)
                cue=visual_mapping.cue_for(hero,{'action':'I cast '+entry['name'],'degree':'Success'})
                with self.subTest(school=school,level=level):
                    self.assertIn(entry['name'],hero['moves'])
                    self.assertEqual(cue['name'],entry['name'])
                    self.assertEqual(cue['tier'],tier)
    def test_every_nonmage_path_evolves_name_and_appearance(self):
        for cls in ('Rogue','Fighter','Vessel'):
            for path in game.PATHS[cls]:
                hero=game.character('Aster',23,cls,random.Random(2))
                hero['path']=path
                hero['moves']=list(game.MOVES[path])
                game.award_experience(hero,10000)
            for _ in range(5):game.award_experience(hero,10000)
                for level,tier in ((5,2),(12,3),(20,4)):
                    entry=next(e for e in technique_catalog.catalog(path) if e['level']==level)
                    cue=visual_mapping.cue_for(hero,{'action':'I use '+entry['name'],'degree':'Success'})
                    with self.subTest(path=path,level=level):
                        self.assertIn(entry['name'],hero['moves'])
                        self.assertEqual(cue['name'],entry['name'])
                        self.assertEqual(cue['tier'],tier)
    def test_locked_ability_never_receives_upgraded_visual(self):
        hero=game.character('Aster',23,'Fighter',random.Random(2))
        entry=technique_catalog.catalog(hero['path'])[-1]
        cue=visual_mapping.cue_for(hero,{'action':'I use '+entry['name'],'degree':'Success'})
        self.assertEqual(cue['tier'],1)
if __name__=='__main__':unittest.main()
