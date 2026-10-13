"""Fixed Vessel class artwork; the AI never selects UI assets."""
from pathlib import Path
import re
PATHS=('monk','spirit_fighter','druid','cultist','priest')
KINDS=('character','portrait','banner')
def slug(v):return re.sub(r'[^a-z0-9]+','_',str(v).strip().lower()).strip('_')
class VesselArt:
 def __init__(self,root):self.root=Path(root)
 def bytes(self,hero,kind):
  if str(hero.get('class','')).casefold()!='vessel' or kind not in KINDS:return None
  path=slug(hero.get('path',''))
  if path not in PATHS:return None
  candidate=self.root/(kind+'_'+path+'.png')
  try:
   if not candidate.is_file() or candidate.stat().st_size>2000000:return None
   from PIL import Image
   with Image.open(candidate) as im:
    if im.format!='PNG' or im.width>1024 or im.height>1024:return None
    if im.convert('RGBA').getchannel('A').getextrema()[0]==255:return None
   return candidate.read_bytes()
  except (OSError,ValueError):return None
