"""Presentation-only, named art for adventure dialogue and story chrome."""
from pathlib import Path
ART={'speaker_narrator','speaker_npc','speaker_player','speaker_dm',
     'divider_gold_short','divider_gold_dotted','divider_gold_arrow',
     'note_empty','note_light','portrait_frame_plain','portrait_frame_gold',
     'button_continue','button_back','input_backing'}
class OverallUIArt:
 def __init__(self,root):self.root=Path(root)
 def read(self,name):
  if name not in ART:return None
  file=self.root/(name+'.png')
  try:
   if not file.is_file() or file.stat().st_size>2000000:return None
   from PIL import Image
   with Image.open(file) as im:
    if im.format!='PNG' or im.width>1024 or im.height>512:return None
    if im.convert('RGBA').getchannel('A').getextrema()[0]==255:return None
   return file.read_bytes()
  except (OSError,ValueError):return None
