"""Fixed art binding for the five Fighter paths; no AI asset selection."""
from pathlib import Path
import re
from io import BytesIO

PATHS=('martial_artist','paladin','knight','barbarian','dual_sword')
def slug(value):
 return re.sub(r'[^a-z0-9]+','_',str(value).strip().lower()).strip('_')
class FighterArt:
 def __init__(self,root):
  self.root=Path(root)
 def bytes(self,hero,kind):
  if hero.get('class')!='Fighter' or kind not in ('character','portrait','banner','nameplate'):return None
  path=slug(hero.get('path',''))
  # Existing game path "Swordsman" is the gameplay label for Dual Sword art.
  if path=='swordsman':path='dual_sword'
  if path not in PATHS:return None
  file=self.root/(kind+'_'+path+'.png')
  try:
   if not file.is_file() or file.stat().st_size>2_000_000:return None
   from PIL import Image
   with Image.open(file) as im:
    if im.format!='PNG' or im.width>1024 or im.height>1024:return None
    if im.convert('RGBA').getchannel('A').getextrema()[0]==255:return None
   return file.read_bytes()
  except (OSError,ValueError):return None
