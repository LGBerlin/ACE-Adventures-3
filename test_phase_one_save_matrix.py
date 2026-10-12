"""Final baseline checks: old saves, new gameplay, and corrupted state."""
import copy
import json
import random
import tempfile
import unittest
from pathlib import Path
import game
import town_services
import loot_system
import update_addons

class PhaseOneSaveMatrix(unittest.TestCase):
 def make(self):
  c=game.new_campaign('Save compatibility',2)
  game.add_hero(c,game.character('Knight',28,'Fighter',random.Random(2)))
  game.add_hero(c,game.character('Sage',26,'Mage',random.Random(3)))
  game.start(c)
  return c
 def test_older_campaign_without_modern_fields_loads(self):
  with tempfile.TemporaryDirectory() as folder:
   c=self.make()
   for h in c['characters']:
    for key in ('gear_slots','enchantments','enchant_types','ward_charges'):
     h.pop(key,None)
   for key in ('guild_job','town_memory','loot_history','party_defeated'):
    c.pop(key,None)
   game.save(folder,c)
   restored=game.load_all(folder)[0]
   self.assertEqual(len(restored['characters']),2)
   self.assertEqual(restored['characters'][0]['level'],1)
 def test_modern_quest_equipment_and_active_party_round_trip(self):
  with tempfile.TemporaryDirectory() as folder:
   c=self.make()
   c['active']=1
   c['town_memory']={'Nella':2}
   c['guild_jobs_completed']=2
   town_services.accept(c,'Herbalist Consultation')
   hero=c['characters'][0]
   hero['inventory'].append('Chainmail')
   hero['gear_slots']={'armor':'Chainmail'}
   hero['enchantments']={'Chainmail':1}
   hero['enchant_types']={'Chainmail':'Frost'}
   game.save(folder,c)
   recovered=game.load_all(folder)[0]
   self.assertEqual(recovered['active'],1)
   self.assertEqual(recovered['guild_job']['name'],'Herbalist Consultation')
   self.assertEqual(recovered['characters'][0]['enchantments']['Chainmail'],1)
   self.assertEqual(recovered['town_memory']['Nella'],2)
 def test_invalid_level_and_enchantment_reject_save(self):
  for path,value in [('level',101),('xp',-10),('enchantments',{'Chainmail':99})]:
   with self.subTest(path=path):
    c=self.make()
    c['characters'][0][path]=value
    with tempfile.TemporaryDirectory() as folder:
     with self.assertRaises(ValueError):game.save(folder,c)
 def test_corrupted_optional_fields_do_not_load(self):
  with tempfile.TemporaryDirectory() as folder:
   c=self.make();game.save(folder,c)
   p=Path(folder)/'campaigns'/(c['id']+'.json')
   bad=copy.deepcopy(c)
   bad['guild_job']={'name':'Untrusted quest','start_turn':1}
   p.write_text(json.dumps(bad))
   self.assertEqual(game.load_all(folder),[])
if __name__=='__main__':unittest.main()
