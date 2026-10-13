"""Install battle PNG sprites without assigning incorrect effects automatically.

Usage: python install_battle_effects.py 'ACE Adventures 3 Battle Effects Pack.zip'
"""
from pathlib import Path
from io import BytesIO
import json,re,sys,zipfile
from PIL import Image
from magic_effect_pack import NAME
DEST=Path.home()/'Library'/'Application Support'/'ACE Adventures 3'/'battle effects'
def install(archive,dest=DEST):
 dest=Path(dest);dest.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(archive) as z:
  paths=[p for p in z.namelist() if re.fullmatch(r'battle effects/battle_[0-9]{3}\.png',p)]
  if not paths or len(paths)>300 or len(paths)!=len(set(paths)):raise ValueError('Invalid battle pack')
  for path in paths:
   raw=z.read(path)
   if len(raw)>3_000_000:raise ValueError('Effect exceeds file size limit')
   with Image.open(BytesIO(raw)) as im:
    if im.format!='PNG' or im.width>2048 or im.height>2048 or im.getchannel('A').getextrema()[0]==255:
     raise ValueError('Not a transparent battle PNG')
    im.load()
   (dest/Path(path).name).write_bytes(raw)
 # Existing approved effect assignments survive additions/replacements.
 index=dest/'effects.json'
 if not index.is_file():index.write_text('{}',encoding='utf8')
 return len(paths)
if __name__=='__main__':
 if len(sys.argv)!=2:raise SystemExit('Usage: python install_battle_effects.py PACK.zip')
 print('Installed',install(sys.argv[1]),'effect candidates.')
