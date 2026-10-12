"""Optional local ComfyUI illustration generator.

Generation is explicit and runs off the Tk thread. Outputs are data-only PNGs,
never executable workflows from a remote party. Only loopback is contacted.
"""
import json,os,random,time,urllib.parse,urllib.request
from pathlib import Path

BASE='http://127.0.0.1:8188'
MAX_JSON=1_000_000
MAX_IMAGE=14_000_000
PLACES={'square':'medieval town square with bell tower and stone streets',
        'tavern':'cozy medieval fantasy tavern fireplace oak furniture',
        'market':'medieval herb market stalls hanging apothecary plants',
        'well':'overgrown ancient stone well with runes and moss',
        'forest':'eerie enchanted forest path ancient broken stone arch',
        'battle':'mysterious woodland ruins clearing for RPG battle'}

def _read(url,body=None,limit=MAX_JSON,timeout=10):
    req=urllib.request.Request(url,data=body,headers={'Content-Type':'application/json'} if body is not None else {},method='POST' if body is not None else 'GET')
    with urllib.request.urlopen(req,timeout=timeout) as response:
        if response.status!=200:raise OSError('ComfyUI returned '+str(response.status))
        payload=response.read(limit+1)
    if len(payload)>limit:raise ValueError('Response too large')
    return payload

def _json(path,body=None,transport=None):
    raw=(transport or _read)(BASE+path,json.dumps(body).encode() if body is not None else None)
    data=json.loads(raw)
    if not isinstance(data,dict):raise ValueError('Malformed ComfyUI response')
    return data

def available_checkpoints(transport=None):
    data=_json('/object_info/CheckpointLoaderSimple',transport=transport)
    item=data.get('CheckpointLoaderSimple',{}).get('input',{}).get('required',{}).get('ckpt_name',[])
    choices=item[0] if isinstance(item,list) and item else []
    return [name for name in choices if isinstance(name,str) and name.endswith(('.safetensors','.ckpt'))]

def workflow(place,checkpoint,seed=None):
    if place not in PLACES:raise ValueError('Unknown scene')
    if not isinstance(checkpoint,str) or not checkpoint.endswith(('.safetensors','.ckpt')):raise ValueError('Unsupported checkpoint')
    description=PLACES[place]
    positive='rich atmospheric handcrafted 16-bit pixel art RPG panorama, '+description+', side-view game background, detailed tiles, warm chiaroscuro, cohesive palette, no characters, no lettering, cinematic composition'
    negative='photorealistic, low quality, generic UI, letters, watermark, logos, modern objects, blurry, smeared pixels'
    return {'1':{'class_type':'CheckpointLoaderSimple','inputs':{'ckpt_name':checkpoint}},
            '2':{'class_type':'CLIPTextEncode','inputs':{'clip':['1',1],'text':positive}},
            '3':{'class_type':'CLIPTextEncode','inputs':{'clip':['1',1],'text':negative}},
            '4':{'class_type':'EmptyLatentImage','inputs':{'width':768,'height':384,'batch_size':1}},
            '5':{'class_type':'KSampler','inputs':{'model':['1',0],'positive':['2',0],'negative':['3',0],'latent_image':['4',0],'seed':random.randrange(2**31) if seed is None else int(seed),'steps':20,'cfg':7.0,'sampler_name':'euler','scheduler':'normal','denoise':1.0}},
            '6':{'class_type':'VAEDecode','inputs':{'samples':['5',0],'vae':['1',2]}},
            '7':{'class_type':'SaveImage','inputs':{'images':['6',0],'filename_prefix':'ACE3_Background'}}}

def generate(place,root,checkpoint=None,timeout=600,transport=None,poll_delay=2,progress=None):
    """Queue a simple SD-style workflow and write one verified PNG atomically."""
    if place not in PLACES:raise ValueError('Unknown scene')
    models=available_checkpoints(transport=transport)
    if not models:raise ValueError('ComfyUI has no compatible checkpoint installed')
    model=checkpoint if checkpoint in models else models[0]
    graph=workflow(place,model)
    response=_json('/prompt',{'prompt':graph},transport)
    prompt_id=response.get('prompt_id')
    if not isinstance(prompt_id,str) or len(prompt_id)>100 or not prompt_id:raise ValueError('ComfyUI did not accept prompt')
    end=time.monotonic()+min(timeout,1200)
    image_info=None
    while time.monotonic()<end:
        history=_json('/history/'+urllib.parse.quote(prompt_id,safe=''),transport=transport)
        record=history.get(prompt_id)
        if isinstance(record,dict):
            status=record.get('status',{})
            if isinstance(status,dict) and status.get('status_str')=='error':raise RuntimeError('ComfyUI image generation failed')
            outputs=record.get('outputs',{})
            node=outputs.get('7',{}) if isinstance(outputs,dict) else {}
            images=node.get('images',[]) if isinstance(node,dict) else []
            if images:
                image_info=images[0];break
        if progress:progress('Generating illustration...')
        time.sleep(max(0,poll_delay))
    if not isinstance(image_info,dict):raise TimeoutError('ComfyUI did not complete in time')
    name=image_info.get('filename','');folder=image_info.get('subfolder','');kind=image_info.get('type','output')
    if not isinstance(name,str) or not name.lower().endswith('.png') or '/' in name or '\\' in name:raise ValueError('Invalid generated filename')
    if not isinstance(folder,str) or '..' in folder or '\\' in folder:raise ValueError('Invalid generated folder')
    query=urllib.parse.urlencode({'filename':name,'subfolder':folder,'type':kind})
    data=(transport or _read)(BASE+'/view?'+query,None,MAX_IMAGE,25)
    if not isinstance(data,bytes) or not data.startswith(b'\x89PNG\r\n\x1a\n') or len(data)>MAX_IMAGE:raise ValueError('Invalid generated PNG')
    directory=Path(root)/'generated'/'locations'
    if directory.is_symlink():raise ValueError('Unsafe artwork destination')
    directory.mkdir(parents=True,exist_ok=True)
    dest=directory/(place+'.png');tmp=directory/(place+'.tmp')
    try:
        with tmp.open('wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
        os.replace(tmp,dest)
    finally:
        if tmp.exists():tmp.unlink()
    return dest