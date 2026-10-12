"""Exercise authenticated, uncached preparation on representative dependency/rig types."""
import json,time
from pathlib import Path
import httpx
ROOT=Path(__file__).resolve().parents[2];STATE=ROOT/'Assets/LocalWorking/AssetWorkbench';s=json.loads((STATE/'runtime/session.json').read_text());origin=f'http://127.0.0.1:{s["port"]}'
results=[]
with httpx.Client(base_url=origin,timeout=30,headers={'Origin':origin}) as client:
 auth=client.post('/api/v1/session',json={'token':s['token']});auth.raise_for_status();client.headers['x-csrf-token']=auth.json()['csrf']
 for pid,needle in [('anim-movement-animset-pro','WalkFwdLoop'),('anim-combat-knife-animation-kit','Attack_1')]:
  pack=client.get('/api/v1/animation-packs/'+pid).json();clip=next(c for c in pack['clips'] if needle in c['name'] and c['id']!=pack['default_clip']);url=f'/api/v1/animation-packs/{pid}/clips/{clip["id"]}'
  before=client.get(url).json();started=time.monotonic();request=client.post(url+'/prepare');request.raise_for_status()
  while True:
   status=client.get(url).json()
   if status['status'] in ('ready','failed'):break
   assert time.monotonic()-started<300,'Preparation timed out';time.sleep(1)
  row={'asset_id':pid,'clip':clip,'before':before['status'],'status':status['status'],'elapsed_s':round(time.monotonic()-started,2)}
  if status['status']=='ready':
   response=client.get(status['model']['file_url']);response.raise_for_status();row['bytes']=len(response.content);row['model']=status['model']
  else:row['code']=status.get('code')
  results.append(row);print(pid,row['status'],row['elapsed_s'],flush=True)
(STATE/'runs/animation-packs/lazy-checks.json').write_text(json.dumps(results,indent=2));assert all(r['status']=='ready' for r in results)
