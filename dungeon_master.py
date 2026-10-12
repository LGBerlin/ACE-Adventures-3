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
    return {'campaign':c.get('title'), 'chapter':w['chapter'], 'location':c.get('location'),
            'quest':c.get('quest',{}), 'party':[
              {'name':h['name'],'class':h['class'],'path':h['path'],'hp':h['hp'],'mana':h['mana']}
              for h in c.get('characters',[])],
            'present_npcs':{k:{**v,'memories':w['npc_memory'].get(k,[])[-4:],'relationship':w['relationships'].get(k,0)}
                            for k,v in available_npcs(c).items()},
            'known_clues':w['clues'][-15:], 'history':c.get('history',[])[-8:],
            'authoritative_outcome':result}

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
    return prose[:2200]