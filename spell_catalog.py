"""Canonical spell names and progression catalog. Starting spells stay unchanged."""
import game
MAGIC_TYPES=tuple(game.SPELLS)
# At levels 1, 3 and 5, each school has a curated next step.
ADVANCED={
'Earth':('Stoneguard','Earthen Grasp'),'Water':('Tidal Ward','Frozen Torrent'),
'Air':('Gale Step','Cyclone Prison'),'Fire':('Blazing Arc','Inferno Ring'),
'Lightning':('Chain Spark','Storm Lance'),'Gravity':('Gravity Well','Crushing Orbit'),
'Blood':('Crimson Binding','Sanguine Aegis'),'Illusion':('Mirror Double','Veil of Phantoms'),
'Light':('Radiant Ward','Solar Judgment'),'Dark':('Umbral Grasp','Eclipse Veil'),
'Support':('Restoration Prayer','Sanctuary'),'Time':('Temporal Anchor','Second Chance'),
'Creation':('Arcane Fabrication','Living Construct'),'Chaos':('Wild Surge','Entropy Cascade')}
def catalog(school):
    if school not in game.SPELLS:raise ValueError('Unknown magic school')
    return [{'name':name,'level':1,'school':school} for name in game.SPELLS[school]]+[
      {'name':name,'level':level,'school':school} for name,level in zip(ADVANCED[school],(3,5))]
def unlocked(school,level):
    return [entry['name'] for entry in catalog(school) if entry['level']<=level]
def role(hero):
    return game.display_archetype(hero)
