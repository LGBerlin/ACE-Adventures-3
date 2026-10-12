"""Path-specific techniques earned at levels 3 and 5, not new selectable classes."""
from game import PATHS
TECHNIQUES={
'Thief':('Misdirection','Master Pickpocket'),'Ranger':('Piercing Arrow','Predator Mark'),
'Assassin':('Venom Cut','Shadow Execution'),'Arcane Trickster':('Phantom Swap','Arcane Ambush'),
'Martial Artist':('Flowing Counter','Hundred Palm Barrage'),'Knight':('Shield Wall','Valiant Charge'),
'Swordsman':('Twin Cut','Blade Tempest'),'Barbarian':('Berserker Rush','Earthshaker'),
'Paladin':('Oathbound Strike','Radiant Bulwark'),
'Monk':('Focused Ki','Celestial Palm'),'Druid':('Entangling Roots','Wildshape Echo'),
'Spirit Fighter':('Spirit Lance','Ancestral Surge'),'Warden':('Thorn Guard','Nature Bastion'),
'Oracle Vessel':('Foretold Step','Fate Reversal')}
def catalog(path):
 if path not in TECHNIQUES:raise ValueError('Unknown technique path')
 return [{'name':name,'level':lv,'path':path} for name,lv in zip(TECHNIQUES[path],(3,5))]
def unlocked(path,level):
 return [x['name'] for x in catalog(path) if level>=x['level']]
def validate():
 actual={p for cls,paths in PATHS.items() if cls!='Mage' for p in paths}
 return actual==set(TECHNIQUES) and all(len(set(x))==2 for x in TECHNIQUES.values())
