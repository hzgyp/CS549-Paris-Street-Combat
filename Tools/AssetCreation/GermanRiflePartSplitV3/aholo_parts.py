"""One quoted, gift-only part-split of the unchanged generated CC0 rifle base.

Private state is excluded by LocalWorking. No secrets/URLs in stdout.
No automatic submission retries, no paid top-ups or model regeneration.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib import request, error, parse

ROOT = Path(__file__).resolve().parents[3]
STORE = ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-parts-v3'
STATE = STORE/'api-state'
BASE = 'https://api.aholo3d.com/global'
ENDPOINT = '/lux3d/v1/part-split/task/create'
KEY = Path('D:/0.Rutgers/CS549/AHOLO api key.txt')
SOURCE_TASK = 3919866
SOURCE_SHA = 'a8ccfed78eed6da13de2070b86cec6bd32357218dd0c0cfb4efe6ae512387b60'
sys.stdout.reconfigure(encoding='utf-8')

class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError('Authenticated redirect refused')

def now():
    return datetime.now(timezone.utc).isoformat()

def save(name, value):
    (STATE/name).write_text(json.dumps(value, indent=2), encoding='utf-8')

def load(name):
    return json.loads((STATE/name).read_text(encoding='utf-8'))

def api(method, path, body=None):
    req=request.Request(BASE+path,
        data=json.dumps(body).encode() if body is not None else None,
        headers={'Authorization':KEY.read_text(encoding='utf-8-sig').strip(),
                 'Content-Type':'application/json'},method=method)
    try:
        with request.build_opener(NoRedirect).open(req,timeout=35) as response:
            raw=json.load(response)
    except error.HTTPError as exc:
        # Retain raw diagnostic only privately, never echo server messages/URLs.
        try:
            payload=json.load(exc)
        except Exception:
            payload={'unparsed':True}
        save('last-http-error.json',{'endpoint':path,'status':exc.code,'response':payload})
        raise RuntimeError('HTTP '+str(exc.code)+' at '+path.split('?')[0]) from None
    if str(raw.get('c'))!='0':
        raise RuntimeError('API business code '+str(raw.get('c')))
    return raw['d']

def balance():
    return api('GET','/lux3d/v1/account/balance?source=1')

def original_url():
    r=api('GET','/lux3d/v1/generate/task/get?taskid='+str(SOURCE_TASK))
    if int(r.get('taskId',0))!=SOURCE_TASK or int(r['status'])!=3 or r.get('bizId')!='LUX_3D':
        raise RuntimeError('Original task mismatch')
    save('original-task.json',r)
    for item in r.get('outputs') or []:
        url=item.get('content','');u=parse.urlparse(url)
        if u.scheme=='https' and Path(u.path).suffix.lower()=='.glb':
            # Anonymous request never sends the API key. Prove exact input bytes.
            h=hashlib.sha256();size=0
            with request.urlopen(url,timeout=45) as response:
                for chunk in iter(lambda:response.read(1024*1024),b''):
                    h.update(chunk);size+=len(chunk)
            if h.hexdigest()!=SOURCE_SHA or size!=17173888:
                raise RuntimeError('Original remote GLB differs; no spend')
            return url
    raise RuntimeError('No valid original GLB URL; no spend')

def run(action):
    STATE.mkdir(parents=True,exist_ok=True)
    if action=='prepare-priced':
        if (STATE/'reservation.lock').exists(): raise RuntimeError('Submission already attempted')
        account=balance()
        if float(account['availableCredits'])!=240:
            raise RuntimeError('Gift ledger differs; no spend')
        diagnostic=load('last-http-error.json')
        if diagnostic['response'].get('c')!='PRICING_ITEM_NOT_QUOTABLE':
            raise RuntimeError('Unexpected quote failure')
        body={'glbUrl':original_url()}
        save('official-priced-request.json',{'request':body,'account':account,'at':now(),
            'priceEvidence':{'url':'https://labs.aholo3d.com/pricing','feature':'Mesh Segmentation',
                             'observedPromotionalCredits':30,'observedOriginalCredits':40},
            'reservedCredits':40,'amendment':'GERMAN_RIFLE_AHOLO_PART_SPLIT_V3.md pre-submit amendment'})
        return {'availableGiftCredits':240,'webPromotionalPrice':30,'reservedCredits':40,'sourceSha256':SOURCE_SHA}
    if action=='quote':
        if (STATE/'reservation.lock').exists(): raise RuntimeError('Submission already attempted')
        account=balance();save('balance-before.json',account)
        if float(account['availableCredits'])!=240:
            raise RuntimeError('Gift ledger differs from240; reconcile before spend')
        body={'glbUrl':original_url()}
        plan={'source':1,'uniqueId':account['uniqueId'],'items':{'1':{
            'endpoint':{'method':'POST','path':ENDPOINT},'parameters':{
                'pathParameters':'{}','queryParameters':'{}',
                'body':json.dumps(body,separators=(',',':'))}}}}
        quote=api('POST','/lux3d/v1/pricing/openapi-quotes',plan)
        save('quote.json',{'request':body,'quote':quote,'account':account,'at':now()})
        cost=float(quote['estimatedCreditsTotal'])
        if not 0<=cost<=20 or sum(float(x) for x in quote['details'].values())!=cost:
            raise RuntimeError('Quote exceeds20 or invalid details; no spend')
        return {'availableGiftCredits':account['availableCredits'],'quoteCredits':cost,
                'sourceSha256':SOURCE_SHA,'expiresAt':quote['expiresAt']}
    if action=='submit-priced':
        q=load('official-priced-request.json');account=balance()
        cost=float(q['reservedCredits'])
        if cost!=40: raise RuntimeError('Budget refused')
        if account['uniqueId']!=q['account']['uniqueId'] or float(account['availableCredits'])!=240:
            raise RuntimeError('Account/balance changed')
        if (datetime.now(timezone.utc)-datetime.fromisoformat(q['at'])).total_seconds()>300:
            raise RuntimeError('Price/source verification older than5min; no spend')
        with (STATE/'reservation.lock').open('x') as f:f.write(now())
        state={'submissionAttempted':True,'reservedCredits':cost,'balanceBefore':240,
               'priceEvidence':q['priceEvidence'],'at':now()}
        save('task.json',state)
        task=api('POST',ENDPOINT,q['request'])
        if not str(task).isdigit(): raise RuntimeError('Missing taskID; do not retry')
        state['taskId']=int(task);save('task.json',state)
        account=balance();save('balance-after-submit.json',account)
        if 240-float(account['availableCredits'])>cost:
            raise RuntimeError('Debit exceeds quote; stop')
        return {'taskId':task,'reservedCredits':cost,'balanceAfterSubmit':account['availableCredits']}
    state=load('task.json');task=state['taskId']
    r=api('GET','/lux3d/v1/generate/task/get?taskid='+str(task))
    if int(r.get('taskId',0))!=task or r.get('bizId')!='LUX_3D':
        raise RuntimeError('Task identity mismatch')
    state.update(lastResult=r,lastCheckedAt=now());save('task.json',state)
    result={'taskId':task,'status':r['status'],'outputCount':len(r.get('outputs') or [])}
    if action in ('download','download-recover'):
        if int(r['status'])!=3: raise RuntimeError('Task not complete')
        incoming=STORE/'incoming';incoming.mkdir(exist_ok=True)
        saved=[]
        for i,item in enumerate(r.get('outputs') or []):
            url=item.get('content','');u=parse.urlparse(url);suffix=Path(u.path).suffix.lower()
            if u.scheme!='https' or suffix not in ('.glb','.zip'): continue
            tag='-recovery' if action=='download-recover' else ''
            dest=incoming/('kar98k-parts-v3-'+str(i)+tag+suffix)
            h=hashlib.sha256()
            if action=='download-recover':
                if dest.exists():raise RuntimeError('Preserve existing recovery output')
                # Credentials absent; capture stderr so signed URLs cannot leak.
                r=subprocess.run(['curl.exe','--silent','--show-error','--fail','--location',
                    '--proto','=https','--proto-redir','=https','--connect-timeout','15','--max-time','60',
                    '--output',str(dest),url],capture_output=True,timeout=70)
                save('download-recovery-status.json',{'returncode':r.returncode,'at':now(),
                    'bytes':dest.stat().st_size if dest.exists() else 0})
                if r.returncode:raise RuntimeError('Artifact curl returncode '+str(r.returncode)+'; no resubmission')
                with dest.open('rb') as f:
                    for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
            else:
                with dest.open('xb') as f,request.urlopen(url,timeout=45) as response:
                    for chunk in iter(lambda:response.read(1024*1024),b''):h.update(chunk);f.write(chunk)
            saved.append({'file':str(dest),'bytes':dest.stat().st_size,'sha256':h.hexdigest()})
        if not saved: raise RuntimeError('No supported output')
        account=balance();save('balance-final.json',account)
        spent=240-float(account['availableCredits'])
        state.update(downloaded=saved,balanceAfter=account['availableCredits'],actualDebit=spent)
        save('task.json',state)
        if not 0<=spent<=state['reservedCredits']: raise RuntimeError('Unexpected final debit')
        result.update(downloaded=saved,actualDebit=spent,balanceAfter=account['availableCredits'])
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=('quote','prepare-priced','submit-priced','poll','download','download-recover'))
    a=p.parse_args()
    try:print(json.dumps(run(a.action)))
    except Exception as exc:
        detail=str(exc) if isinstance(exc,RuntimeError) else ('HTTP '+str(exc.code) if isinstance(exc,error.HTTPError) else type(exc).__name__)
        print(json.dumps({'failed':True,'action':a.action,'error':detail}));sys.exit(1)
