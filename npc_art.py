"""Reviewed NPC artwork uses fixed gameplay roles rather than generated choices."""
from pathlib import Path
from io import BytesIO
import re
ROLES={'merchant','noble','blacksmith','hooded_scholar','armorer','priest','innkeeper','herbalist','mage','guard','apothecary','scholar'}
def slug(s):return re.sub(r'[^a-z0-9]+','_',str(s).lower()).strip('_')
class NPCArt:
 def __init__(self,root):self.root=Path(root)
 def bytes(self,role,kind='portrait'):
  role=slug(role)
  if role not in ROLES or kind not in ('portrait','character'):return None
  file=self.root/(kind+'_'+role+'.png')
  try:
   if file.stat().st_size>2000000:return None
   from PIL import Image
   with Image.open(file) as im:
    if im.format!='PNG' or im.width>1024 or im.height>1024 or im.convert('RGBA').getchannel('A').getextrema()[0]==255:return None
   return file.read_bytes()
  except (OSError,ValueError):return None
