"""One free-text interaction path. Dice only for uncertain actions.

Never let narration or intent classification bypass the deterministic quest gates.
"""
import re
import game,story,dungeon_master

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

def perform(c,text,rng=None,intent=None):
    """A successful harmless action never rolls; rules decide risky outcomes."""
    text=text.strip()
    if not text:raise ValueError('Describe what you want to do.')
    if not c.get('started'):raise ValueError('Start the campaign first.')
    hero=c['characters'][c['active']]
    if hero['hp']<=0:raise ValueError('This character is incapacitated.')
    choice=interpret_simple(c,text)
    if choice is not None:
        outcome=story.select(c,choice)
        return {'roll_required':False,'result':outcome,'choice':choice,'action':text}
    intent=dungeon_master.validate_intent(intent,text)
    literal=dungeon_master.fallback_interpret(text)
    kind=literal['kind'] if literal['kind'] in ('fight','cast','travel','trade','use_item') else intent['kind']
    # Model proposals must pass the same deterministic location and quest gates.
    target=intent.get('target','').strip().casefold()
    if kind=='travel':
        place=next((key for key,aliases in LOCATION_WORDS.items() if target==key or target in aliases),None)
        if place is not None:
            choice=interpret_simple(c,'go to '+place)
            if choice is not None:
                return {'roll_required':False,'result':story.select(c,choice),'choice':choice,'action':text}
    if kind=='use_item':
        item=next((name for name in ('Healing Draught','Health Potion') if name.casefold() in text.casefold()),None)
        if item is None:raise ValueError('Name the item to use from your inventory.')
        return {'roll_required':False,'result':game.use_item(c,item),'action':text}
    if not c.get('enemy'):
        if kind=='travel':raise ValueError('Choose an available destination and tell the Dungeon Master where to go.')
        if kind=='fight':raise ValueError('There is no opponent here.')
        if kind=='trade':raise ValueError('Visit the market and use the Shop tab.')
        uncertain=bool(re.search(r'\b(persuade|convince|negotiate|bargain|sneak|hide|climb|pickpocket|disarm|steal|force|jump)\b|\bpick\s+(?:the\s+|a\s+)?lock\b|\bsearch\b.*\b(hidden|trap|secret|clue)\b',text,re.I))
        if kind not in ('cast',) and not uncertain:
            if kind=='speak':
                npcs=dungeon_master.available_npcs(c)
                if not npcs:raise ValueError('There is nobody here to speak with.')
                npc=next(iter(npcs))
                message=npcs[npc]['name']+' listens. '+story.DEFAULT_FLAVOUR.get(c.get('location'),'')
                dungeon_master.remember(c,npc,text,message)
            elif kind=='investigate':
                message=story.DEFAULT_FLAVOUR.get(c.get('location'),'You examine your surroundings.')
            else:
                ordinary=re.sub(r'^(?:i\s+)?(?:want to |would like to |will |am going to )?','',text,flags=re.I).rstrip('.!?')
                message='You '+ordinary[:1].lower()+ordinary[1:]+'. '+story.DEFAULT_FLAVOUR.get(c.get('location'),'')
            c['history'].append(message);c['turn']+=1
            return {'roll_required':False,'result':message,'action':text}
    result=game.action(c,text,rng)
    result['roll_required']=True
    return result
