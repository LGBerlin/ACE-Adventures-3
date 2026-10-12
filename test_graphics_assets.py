import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import tkinter as tk
import art
class GraphicsAssetTests(unittest.TestCase):
 def test_addon_image_and_fallback(self):
  root=tk.Tk();root.withdraw()
  try:
   cv=tk.Canvas(root,width=760,height=310);cv.pack()
   with tempfile.TemporaryDirectory() as home:
    with patch.object(Path,'home',return_value=Path(home)):
     art.world(cv,'square',width=760,height=310)
     self.assertGreater(len(cv.find_all()),10)
     storage=Path(home)/'Library/Application Support/ACE Adventures 3/addons'
     directory=storage/'versions/1.0.0/assets/locations';directory.mkdir(parents=True)
     image=tk.PhotoImage(master=cv,width=760,height=310)
     image.put('#335544',to=(0,0,760,310))
     image.write(str(directory/'square.png'),format='png')
     (storage/'active.json').write_text(json.dumps({'version':'1.0.0'}))
     cv.delete('all');art.world(cv,'square',width=760,height=310)
     types=[cv.type(i) for i in cv.find_all()]
     self.assertIn('image',types)
  finally:root.destroy()
if __name__=='__main__':unittest.main()