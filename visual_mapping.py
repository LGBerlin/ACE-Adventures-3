"""Visual cue mapping for four classes and every supported magic school.

All IDs are internal registry keys, not paths supplied by an LLM.
"""
from asset_registry import MAGIC_TYPES, CLASSES
import spell_catalog, technique_catalog
MAGIC_EFFECTS={
'Earth':'earth_impact','Water':'water_impact','Air':'air_gust','Fire':'fire_impact',
'Lightning':'lightning_impact','Gravity':'gravity_pulse','Blood':'blood_pulse',
'Illusion':'illusion_glimmer','Light':'light_burst','Dark':'dark_pulse',
'Support':'healing_aura','Time':'time_ring','Creation':'creation_sigil','Chaos':'chaos_spark'
}
CLASS_ATTACKS={'Fighter':'physical_impact','Rogue':'physical_impact','Mage':'magic_impact','Vessel':'spirit_impact'}
assert set(MAGIC_EFFECTS)==set(MAGIC_TYPES)
assert set(CLASS_ATTACKS)==set(CLASSES)

def evolution(hero, action):
    """Return distinct learned ability name and effect tier; no new asset paths."""
    text=str(action).casefold()
    if hero.get('class')=='Mage' and hero.get('magic') in spell_catalog.MAGIC_TYPES:
        entries=spell_catalog.catalog(hero['magic'])
    elif hero.get('path') in technique_catalog.TECHNIQUES:
        entries=technique_catalog.catalog(hero['path'])
    else:
        entries=[]
    for entry in sorted(entries,key=lambda e:e['level'],reverse=True):
        if entry['name'] in hero.get('moves',[]) and entry['level']<=hero.get('level',1) and entry['name'].casefold() in text:
            return {'name':entry['name'],'tier':4 if entry['level']>=20 else 3 if entry['level']>=12 else 2 if entry['level']>=5 else 1}
    return {'name':None,'tier':1}

def cue_for(hero,result):
    text=str(result.get('action','')).lower()
    evolved=evolution(hero,result.get('action',''))
    outcome=result.get('degree')
    hit=outcome is None or outcome in ('Success','Exceptional Success','Critical Success')
    cls=hero.get('class','Fighter')
    if cls not in CLASS_ATTACKS:cls='Fighter'
    # Explicit USE commands from the ability sidebar should animate, not idle.
    if evolved['name'] and text.startswith(('i use ','use ','i cast ','cast ')):
        defensive=any(word in evolved['name'].casefold() for word in ('guard','ward','shield','parry','stance','counter'))
        if defensive:
            return {'animation':'guard','effect':None,**evolved}
        if cls=='Mage':
            return {'animation':'cast','effect':MAGIC_EFFECTS.get(hero.get('magic'),'magic_impact') if hit else None,**evolved}
        return {'animation':'attack','effect':CLASS_ATTACKS[cls] if hit else None,**evolved}
    if any(x in text for x in ('guard','defend','shield','block')):
        return {'animation':'guard','effect':None,**evolved}
    if any(x in text for x in ('cast','spell','flame','lightning','magic','heal')):
        return {'animation':'cast','effect':MAGIC_EFFECTS.get(hero.get('magic'),'magic_impact') if hit else None,**evolved}
    if any(x in text for x in ('attack','strike','stab','slash','shoot','punch','kick')):
        return {'animation':'attack','effect':CLASS_ATTACKS[cls] if hit else None,**evolved}
    return {'animation':'idle','effect':None,**evolved}
