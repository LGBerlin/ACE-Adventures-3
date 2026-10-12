"""A deterministic, low-power bridge from validated game events to known animations.

Never render continuously: only queue animation events when a rules-engine action
occurs. Unknown states use a static idle pose; no model-supplied file paths.
"""
from dataclasses import dataclass
from collections import deque

CORE=('idle','walk','attack','cast','guard','hurt','defeated','impact','heal')
@dataclass(frozen=True)
class Cue:
    actor: str
    action: str
    duration_ms: int
    effect: str = ''

class Director:
    def __init__(self, max_events=32, max_effects=2, max_duration_ms=1200):
        self.events=deque(maxlen=max_events)
        self.max_effects=max_effects
        self.max_duration_ms=max_duration_ms
    def enqueue(self, actor, action, effect=''):
        if action not in CORE: action='idle'
        if not isinstance(actor,str) or not actor or len(actor)>100:
            raise ValueError('Invalid actor')
        if not isinstance(effect,str) or len(effect)>80:effect=''
        if effect and sum(bool(e.effect) for e in self.events)>=self.max_effects:
            effect=''
        cue=Cue(actor,action,300 if action=='idle' else min(self.max_duration_ms,700),effect)
        self.events.append(cue)
        return cue
    def resolve_action(self, character, result):
        """Read validated rules-engine outcome; never modify HP/mana/inventory."""
        actor=str(character.get('id') or character.get('name') or 'hero')
        text=str(result.get('action','')).lower()
        outcome=str(result.get('result',''))
        success=bool('Success' in str(result.get('degree','')))
        if any(t in text for t in ('guard','defend','block','shield')):
            action='guard'
        elif any(t in text for t in ('cast','spell','flame','lightning','heal','magic')):
            action='cast'
        elif any(t in text for t in ('attack','strike','stab','slash','shoot','punch','kick')):
            action='attack'
        else:
            action='idle'
        effect='' if not success else ('magic_impact' if action=='cast' else 'physical_impact' if action=='attack' else '')
        return self.enqueue(actor,action,effect)
    def drain(self,limit=4):
        """Consume at most a few cues per UI update; idle UI has no frame loop."""
        taken=[]
        for _ in range(min(max(0,int(limit)),len(self.events))):
            taken.append(self.events.popleft())
        return taken
    def clear(self):self.events.clear()
