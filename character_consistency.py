"""Release-time consistency checks for character identity and presentation.

The game has four selectable classes. Paths, magic affinities and narrative roles
are distinct concepts; UI and art must not invent additional selectable classes.
"""
from game import PATHS, MOVES, SPELLS, display_archetype
CLASSES=('Fighter','Rogue','Mage','Vessel')
STARTING_GEAR={'Fighter':'Iron Sword','Rogue':'Daggers','Mage':'Ashwood Staff','Vessel':'Pilgrim Staff'}
MAGIC_AFFINITIES=set(SPELLS)|{'None','Ki','Nature','Spirit','Omen'}
def validate_definitions():
    problems=[]
    if set(PATHS)!=set(CLASSES):problems.append('Selectable classes differ from four-class specification')
    seen=set()
    for cls,paths in PATHS.items():
        if not paths:problems.append(cls+' has no paths')
        for path in paths:
            if path in seen:problems.append('Duplicate path: '+path)
            seen.add(path)
            if cls!='Mage' and (path not in MOVES or not MOVES[path]):
                problems.append('Missing path moves: '+path)
    for school,moves in SPELLS.items():
        if not moves:problems.append('Magic school has no spells: '+school)
    if 'Ranger' not in PATHS.get('Rogue',[]):problems.append('Ranger must be a Rogue path')
    if 'Cleric' in PATHS or 'Ranger' in PATHS:problems.append('Subclasses cannot be selectable classes')
    if display_archetype({'class':'Mage','magic':'Support','path':'Spellweaver'})!='Cleric':
        problems.append('Support Mage must display as Cleric')
    return problems
def validate_character(hero):
    problems=[]
    cls=hero.get('class')
    path=hero.get('path')
    magic=hero.get('magic','None')
    if cls not in CLASSES:return ['Unknown base class']
    if path not in PATHS[cls]:problems.append('Path does not belong to selected class')
    if magic not in MAGIC_AFFINITIES:problems.append('Unknown magic affinity')
    if cls=='Mage' and magic not in SPELLS:problems.append('Mage requires an established magic school')
    if cls=='Rogue' and path=='Ranger' and display_archetype(hero)!='Ranger':
        problems.append('Ranger identity mismatch')
    if cls=='Mage' and magic=='Support' and display_archetype(hero)!='Cleric':
        problems.append('Cleric identity mismatch')
    if not isinstance(hero.get('sprite_seed'),int):problems.append('Missing stable sprite seed')
    if not isinstance(hero.get('stats'),dict) or set(hero['stats'])!={'STR','DEX','CON','INT','WIS','CHA'}:
        problems.append('Missing D20 attributes')
    return problems
if __name__=='__main__':
    problems=validate_definitions()
    if problems:raise SystemExit('; '.join(problems))
    print('Class/path/magic canonical definitions verified')
