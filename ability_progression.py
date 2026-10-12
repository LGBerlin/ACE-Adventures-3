"""Long-campaign training for every learned attack, spell and technique.

Stable internal ability names preserve save compatibility and free-text matching.
Displayed epithets and visual tiers evolve as each move is practised.
"""
STAGES=((60,'Mythic'),(20,'Empowered'),(5,'Refined'))

def required_level(hero,move):
    if move not in hero.get('moves',[]):return None
    import game
    if hero.get('class')=='Mage':
        if move in game.SPELLS.get(hero.get('magic'),()):return 1
        import spell_catalog
        if hero.get('magic') in spell_catalog.MAGIC_TYPES:
            for entry in spell_catalog.catalog(hero['magic']):
                if entry['name']==move:return entry['level']
    else:
        if move in game.MOVES.get(hero.get('path'),()):return 1
        import technique_catalog
        if hero.get('path') in technique_catalog.TECHNIQUES:
            for entry in technique_catalog.catalog(hero['path']):
                if entry['name']==move:return entry['level']
    # A class-compatible training scroll has its own minimum learned level.
    import training_scrolls
    for spec in training_scrolls.SCROLLS.values():
        if spec['ability']==move:return spec['level']
    return 1

def rank(hero,move):
    unlocked=required_level(hero,move)
    if unlocked is None:return 0
    level=max(1,min(100,int(hero.get('level',1))))
    return 1+max(0,level-unlocked)//4

def damage_bonus(hero,move):
    unlocked=required_level(hero,move)
    if unlocked is None:return 0
    quality=1+min(8,(unlocked-1)//10)
    practice=min(8,max(0,hero.get('level',1)-unlocked)//4)
    return quality+practice

def tier(hero,move):
    unlocked=required_level(hero,move)
    if unlocked is None:return 1
    level=hero.get('level',1)
    return 4 if level>=60 else 3 if level>=20 else 2 if level>=5 else 1

def display_name(hero,move):
    if move not in hero.get('moves',[]):return move
    level=hero.get('level',1)
    for minimum,label in STAGES:
        if level>=minimum and rank(hero,move)>1:
            return move+' · '+label+' (Rank '+str(rank(hero,move))+')'
    return move
