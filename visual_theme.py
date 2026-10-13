"""Phase 2 tabletop visual tokens and readable desktop presentation.

Centralized colors keep every native Tk screen visually consistent.
All rendering is deterministic, lightweight and independent of optional AI art.
"""
COLORS={
 'background':'#251a16',
 'wood':'#543624',
 'wood_dark':'#322119',
 'wood_highlight':'#795032',
 'parchment':'#efe0bf',
 'parchment_light':'#f8edcf',
 'parchment_shadow':'#d1b989',
 'ink':'#362820',
 'muted_ink':'#73573b',
 'brass':'#bc9252',
 'brass_light':'#e9c88b',
 'ivory':'#ffeed0',
 'forest':'#547653',
 'mana':'#587e9c',
 'danger':'#9f5147',
}
FONT='Georgia'
NAVIGATION=('Character Sheet','Inventory','Abilities','Journal','Story Tree','Shop','Map','Dice Board','Town')

def contrast(foreground,background):
 def luminance(rgb):
  values=[int(rgb[i:i+2],16)/255 for i in (1,3,5)]
  values=[v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4 for v in values]
  return sum(a*b for a,b in zip(values,(0.2126,0.7152,0.0722)))
 a,b=sorted((luminance(foreground),luminance(background)),reverse=True)
 return (a+0.05)/(b+0.05)

def meter(canvas,current,maximum,width=210,height=13,fill=None):
 """Paint a static high-contrast resource meter with bounded values."""
 width=max(10,int(width));height=max(4,int(height))
 maximum=max(1,int(maximum))
 current=max(0,min(maximum,int(current)))
 fill=fill or COLORS['forest']
 canvas.create_rectangle(0,0,width,height,fill=COLORS['parchment_shadow'],outline=COLORS['wood_dark'])
 occupied=int((width-2)*current/maximum)
 if occupied:canvas.create_rectangle(1,1,1+occupied,height-1,fill=fill,outline='')
 return occupied
