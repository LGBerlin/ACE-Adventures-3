"""Render approved, named combat effects without model-controlled UI assembly.

A local effects.json maps stable effect IDs to PNG filenames. Unmapped effects
fall back to the existing procedural battle_effects renderer.
"""
from pathlib import Path
from io import BytesIO
import json
import re

NAME = re.compile(r'^[a-z][a-z0-9_]{1,60}$')

class Effects:
    def __init__(self, directory):
        self.directory=Path(directory)
        self.mapping={}
        index=self.directory/'effects.json'
        if index.is_file():
            try:
                data=json.loads(index.read_text(encoding='utf-8'))
                if not isinstance(data,dict):return
                for effect,filename in data.items():
                    if NAME.fullmatch(effect) and isinstance(filename,str) and re.fullmatch(r'(?:effect|battle)_[0-9]{3}\.png',filename):
                        self.mapping[effect]=filename
            except (ValueError,OSError):
                pass

    def paint(self, canvas, effect_id, x, y, size=120):
        """Return False if an effect is not configured; never invent artwork."""
        filename=self.mapping.get(effect_id)
        if not filename:return False
        target=self.directory/filename
        try:
            if not target.is_file() or target.stat().st_size>3_000_000:return False
            from PIL import Image,ImageTk
            with Image.open(target) as original:
                if original.width>2048 or original.height>2048:return False
                image=original.convert('RGBA')
                if image.getextrema()[3][0]==255:return False
                image.thumbnail((size,size),Image.Resampling.NEAREST)
                photo=ImageTk.PhotoImage(image,master=canvas)
            canvas.create_image(x,y,image=photo,anchor='center')
            canvas._ace_effect_refs=getattr(canvas,'_ace_effect_refs',[])+[photo]
            return True
        except (OSError,ValueError,ImportError):
            return False
