"""Visual cue mapping for four classes and every supported magic school.

All IDs are internal registry keys, not paths supplied by an LLM.
"""
from asset_registry import MAGIC_TYPES, CLASSES
MAGIC_EFFECTS={
'Earth':'earth_impact','Water':'water_impact','Air':'air_gust','Fire':'fire_impact',
'Lightning':'lightning_impact','Gravity':'gravity_pulse','Blood':'blood_pulse',
'Illusion':'illusion_glimmer','Light':'light_burst','Dark':'dark_pulse',
'Support':'healing_aura','Time':'time_ring','Creation':'creation_sigil','Chaos':'chaos_spark'
}
CLASS_ATTACKS={'Fighter':'physical_impact','Rogue':'physical_impact','Mage':'magic_impact','Vessel':'spirit_impact'}
assert set(MAGIC_EFFECTS)==set(MAGIC_TYPES)
assert set(CLASS_ATTACKS)==set(CLASSES)

def cue_for(hero,result):
    text=str(result.get('action','')).lower()
    cls=hero.get('class','Fighter')
    if cls not in CLASS_ATTACKS:cls='Fighter'
    if any(x in text for x in ('guard','defend','shield','block')):
        return {'animation':'guard','effect':None}
    if any(x in text for x in ('cast','spell','flame','lightning','magic','heal')):
        return {'animation':'cast','effect':MAGIC_EFFECTS.get(hero.get('magic'),'magic_impact')}
    if any(x in text for x in ('attack','strike','stab','slash','shoot','punch','kick')):
        return {'animation':'attack','effect':CLASS_ATTACKS[cls]}
    return {'animation':'idle','effect':None}
