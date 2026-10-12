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
    hero['ward_charges']=min(2,hero.get('ward_charges',0)+1)
    return move+' grants a protective ward against the next hit.'
