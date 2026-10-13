"""Release-ready report of sprite coverage, grounded in actual approved PNGs."""
import json
from pathlib import Path
from asset_registry import Registry,MAGIC_TYPES
from game import PATHS

CLASS_CORE=('idle','walk','attack','hurt')
CLASS_COUNT=20
MAGIC_CORE=('cast','impact')

def report(root):
    root=Path(root)
    manifest=root/'manifest.json'
    if not manifest.is_file():
        return {'ready':False,'reason':'No approved sprite manifest installed','classes':{},'magic':{},'asset_count':0}
    try:
        reg=Registry(root,manifest,max_cache_bytes=16*1024*1024)
    except (OSError,ValueError,KeyError,TypeError) as exc:
        return {'ready':False,'reason':'Invalid manifest: '+str(exc),'classes':{},'magic':{},'asset_count':0}
    classes={}
    for cls,paths in PATHS.items():
        entries={}
        for path in paths:
            candidates={}
            for state in CLASS_CORE:
                candidates[state]=[key for key in reg.choose(state,**{'class':cls.lower(),'path':path.lower()}) if reg.bytes(key) is not None]
            entries[path]={'states':{k:len(v) for k,v in candidates.items()},'complete':all(candidates.values())}
        classes[cls]={'paths':entries,'complete':all(d['complete'] for d in entries.values())}
    magic={}
    for school in MAGIC_TYPES:
        magic[school]={}
        for phase in MAGIC_CORE:
            keys=reg.choose('effect',magic=school.lower(),phase=phase)
            magic[school][phase]=sum(reg.bytes(k) is not None for k in keys)
    ready=all(c['complete'] for c in classes.values()) and all(all(x>0 for x in m.values()) for m in magic.values())
    return {'ready':bool(ready),'reason':'All required sprite variants found' if ready else 'Missing path-specific frames or magic effects','classes':classes,'magic':magic,'asset_count':len(reg.records)}
def visual_review(root):
    """Flag missing approved art for the final concept-to-game screenshot review."""
    root=Path(root)
    baseline=report(root)
    if not (root/'manifest.json').is_file():
        return {'ready':False,'review_needed':['No approved artwork pack has been installed'],
                'missing_portraits':list(PATHS),'missing_bodies':list(PATHS)}
    try:reg=Registry(root,root/'manifest.json')
    except (OSError,ValueError,KeyError,TypeError):
        return {'ready':False,'review_needed':['Approved artwork manifest cannot be opened'],
                'missing_portraits':list(PATHS),'missing_bodies':list(PATHS)}
    from asset_registry import select_character_sprite
    missing_portraits=[];missing_bodies=[]
    for cls,paths in PATHS.items():
        for path in paths:
            sample={'class':cls,'path':path,'sprite_seed':1}
            if select_character_sprite(reg,sample,'portrait') is None:missing_portraits.append(cls+' / '+path)
            if select_character_sprite(reg,sample,'body') is None:missing_bodies.append(cls+' / '+path)
    findings=[]
    if missing_portraits:findings.append('Portrait art missing for '+str(len(missing_portraits))+' class paths')
    if missing_bodies:findings.append('Battle body art missing for '+str(len(missing_bodies))+' class paths')
    if not baseline['ready']:findings.append('Some animation or magic effect frames remain missing')
    return {'ready':not findings,'review_needed':findings,'missing_portraits':missing_portraits,
            'missing_bodies':missing_bodies}

def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument('asset_root',type=Path)
    p.add_argument('--strict',action='store_true')
    args=p.parse_args()
    result=report(args.asset_root)
    print(json.dumps(result,indent=2))
    if args.strict and not result['ready']:raise SystemExit('Sprite coverage gate FAILED')
if __name__=='__main__':main()
