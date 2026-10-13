"""Pixel-art controls rendered at runtime as reusable *real Tk widgets*.

The label owns a callback; decoration is an opaque nearest-neighbour pixel skin,
not a screenshot with dead hotspots. No external service or generated mockups.
"""
from functools import lru_cache
import tkinter as tk

PALE = (231, 208, 158)
INK = '#2d2119'
GOLD = (226, 171, 83)
DARK = (37, 25, 24)
IRON = (82, 76, 72)
WOOD = (76, 44, 32)
GREEN = (54, 92, 55)

@lru_cache(maxsize=256)
def skin(width, height, light=False, highlighted=False):
    from PIL import Image, ImageDraw
    # Pixel art at half resolution, enlarged ONLY via NEAREST.
    w=max(28,width//2); h=max(17,height//2)
    image=Image.new('RGB',(w,h),DARK)
    d=ImageDraw.Draw(image)
    edge=GOLD if highlighted else IRON
    base=PALE if light else (62,39,31)
    inner=(248,227,184) if (light and highlighted) else ((102,63,44) if highlighted else base)
    d.rectangle((1,1,w-2,h-2),fill=edge)
    d.rectangle((3,3,w-4,h-4),fill=WOOD)
    d.rectangle((5,4,w-6,h-5),fill=inner)
    # Pixel corner ornaments, wood-grain hatching, metallic corner rivets.
    for x in (3,w-6):
        for y in (3,h-6):
            d.rectangle((x,y,x+2,y+2),fill=(31,34,38))
            d.point((x+1,y+1),fill=GOLD)
    for y in range(7,h-5,7):
        d.line((9,y,min(w-10,19+(y*11)%max(20,w-30)),y),fill=(171,137,91) if light else (97,62,43))
    d.line((8,5,w-9,5),fill=(249,223,165) if light else (159,101,61))
    d.line((8,h-6,w-9,h-6),fill=(151,108,69) if light else (27,20,19))
    return image.resize((w*2,h*2),Image.Resampling.NEAREST)

class PixelButton(tk.Label):
    """Keyboard-accessible clickable picture button; compatible with pack/grid."""
    def __init__(self,parent,text,command,light=False):
        self._command=command
        self._light=bool(light)
        self._over=False
        width=max(104,min(285,32+len(text)*8))
        height=46
        self._images={}
        from PIL import ImageTk
        for highlighted in (False,True):
            self._images[highlighted]=ImageTk.PhotoImage(
                skin(width,height,self._light,highlighted),master=parent)
        super().__init__(parent,text=text,image=self._images[False],
                         compound='center',font=('Georgia',11,'bold'),
                         fg=INK if light else '#f7e2b8',
                         bg='#302019',bd=0,highlightthickness=0,
                         cursor='hand2',takefocus=True,padx=0,pady=0)
        self.bind('<Enter>',lambda event:self._hover(True))
        self.bind('<Leave>',lambda event:self._hover(False))
        self.bind('<FocusIn>',lambda event:self._hover(True))
        self.bind('<FocusOut>',lambda event:self._hover(False))
        self.bind('<ButtonRelease-1>',self._click)
        self.bind('<Return>',lambda event:self.invoke())
        self.bind('<space>',lambda event:self.invoke())
    def _hover(self,on):
        self._over=on
        self.configure(image=self._images[bool(on)])
    def _click(self,event):
        if self.winfo_containing(event.x_root,event.y_root)==self:
            self.invoke()
    def invoke(self):
        if self._command:
            return self._command()
