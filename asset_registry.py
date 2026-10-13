"""Low-memory sprite registry for approved ACE Adventures 3 asset packs.

Only loads explicitly indexed files on demand. Never guesses or executes assets
from the 3rd-party raw library. Images are evicted with an LRU byte budget.
"""
from collections import OrderedDict
from pathlib import Path, PurePosixPath
import json, hashlib, re
MAGIC_TYPES=('Earth','Water','Air','Fire','Lightning','Gravity','Blood','Illusion','Light','Dark','Support','Time','Creation','Chaos')
CLASSES=('Fighter','Rogue','Mage','Vessel')
SLOTS=('body','portrait','weapon','armor','accessory','idle','walk','run','attack','cast','guard','hurt','background','icon','effect')
NAME=re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,110}$')
def safe_relative(value):
    if not isinstance(value,str) or '\\' in value or ':' in value or value.startswith('/'):raise ValueError('Bad asset path')
    p=PurePosixPath(value)
    if not value or len(value)>240 or any(not NAME.fullmatch(x) for x in p.parts) or len(p.parts)<2:raise ValueError('Bad asset path')
    if p.suffix.lower() not in ('.png','.gif'):raise ValueError('Unsupported sprite format')
    return p
class Registry:
    def __init__(self,root,manifest=None,max_cache_bytes=24*1024*1024,max_file_bytes=4*1024*1024):
        self.root=Path(root).resolve()
        self.max_cache_bytes=max_cache_bytes
        self.max_file_bytes=max_file_bytes
        self.cache=OrderedDict();self.cache_size=0
        self.records={}
        if manifest is not None:self.load(manifest)
    def load(self,manifest):
        data=json.loads(Path(manifest).read_text(encoding='utf-8')) if isinstance(manifest,(str,Path)) else manifest
        if not isinstance(data,dict) or data.get('version')!=1 or not isinstance(data.get('assets'),dict):
            raise ValueError('Invalid sprite manifest')
        checked={}
        for key,entry in data['assets'].items():
            if not NAME.fullmatch(key) or not isinstance(entry,dict):raise ValueError('Invalid asset entry')
            relative=safe_relative(entry.get('file'))
            checksum=entry.get('sha256')
            if not isinstance(checksum,str) or not re.fullmatch(r'[a-f0-9]{64}',checksum):raise ValueError('Missing file checksum')
            category=entry.get('category')
            if category not in SLOTS:raise ValueError('Unknown category')
            checked[key]={'file':str(relative),'sha256':checksum,'category':category,'tags':entry.get('tags',[])}
        self.records=checked;self.clear()
    def path(self,key):
        entry=self.records.get(key)
        if entry is None:return None
        target=(self.root/entry['file']).resolve()
        if not target.is_relative_to(self.root) or not target.is_file() or target.stat().st_size>self.max_file_bytes:
            return None
        return target
    def bytes(self,key):
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        target=self.path(key)
        if target is None:return None
        content=target.read_bytes()
        if len(content)>self.max_file_bytes or hashlib.sha256(content).hexdigest()!=self.records[key]['sha256']:
            return None
        if len(content)>self.max_cache_bytes:return content
        while self.cache and self.cache_size+len(content)>self.max_cache_bytes:
            _,old=self.cache.popitem(last=False);self.cache_size-=len(old)
        self.cache[key]=content;self.cache_size+=len(content)
        return content
    def choose(self,category,**tags):
        matches=[]
        for key,e in self.records.items():
            if e['category']!=category:continue
            metadata=e.get('tags',[])
            if all(f'{name}:{value}'.lower() in metadata for name,value in tags.items()):
                matches.append(key)
        return sorted(matches)
    def clear(self):
        self.cache.clear();self.cache_size=0

def appearance_id(character):
    """Stable assignment: unchanged on campaign reload and across machines."""
    if character.get('appearance_id'):return character['appearance_id']
    value=str(character.get('sprite_seed',character.get('id',character.get('name',''))))
    cls=character.get('class','Fighter').lower()
    return cls+'_'+hashlib.sha256(value.encode()).hexdigest()[:10]

def select_character_sprite(registry,character,category='portrait'):
    """Select a repeatable approved image variant without modifying the character.

    Path-matched sprites take priority, followed by class-matched art.
    Missing imagery returns None so the native canvas can draw a fallback.
    """
    if category not in ('portrait','body','idle'):
        raise ValueError('Unsupported character sprite category')
    cls=str(character.get('class','Fighter')).lower()
    path=str(character.get('path','')).lower()
    seed=str(character.get('sprite_seed',character.get('id',character.get('name',''))))
    # A listed but damaged path sprite must not prevent a valid class fallback.
    for specificity,keys in (
        ('path',registry.choose(category,**{'class':cls,'path':path})),
        ('class',registry.choose(category,**{'class':cls}))):
        if not keys:continue
        index=int.from_bytes(hashlib.sha256((cls+'|'+path+'|'+seed+'|'+specificity).encode()).digest()[:8],'big')%len(keys)
        for offset in range(len(keys)):
            key=keys[(index+offset)%len(keys)]
            if registry.bytes(key) is not None:return key
    return None

def find_approved_assets(user_data,application_root=None):
    """Locate the approved asset pack in installed or bundled locations.

    Deliberately ignore raw or unreviewed sprite downloads. A verified
    manifest controls exact sprite selection and protects campaign identity.
    User-installed assets override packaged files so updates don't erase art.
    """
    import sys
    data=Path(user_data)
    candidates=[data/'approved sprites']
    if application_root is not None:
        base=Path(application_root)
        candidates.extend((base/'assets'/'approved sprites',base/'approved sprites'))
    frozen=getattr(sys,'_MEIPASS',None)
    if frozen:
        base=Path(frozen)
        candidates.extend((base/'assets'/'approved sprites',base/'approved sprites'))
    source=Path(__file__).resolve().parent
    candidates.extend((source/'assets'/'approved sprites',source/'approved sprites'))
    for candidate in candidates:
        if (candidate/'manifest.json').is_file():
            return candidate
    return candidates[0]
