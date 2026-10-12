"""Bounded, save-compatible audit trail of actual rules-engine D20 rolls."""
MAX_ROLLS = 40
FIELDS = ("roll", "modifier", "total", "dc", "degree")
def record(campaign, result, action):
    """Record only genuine resolved dice checks, never narrative-only actions."""
    if not result.get("roll_required"):
        return None
    if not all(k in result for k in ("roll", "modifier", "total", "dc")):
        return None
    values = [result[k] for k in ("roll", "modifier", "total", "dc")]
    if not all(isinstance(v, int) and not isinstance(v, bool) for v in values):
        return None
    if not 1 <= result["roll"] <= 20:
        return None
    entry = {key: result.get(key) for key in FIELDS}
    entry["action"] = str(action)[:160]
    entry["turn"] = campaign.get("turn", 0)
    entry["character_id"] = campaign["characters"][campaign["active"]]["id"]
    ledger = campaign.setdefault("dice_history", [])
    ledger.append(entry)
    del ledger[:-MAX_ROLLS]
    return entry
def history(campaign):
    return list(campaign.get("dice_history", [])[-MAX_ROLLS:])
