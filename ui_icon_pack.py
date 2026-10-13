"""Load only explicitly named UI icons; unknown names retain native Tk skin."""
from pathlib import Path
from io import BytesIO
from PIL import Image
class UIIcons:
 def __init__(self,root):
  self.root=Path(root)
 def get(self,name):
  if name not in {'save','load','settings','journal','players','help','stats','trophy','refresh','close','chat'}:return None
  match={'save':'button_save','load':'button_load','settings':'button_icon_settings',
         'journal':'button_icon_journal','players':'button_icon_players',
         'help':'button_icon_help','stats':'button_icon_stats','trophy':'button_icon_trophy',
         'refresh':'button_refresh_green','close':'button_close','chat':'icon_chat_dots'}[name]
  file=self.root/(match+'.png')
  try:
   if file.stat().st_size>1000000:return None
   with Image.open(file) as im:
    if im.width>512 or im.height>512:return None
    if im.getchannel('A').getextrema()[0]==255:return None
    return file.read_bytes()
  except (OSError,ValueError,KeyError):return None
