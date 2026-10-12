"""Stage small candidate sprites from the archived source packs.

Not an approval step: preserves provenance and requires licence/art review before
a production asset manifest may be published.
"""
import csv,hashlib,io,json,re,sys,zipfile
from pathlib import Path,PurePosixPath
from PIL import Image
KEYWORDS={
 'fighter':('fighter','knight','warrior','sword','plate'),
 'rogue':('rogue','thief','assassin','ranger'),
 'mage':('mage','wizard','spellcaster','robe'),
 'vessel':('monk','druid','priest','healer'),
 'enemy':('goblin','skeleton','wolf','slime','monster','orc','spider'),
 'magic':('fire','water','earth','wind','lightning','gravity','blood','illusion','shadow','heal','spell','magic','effect'),
 'environment':('town','house','forest','tavern','cave','castle','tileset'),
 'ui':('interface','button','panel','frame','parchment','inventory','health','mana')
}
def classify(path):
 s=path.lower()
 return [k for k,words in KEYWORDS.items() if any(w in s for w in words)]
def stage(source,dest,max_images=180):
 dest=Path(dest);dest.mkdir(parents=True,exist_ok=True)
 entries=[];counts={k:0 for k in KEYWORDS};licenses=[]
 with zipfile.ZipFile(source) as outer:
  for outer_entry in outer.infolist():
   if not outer_entry.filename.lower().endswith('.zip') or outer_entry.file_size>450_000_000:continue
   pack=PurePosixPath(outer_entry.filename).name
   try:
    with zipfile.ZipFile(io.BytesIO(outer.read(outer_entry))) as archive:
     for member in archive.infolist():
      if member.is_dir():continue
      name=member.filename;extension=PurePosixPath(name).suffix.lower()
      if any(x in name.lower() for x in ('license','licence','credits','attribution','readme')) and extension in ('.txt','.md','.license'):
       licenses.append({'pack':pack,'name':name})
      if extension!='.png' or not 0<member.file_size<=2_000_000 or len(entries)>=max_images:continue
      categories=classify(name)
      if not categories:continue
      category=min(categories,key=lambda x:counts[x])
      if counts[category]>=30:continue
      try:
       blob=archive.read(member)
       with Image.open(io.BytesIO(blob)) as im:
        im.verify()
       with Image.open(io.BytesIO(blob)) as im:
        if im.width>2048 or im.height>2048 or im.width<16 or im.height<16:continue
        dimensions=[im.width,im.height]
      except Exception:continue
      index=counts[category]+1
      out=dest/category/f'{category}_{index:03d}.png'
      out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(blob)
      entries.append({'file':str(out.relative_to(dest)),'original':name,'pack':pack,
                      'category_guess':category,'dimensions':dimensions,'sha256':hashlib.sha256(blob).hexdigest(),
                      'review':'UNREVIEWED - DO NOT DISTRIBUTE'})
      counts[category]+=1
   except (zipfile.BadZipFile,RuntimeError,ValueError):continue
 report={'source_archive':Path(source).name,'candidate_count':len(entries),'counts':counts,
         'candidates':entries,'licence_documents':licenses,
         'release_approved':False,
         'warning':'Candidate selection is automatic, not licence clearance, animation verification, or style approval.'}
 (dest/'candidate report.json').write_text(json.dumps(report,indent=2))
 return report
if __name__=='__main__':
 if len(sys.argv)!=3:raise SystemExit('Usage: python stage_sprite_candidates.py outer.zip destination')
 result=stage(sys.argv[1],sys.argv[2]);print(json.dumps(result['counts'],indent=2))
