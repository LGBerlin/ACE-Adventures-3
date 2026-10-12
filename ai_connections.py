"""Optional local AI-service health checks; never install/start services.
Only fixed loopback endpoints are accessed.
"""
import json
import urllib.request
OLLAMA='http://127.0.0.1:11434'
COMFYUI='http://127.0.0.1:8188'
def _get(url,timeout=2,opener=None):
    if opener is None:
        with urllib.request.urlopen(url,timeout=timeout) as response:
            if response.status!=200:raise OSError('Unhealthy response')
            return json.load(response)
    return opener(url,timeout)
def ollama_status(model='qwen3.5:4b',timeout=2,opener=None):
    try:
        payload=_get(OLLAMA+'/api/tags',timeout,opener)
        models=[x['name'] for x in payload.get('models',[]) if isinstance(x,dict) and isinstance(x.get('name'),str)]
        return {'service':'ollama','online':True,'ready':model in models,'models':models,
                'message':'Ready' if model in models else 'Online; model not downloaded'}
    except (OSError,ValueError,TypeError,KeyError):
        return {'service':'ollama','online':False,'ready':False,'models':[],'message':'Offline or inaccessible'}
def comfyui_status(timeout=2,opener=None):
    try:
        data=_get(COMFYUI+'/system_stats',timeout,opener)
        if not isinstance(data,dict) or not isinstance(data.get('system'),dict):raise ValueError('Unexpected response')
        return {'service':'comfyui','online':True,'ready':True,'message':'Ready (asset generation only)'}
    except (OSError,ValueError,TypeError,KeyError):
        return {'service':'comfyui','online':False,'ready':False,'message':'Offline or inaccessible'}
def all_statuses(timeout=2,opener=None):
    return {'ollama':ollama_status(timeout=timeout,opener=opener),'comfyui':comfyui_status(timeout=timeout,opener=opener)}
