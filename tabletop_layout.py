"""Phase 2 adaptive tabletop geometry independent of game rules."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Geometry:
    sidebar: int
    scene_height: int
    party_columns: int
    compact: bool

def for_window(width,height,party_count=1,in_battle=False):
    width=max(700,int(width));height=max(550,int(height))
    party_count=max(1,int(party_count))
    compact=width<1150
    sidebar=300 if compact else 340
    # Combat adds a sizeable rules HUD; compress scenery to keep actions visible.
    scene_height=max(120,min(255 if in_battle else 370,int(height*(.21 if in_battle else .31))))
    columns=2 if compact and party_count>3 else min(party_count,4)
    return Geometry(sidebar,scene_height,columns,compact)

def scene_caption(place,enemy=None):
    return ('ENCOUNTER · '+str(enemy['name']) if enemy else 'EXPLORING · '+place).upper()
