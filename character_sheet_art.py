"""Presentation-only character-sheet art. Campaign data always comes from game.py."""
from pathlib import Path
from io import BytesIO
TABS={'Record':'tab_overview','Pack':'tab_equipment','Abilities':'tab_skills'}
class CharacterSheetArt:
 def __init__(self,root):self.root=Path(root)
 def read(self,key):
  if key not in set(TABS.values()):return None
  path=self.root/(key+'.png')
  try:
   if path.stat().st_size>1000000:return None
   from PIL import Image
   with Image.open(path) as img:
    if img.format!='PNG' or img.width>600 or img.height>200:return None
    if img.convert('RGBA').getchannel('A').getextrema()[0]==255:return None
   return path.read_bytes()
  except (OSError,ValueError):return None
 def tab(self,panel):
  key=TABS.get(panel)
  return self.read(key) if key else None
