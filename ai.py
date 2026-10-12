"""Compatibility gateway for the same local Ollama model used by the game."""
import dungeon_master
import ai_connections

URL=dungeon_master.BASE_URL
MODEL=dungeon_master.MODEL

def status(timeout=2):
    """Return model availability consistently with the AI Connections screen."""
    result=ai_connections.ollama_status(model=MODEL,timeout=timeout)
    return ('ready' if result['ready'] else 'model missing' if result['online'] else 'offline',result['models'])

def narrate(c,latest,timeout=45):
    return dungeon_master.narrate(c,latest,timeout=timeout)
