"""Map downloadable sprite candidates to existing game UI slots, without approving licenses."""
import json,sys
from pathlib import Path
SLOTS={
 'body':('party battle character','character creation'),
 'armor':('equipment paper doll','inventory equipment slot'),
 'weapons':('combat attack','equipped weapon'),
 'enemies':('encounter character','turn order'),
 'effects':('magic cast effect','status indicator'),
 'environments':('exploration','battle backdrop','map region'),
 'ui':('wood/parchment border','button','dice board'),
 'items':('inventory','shop','loot')
}
def report(directory):
 root=Path(directory)
 raw=json.loads((root/'candidate report.json').read_text(encoding='utf-8'))
 selected={name:[] for name in SLOTS}
 for item in raw['candidates']:
  category=item['category_guess']
  if category not in selected:continue
  selected[category].append({'file':item['file'],'original':item['original'],'pack':item['pack'],
    'sha256':item['sha256'],'target_surfaces':SLOTS[category],
    'status':'AWAITING LICENSE AND ART-STYLE REVIEW'})
 outcome={'release_approved':False,'asset_source':raw['source_archive'],
    'candidate_total':len(raw['candidates']),'categories':selected,
    'missing_categories':[x for x,v in selected.items() if not v],
    'note':'Review original license and verify visual compatibility before indexing these in the approved sprite manifest.'}
 (root/'UI asset candidates.json').write_text(json.dumps(outcome,indent=2),encoding='utf-8')
 return outcome
if __name__=='__main__':
 if len(sys.argv)!=2:raise SystemExit('Usage: python candidate_asset_report.py STAGED_DIRECTORY')
 result=report(sys.argv[1])
 print('Mapped',result['candidate_total'],'candidates; missing categories:',result['missing_categories'])
