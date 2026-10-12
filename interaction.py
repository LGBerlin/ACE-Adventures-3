"""One free-text interaction path. Dice only for uncertain actions.

Never let narration or intent classification bypass the deterministic quest gates.
"""
import re
import game,story,dice_ledger

LOCATION_WORDS={
 'square':('square','town square','village square'),
 'tavern':('tavern','inn','lantern & thistle','lantern and thistle'),
 'market':('market','apothecary','shop','yarrow\'s shop'),
 'well':('well','old well'),
 'forest':('forest','ashwood','woods')}
TRAVEL=re.compile(r'^(?:i\s+)?(?:want to |would like to |will |am going to |decide to )?(?:go|walk|travel|head|move|return|visit|enter|follow|make my way|take the road)(?:\s+back)?\s+(?:to|toward|towards|into|over to|through|the|a)?\s*',re.I)
def interpret_simple(c,text):
    """Return a canonical quest choice, or None for uncertain actions."""
    lower=' '.join(text.casefold().strip().split())
    available={value for _,value in story.options(c)}
    travel=TRAVEL.match(lower)
    if travel:
        destination=lower[travel.end():].strip()
        destination=re.sub(r'^(?:to|the|a|into|toward|towards)\s+','',destination)
        for place,aliases in LOCATION_WORDS.items():
            if any(destination==alias or destination==('the '+alias) for alias in aliases):
                if place not in available:raise ValueError('That route is not available yet. Follow the clues.')
                return place
    # Social choices are deliberately limited to present NPCs, not remote dialogue.
    npc_verbs=('talk','speak','ask','question','converse','chat')
    if any(re.search(r'\b'+v+r'\b',lower) for v in npc_verbs):
        for choice,names in {'elder':('sera','elder'),'mira':('mira','innkeeper'),'yarrow':('yarrow','herbalist')}.items():
            if choice in available and any(re.search(r'\b'+name+r'\b',lower) for name in names):
                return choice
    if c.get('location')=='well' and 'runes' in available and any(w in lower for w in ('read the runes','examine the carvings','inspect the runes')):
        return 'runes'
    if c.get('location')=='market' and 'buy_potion' in available and any(w in lower for w in ('buy a healing draught','buy a potion','purchase a healing draught')):
        return 'buy_potion'
    if c.get('location')=='forest' and 'encounter' in available and any(w in lower for w in ('approach the ruined arch','approach the ruins')):
        return 'encounter'
    return None

def perform(c,text,rng=None):
    text=text.strip()
    if not text:raise ValueError('Describe what you want to do.')
    if not c.get('started'):raise ValueError('Start the campaign first.')
    choice=interpret_simple(c,text)
    if choice is not None:
        outcome=story.select(c,choice)
        return {'roll_required':False,'result':outcome,'choice':choice,'action':text}
    if c.get('enemy') is None and re.fullmatch(r'(?:hello|hi|hey|thank you|thanks|look around|look at the scenery|wait|rest|sit down|listen)',text,re.I):
        msg='You '+text.lower().rstrip('.')+'.'
        c['history'].append(msg);c['turn']+=1
        return {'roll_required':False,'result':msg,'action':text}
    result=game.action(c,text,rng)
    result['roll_required']=True
    dice_ledger.record(c,result,text)
    return result
