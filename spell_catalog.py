"""Canonical spell names and progression catalog. Starting spells stay unchanged."""
import game
MAGIC_TYPES=tuple(game.SPELLS)
# Progression: starter 1, regular 5, advanced 12, mastery 20.
ADVANCED={
'Earth':('Stoneguard','Earthen Grasp'),'Water':('Tidal Ward','Frozen Torrent'),
'Air':('Gale Step','Cyclone Prison'),'Fire':('Blazing Arc','Inferno Ring'),
'Lightning':('Chain Spark','Storm Lance'),'Gravity':('Gravity Well','Crushing Orbit'),
'Blood':('Crimson Binding','Sanguine Aegis'),'Illusion':('Mirror Double','Veil of Phantoms'),
'Light':('Radiant Ward','Solar Judgment'),'Dark':('Umbral Grasp','Eclipse Veil'),
'Support':('Restoration Prayer','Sanctuary'),'Time':('Temporal Anchor','Second Chance'),
'Creation':('Arcane Fabrication','Living Construct'),'Chaos':('Wild Surge','Entropy Cascade')}
REGULAR={"Earth":"Stone Spike","Water":"Ice Lance","Air":"Gale Blade","Fire":"Firebolt","Lightning":"Thunder Jolt","Gravity":"Gravitic Crush","Blood":"Crimson Lash","Illusion":"Phantom Veil","Light":"Radiant Lance","Dark":"Shadow Lance","Support":"Mending Light","Time":"Temporal Pulse","Creation":"Runic Blade","Chaos":"Wild Bolt"}
def catalog(school):
    if school not in game.SPELLS:raise ValueError('Unknown magic school')
    return [{'name':name,'level':1,'school':school} for name in game.SPELLS[school]]+[
      {'name':REGULAR[school],'level':5,'school':school}]+[
      {'name':name,'level':level,'school':school} for name,level in zip(ADVANCED[school],(12,20))]+[{'name':name,'level':level,'school':school} for name,level in late_names(school)]
def late_names(school):
    base=REGULAR[school]
    return [(base+' Ascendant',35),(base+' Exalted',60),(base+' Mythic',85)]
def unlocked(school,level):
    return [entry['name'] for entry in catalog(school) if entry['level']<=level]
def role(hero):
    return game.display_archetype(hero)
