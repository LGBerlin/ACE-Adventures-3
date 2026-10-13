"""Static keyboard shortcuts for the Tkinter adventure UI.

All actions call Python UI methods. Neither the narrator nor model chooses
which widget to create, where it goes, or which shortcut opens a panel.
"""
PANELS={
    '1':'Record','2':'Pack','3':'Abilities','4':'Journal',
    '5':'Story Tree','6':'Map','7':'Dice Board','8':'Town','9':'Shop'
}
def panel_for_key(key, in_combat=False):
    panel=PANELS.get(str(key))
    if in_combat and panel in ('Map','Town','Shop'):
        return None
    return panel
