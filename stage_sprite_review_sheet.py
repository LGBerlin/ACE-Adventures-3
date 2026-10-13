"""Review sheet of the actual downloaded sprite candidates, not synthetic previews."""
import json,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
def make(directory):
 root=Path(directory)
 entries=json.loads((root/'candidate report.json').read_text(encoding='utf8'))['candidates']
 width=1200;cell_w=200;cell_h=182;cols=6;rows=(len(entries)+cols-1)//cols
 output=Image.new('RGB',(width,rows*cell_h),(41,29,24))
 d=ImageDraw.Draw(output)
 for i,entry in enumerate(entries):
  x=(i%cols)*cell_w;y=(i//cols)*cell_h
  d.rectangle((x+3,y+3,x+cell_w-4,y+cell_h-4),fill=(226,205,163),outline=(192,143,71),width=3)
  try:
   with Image.open(root/entry['file']) as raw:
    im=raw.convert('RGBA');im.thumbnail((cell_w-24,126),Image.Resampling.NEAREST)
   tile=Image.new('RGBA',im.size,(63,47,39,255));tile.alpha_composite(im)
   output.paste(tile.convert('RGB'),(x+(cell_w-im.width)//2,y+9))
  except (ValueError,OSError):pass
  d.text((x+8,y+136),entry['category_guess'][:22],fill=(48,35,26))
  d.text((x+8,y+154),Path(entry['original']).name[:28],fill=(48,35,26))
 path=root/'Actual sprite candidate review.jpg'
 output.save(path,quality=88)
 return path
if __name__=='__main__':
 print(make(sys.argv[1]))
