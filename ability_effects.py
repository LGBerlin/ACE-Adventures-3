"""Deterministic combat roles for learned abilities.

Narrative text never supplies an effect. Only a character's known move and
class/school select the role. Effects are bounded and campaign-save compatible.
"""
CONTROL_SCHOOLS=frozenset(('Earth','Water','Air','Gravity','Illusion','Time','Chaos'))
SHIELD_WORDS=('guard','ward','shield','parry','stance','counter','aegis','bulwark','bastion','protective','sanctuary')
CONTROL_WORDS=('snare','grasp','binding','prison','slow','entangl','stun','root','trap','misdirection','glimpse')
HEAL_WORDS=('heal','restor','mending','blessing','nature touch')
MANA_WORDS=('mana boost',)
def role(hero,move):
    if not move or move not in hero.get('moves',[]):return 'basic'
    name=move.casefold()
    if any(word in name for word in MANA_WORDS):return 'mana'
    if any(word in name for word in HEAL_WORDS) or hero.get('magic')=='Support' and not any(word in name for word in SHIELD_WORDS):return 'heal'
    if any(word in name for word in SHIELD_WORDS):return 'ward'
    if any(word in name for word in CONTROL_WORDS):return 'control'
    if hero.get('class')=='Mage' and hero.get('magic') in CONTROL_SCHOOLS:return 'control'
    return 'damage'
def apply_control(c,hero,move,success):
    if not success or not c.get('enemy'):return ''
    c['enemy']['staggered']=True
    return move+' disrupts the enemy; its next retaliation is prevented.'
def ward(hero,move,success):
    if not success:return 'The ward does not take hold.'
    import ability_progression
    hero['ward_charges']=min(2,hero.get('ward_charges',0)+1)
    hero['ward_strength']=min(6,max(0,ability_progression.rank(hero,move)//4))
    return move+' grants a protective ward against the next hit.'

def offensive_effect(c,hero,move):
    """Additional effects after a successful, authorized attack; no extra rolls."""
    enemy=c.get('enemy')
    if not enemy or not move or move not in hero.get('moves',[]):return (0,'')
    school=hero.get('magic') if hero.get('class')=='Mage' else None
    path=hero.get('path','')
    if school=='Fire':
        return (2,'Flames intensify the hit.')
    if school=='Lightning':
        enemy['staggered']=True
        return (1,'Electric shock interrupts the counterattack.')
    if school=='Blood':
        restored=min(2,hero['max_hp']-hero['hp'])
        hero['hp']+=restored
        return (0,'Sanguine magic restores '+str(restored)+' HP.')
    if school=='Dark':
        enemy['weakened']=True
        return (0,'Shadows weaken the enemy’s next blow.')
    if school=='Light':
        hero['ward_charges']=min(2,hero.get('ward_charges',0)+1)
        return (0,'Radiance grants a ward.')
    if school=='Creation':
        return (1,'The conjured form strengthens the strike.')
    if path=='Assassin':
        return (2,'The precise strike finds a weak point.')
    if path=='Paladin':
        hero['ward_charges']=min(2,hero.get('ward_charges',0)+1)
        return (0,'Sacred energy reinforces a ward.')
    return (0,'')
