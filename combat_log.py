"""Persisted, bounded event history for the tabletop battle panel.

The ledger records resolved rule outcomes only and does not modify HP or rewards.
"""
LIMIT=60
def append(campaign, *, actor, kind, description, hp=None):
    if not campaign.get("started"):raise ValueError("Campaign has not started.")
    entry={"actor":str(actor)[:80],"kind":str(kind)[:32],
           "description":str(description)[:600],"turn":campaign.get("turn",0)}
    if hp is not None:entry["hp"]=max(0,int(hp))
    log=campaign.setdefault("combat_log",[])
    log.append(entry)
    del log[:-LIMIT]
    return entry
def recent(campaign,limit=12):
    return list(campaign.get("combat_log",[])[-max(0,min(LIMIT,int(limit))):])
