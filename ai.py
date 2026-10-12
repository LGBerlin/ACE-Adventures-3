"""Compatibility gateway for local Ollama narration."""
import json,urllib.request
import dungeon_master
URL=dungeon_master.BASE_URL
MODEL=dungeon_master.MODEL
def status(timeout=2):
    try:
        with urllib.request.urlopen(URL+'/api/tags',timeout=timeout) as r:payload=json.load(r)
        names=[x.get('name','') for x in payload.get('models',[])]
        return ('ready' if any(x.startswith(MODEL) for x in names) else 'model missing',names)
    except Exception:return ('offline',[])
def narrate(c,latest,timeout=45):
    return dungeon_master.narrate(c,latest,timeout=timeout)
