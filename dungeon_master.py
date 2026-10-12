"""State-safe story director for ACE Adventures 3.

The model proposes intentions and narration; only deterministic Python rules
can change a campaign. Never execute tools or arbitrary model-supplied code.
"""
import json, re, urllib.request

MODEL='qwen3.5:4b'
BASE_URL='http://127.0.0.1:11434'
NPCS={
 'sera':{'name':'Elder Sera','place':'square','role':'Village elder','secrets':['The old bell was buried after the winter plague.'],'mood':'worried'},
 'mira':{'name':'Mira','place':'tavern','role':'Innkeeper','secrets':['Footprints lead from the well to Ashwood.'],'mood':'guarded'},
 'yarrow':{'name':'Yarrow','place':'market','role':'Herbalist','secrets':['The ruin once held a guardian.'],'mood':'thoughtful'},
}
CATEGORIES=('speak','investigate','travel','fight','cast','hide','trade','use_item','other')

def ensure_world(c):
    world=c.setdefault('director',{})
    world.setdefault('npc_memory',{})
    world.setdefault('clues',[])
    world.setdefault('events',[])
    world.setdefault('relationships',{})
    world.setdefault('chapter','The Hollow Bell')
    for key in NPCS:
        world['npc_memory'].setdefault(key,[])
        world['relationships'].setdefault(key,0)
    return world

def available_npcs(c):
    return {key:info for key,info in NPCS.items() if info['place']==c.get('location')}

def remember(c,npc_id,player_text,outcome):
    if npc_id not in NPCS or npc_id not in available_npcs(c):
        raise ValueError('That character is not here.')
    world=ensure_world(c)
    entry={'player':player_text[:350], 'outcome':outcome[:500], 'turn':c.get('turn',0)}
    world['npc_memory'][npc_id].append(entry)
    world['npc_memory'][npc_id]=world['npc_memory'][npc_id][-12:]
    world['events'].append({'kind':'conversation','npc':npc_id,'turn':c.get('turn',0)})
    world['events']=world['events'][-100:]
    return entry

def discover(c,clue):
    world=ensure_world(c)
    if clue not in world['clues']: world['clues'].append(clue)
    return world['clues']

def extract_object(text):
    return re.sub(r'[^a-z0-9\s-]','',text.lower())[:90].strip()

def fallback_interpret(text):
    """Offline deterministic classifier: never changes character or world state."""
    text=text.strip()
    if not text: raise ValueError('Describe an action.')
    t=text.lower()
    if any(w in t for w in ('attack','strike','stab','shoot','punch','slash')):kind='fight'
    elif any(w in t for w in ('cast ','spell','enchant','magic')):kind='cast'
    elif any(w in t for w in ('talk','ask','persuade','tell','speak','question')):kind='speak'
    elif any(w in t for w in ('look','search','inspect','examine','investigate')):kind='investigate'
    elif any(w in t for w in ('go to','travel','walk to','enter ','leave ')):kind='travel'
    elif any(w in t for w in ('buy','sell','barter','trade')):kind='trade'
    elif any(w in t for w in ('sneak','hide','stealth')):kind='hide'
    elif any(w in t for w in ('drink','use potion','eat ','use item')):kind='use_item'
    else:kind='other'
    return {'kind':kind,'target':extract_object(text),'method':text[:350]}

def validate_intent(candidate,text):
    if not isinstance(candidate,dict):return fallback_interpret(text)
    kind=candidate.get('kind')
    if kind not in CATEGORIES:return fallback_interpret(text)
    return {'kind':kind,'target':str(candidate.get('target',''))[:90], 'method':text[:350]}

def interpret(text,model=MODEL,timeout=16,request=None):
    """Interpret natural language as an intention, not a game-state mutation."""
    offline=fallback_interpret(text)
    system=('Classify an RPG player action into one of: '+', '.join(CATEGORIES)+'. '
            'Return ONLY JSON {"kind":"...","target":"..."}. No other keys. '
            'Do not invent outcomes, rolls, items, quest completion or NPC dialogue.')
    body={'model':model,'stream':False,'format':'json','think':False,'messages':[
      {'role':'system','content':system},{'role':'user','content':text[:500]}],
      'options':{'temperature':0,'num_predict':100}}
    try:
        data=json.dumps(body).encode('utf-8')
        if request is None:
            req=urllib.request.Request(BASE_URL+'/api/chat',data=data,headers={'Content-Type':'application/json'})
            with urllib.request.urlopen(req,timeout=timeout) as resp:reply=json.load(resp)
        else:reply=request(body)
        return validate_intent(json.loads(reply['message']['content']),text)
    except (ValueError,KeyError,TypeError,OSError,TimeoutError):return offline

def prompt_context(c,result):
    """Bounded context for the narrator; immutable facts come first."""
    import copy
    w=ensure_world(copy.deepcopy(c))
    import town_services
    local_people={name:{'role':data['role'],'familiarity':c.get('town_memory',{}).get(name,0)}
                  for name,data in town_services.PEOPLE.items() if data['place']==c.get('location')}
    import loot_system,ability_progression
    return {'campaign':c.get('title'), 'chapter':w['chapter'], 'location':c.get('location'),
            'enemy':{key:value for key,value in (c.get('enemy') or {}).items() if key in ('name','hp','max_hp','ac','boss','phase','staggered','weakened')},
            'guild_rank':town_services.guild_rank(c),
            'guild_jobs_completed':c.get('guild_jobs_completed',0),
            'townsfolk':local_people,
            'last_dice':c.get('dice_history',[])[-3:],
            'active_quests':town_services.quest_status(c),
            'last_enchantment':c.get('last_enchant_spin'),
            'last_loot':c.get('loot_history',[])[-3:],
            'quest':c.get('quest',{}), 'party':[
              {'name':h['name'],'class':h['class'],'path':h['path'],'level':h.get('level',1),
               'hp':h['hp'],'max_hp':h['max_hp'],'mana':h['mana'],'max_mana':h['max_mana'],
               'known_abilities':h.get('moves',[])[-15:],
               'ability_ranks':{move:ability_progression.rank(h,move) for move in h.get('moves',[])[-15:]},
               'passives':h.get('passives',[])[-10:],
               'equipment':h.get('gear_slots',{}), 'equipment_effects':loot_system.bonuses(h),
               'enchants':h.get('enchant_types',{})}
              for h in c.get('characters',[])],
            'present_npcs':{k:{**v,'memories':w['npc_memory'].get(k,[])[-4:],'relationship':w['relationships'].get(k,0)}
                            for k,v in available_npcs(c).items()},
            'known_clues':w['clues'][-15:], 'history':c.get('history',[])[-8:],
            'authoritative_outcome':result}

def _narration_conflicts(c,result,prose):
    """Conservatively reject explicit fictional state changes."""
    lower=prose.casefold()
    actual=json.dumps(result,ensure_ascii=False).casefold()
    quest=c.get('quest') or {}
    if not quest.get('completed') and re.search(r'\b(?:the |your )?quest (?:is |has been )?complet(?:e|ed)\b',lower):
        return True
    if c.get('enemy') and re.search(r'\b(?:enemy|guardian|monster|boss) (?:is |has been )?(?:defeated|slain|killed)\b',lower):
        return True
    for match in re.finditer(r'\b(?:gain|gains|earn|earns|receive|receives|obtain|obtains|awarded)\s+(\d{1,9})\s+gold\b',lower):
        if match.group(1)+' gold' not in actual:
            return True
    return False

def narrate(c,result,model=MODEL,timeout=45,request=None):
    """Narrate only. Callers must never apply LLM prose as authoritative state."""
    sys=('You are a skilled, grounded D&D-style narrator in a coherent fantasy world. '
         'Write evocative second-person prose, 80-150 words. Respect established NPC personalities and memories. '
         'The authoritative_outcome, locations, quest state and character values are settled by game rules. '
         'Never contradict a failed D20 roll, teleport the player, spawn rewards, change HP, or complete a quest. '
         'Describe consequences and offer an organic next choice. Avoid generic praise and modern UI language.')
    body={'model':model,'stream':False,'think':False,'messages':[
      {'role':'system','content':sys},{'role':'user','content':json.dumps(prompt_context(c,result))}],
      'options':{'temperature':0.65,'num_predict':280}}
    if request is not None:reply=request(body)
    else:
        req=urllib.request.Request(BASE_URL+'/api/chat',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(req,timeout=timeout) as resp:reply=json.load(resp)
    prose=str(reply.get('message',{}).get('content','')).strip()
    if not prose:raise ValueError('Model returned no narration.')
    if _narration_conflicts(c,result,prose):
        return str(result.get('result',result) if isinstance(result,dict) else result)[:1100]
    return prose[:2200]