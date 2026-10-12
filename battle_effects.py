"""Deterministic lightweight VFX glyphs keyed by rules-authorized effect IDs.

Only paint when a completed game action supplies a cue. No timers, remote
assets or AI-generated canvas commands.
"""
import math
import visual_mapping

PALETTE={
 'earth_impact':'#ad9669','water_impact':'#77c7d7','air_gust':'#d5e6de',
 'fire_impact':'#f2a15c','lightning_impact':'#f6dc77',
 'gravity_pulse':'#a49bd4','blood_pulse':'#ba626d','illusion_glimmer':'#d5a5e4',
 'light_burst':'#f6df9a','dark_pulse':'#8a829f','healing_aura':'#95d9ad',
 'time_ring':'#86c8c4','creation_sigil':'#dfa8c6','chaos_spark':'#e9b48f',
 'physical_impact':'#edd5a5','spirit_impact':'#a9c4e9','magic_impact':'#b9c8e8'
}
assert set(visual_mapping.MAGIC_EFFECTS.values()).issubset(PALETTE)

def paint(cv,effect,cx,cy,tier=1):
 """Paint up to four bounded geometric effect layers on an existing Tk canvas."""
 if not effect or effect not in PALETTE:return False
 tier=max(1,min(4,int(tier)))
 color=PALETTE[effect]
 for i in range(tier):
  radius=12+14*i
  if effect in ('lightning_impact','chaos_spark','fire_impact','physical_impact'):
   cv.create_line(cx-radius,cy+radius,cx-radius//3,cy-radius,
                  cx+radius//3,cy+radius//3,cx+radius,cy-radius,
                  fill=color,width=2+i)
  elif effect in ('earth_impact','creation_sigil'):
   cv.create_polygon(cx-radius,cy+radius,cx,cy-radius,
                     cx+radius,cy+radius,outline=color,fill='',width=2)
  else:
   cv.create_oval(cx-radius,cy-radius,cx+radius,cy+radius,outline=color,width=2+i)
 cv.create_text(cx,cy,text='✦' if effect!='healing_aura' else '+',
                fill=color,font=('Georgia',13+tier*3,'bold'))
 return True
