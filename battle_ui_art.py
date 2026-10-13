"""Static, named combat UI graphics; gameplay commands remain Python callbacks."""
from pathlib import Path
from io import BytesIO
import re
ACTIONS=('attack','magic','skills','item','defend','move','end_turn')
STATES=('plain','gold','colored','disabled')
class BattleUIArt:
 def __init__(self,root):self.root=Path(root)
 def button(self,label,state='gold'):
  action=str(label).strip().lower().replace(' ','_')
  if action not in ACTIONS or state not in STATES:return None
  path=self.root/('button_'+state+'_'+action+'.png')
  try:
   if path.stat().st_size>1000000:return None
   from PIL import Image
   with Image.open(path) as im:
    if im.format!='PNG' or im.width>512 or im.height>256 or im.convert('RGBA').getchannel('A').getextrema()[0]==255:return None
   return path.read_bytes()
  except (OSError,ValueError):return None
