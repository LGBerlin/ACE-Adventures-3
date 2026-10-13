"""Deterministic Rogue path artwork lookup; never allow model-selected files."""
from pathlib import Path
import re

PATHS=('thief','ranger','assassin','arcane_trickster')
KINDS=('sprite','portrait','badge')
def slug(value):
 return re.sub(r'[^a-z0-9]+','_',str(value).strip().lower()).strip('_')
class RogueArt:
 def __init__(self,root):
  self.root=Path(root)
 def bytes(self,hero,kind):
  if str(hero.get('class','')).casefold()!='rogue' or kind not in KINDS:return None
  path=slug(hero.get('path',''))
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
