"""Bounded LPC layered sprite-sheet assembly; generated only when needed.

Consumes local, approved sheets. No live AI generation and no animation timer.
Outputs composite sheets that share the exact frame grid.
"""
from io import BytesIO
from PIL import Image
MAX_PIXELS=2_000_000
MAX_LAYERS=8

def composite_layers(layers, frame_width=64, frame_height=64):
    if not isinstance(layers,(list,tuple)) or not 1<=len(layers)<=MAX_LAYERS:
        raise ValueError('Expected 1 to 8 approved layers')
    if frame_width<=0 or frame_height<=0 or frame_width>256 or frame_height>256:
        raise ValueError('Unsupported frame dimensions')
    canvas=None
    for content in layers:
        if not isinstance(content,bytes) or len(content)>4_000_000:
            raise ValueError('Invalid layer bytes')
        with Image.open(BytesIO(content)) as src:
            if src.format!='PNG' or src.width*src.height>MAX_PIXELS:
                raise ValueError('Unsupported or oversized sprite layer')
            if src.width%frame_width or src.height%frame_height:
                raise ValueError('Layer does not align to frame grid')
            image=src.convert('RGBA')
        if canvas is None:
            canvas=Image.new('RGBA',image.size,(0,0,0,0))
        elif canvas.size!=image.size:
            raise ValueError('All layers must share identical frame dimensions')
        canvas.alpha_composite(image)
    out=BytesIO();canvas.save(out,format='PNG',optimize=True)
    return out.getvalue()

def frame_bounds(sheet_width,sheet_height,frame_width=64,frame_height=64):
    if sheet_width%frame_width or sheet_height%frame_height:
        raise ValueError('Frame size mismatch')
    return [(x,y,x+frame_width,y+frame_height)
            for y in range(0,sheet_height,frame_height)
            for x in range(0,sheet_width,frame_width)]
