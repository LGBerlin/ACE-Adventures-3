import io,unittest
from PIL import Image
from sprite_compositor import composite_layers,frame_bounds

def layer(size,color):
    f=io.BytesIO();Image.new('RGBA',size,color).save(f,format='PNG');return f.getvalue()

class SpriteCompositeTests(unittest.TestCase):
 def test_correct_layers(self):
    result=composite_layers([layer((128,64),(200,0,0,255)),layer((128,64),(0,0,200,128))])
    with Image.open(io.BytesIO(result)) as im:
        self.assertEqual(im.size,(128,64))
        self.assertEqual(im.mode,'RGBA')
        self.assertGreater(im.getpixel((0,0))[2],0)
 def test_reject_mismatch(self):
    with self.assertRaises(ValueError):
        composite_layers([layer((128,64),(255,0,0,255)),layer((64,64),(0,0,0,255))])
 def test_reject_non_frame_alignment(self):
    with self.assertRaises(ValueError):composite_layers([layer((100,100),(0,0,0,255))])
 def test_frame_grid(self):
    self.assertEqual(len(frame_bounds(832,1344)),273)
 def test_compositing_does_not_change_input(self):
    source=layer((64,64),(30,40,50,255))
    before=bytes(source)
    composite_layers([source])
    self.assertEqual(source,before)
