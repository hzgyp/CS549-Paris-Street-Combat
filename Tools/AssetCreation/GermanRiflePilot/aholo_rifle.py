"""Isolated one-job Aholo prop pilot. No top-up, retries or character state writes."""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib import request, error, parse
import uuid
import math

ROOT = Path(__file__).resolve().parents[3]
STORE = ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-v1'
STATE = STORE/'api-state'
STATE.mkdir(parents=True, exist_ok=True)
BASE = 'https://api.aholo3d.com/global'
LABEL = 'kar98k-base-v1'
KEY_FILE = Path('D:/0.Rutgers/CS549/AHOLO api key.txt')
sys.stdout.reconfigure(encoding='utf-8')

class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError('Authenticated redirect refused')

def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def utc():
    return datetime.now(timezone.utc).isoformat()

def api(method, path, body=None):
    secret=KEY_FILE.read_text(encoding='utf-8-sig').strip()
    req=request.Request(BASE+path, data=json.dumps(body).encode() if body is not None else None,
                        headers={'Authorization':secret,'Content-Type':'application/json'},method=method)
    with request.build_opener(NoRedirect).open(req,timeout=35) as response:
        raw=json.load(response)
    if path=='/asset/v1/token' and 'c' not in raw: return raw
    if str(raw.get('c'))!='0': raise RuntimeError('API business code '+str(raw.get('c')))
    return raw['d']

def balance():
    return api('GET','/lux3d/v1/account/balance?source=1')

def validated_gift(account):
    # Known account: one 300-credit gift, 40 previously consumed, no top-ups.
    # Unexpected account totals are not treated as new spending authority.
    before=STATE/'gift_verification.json'
    if before.exists():
        g=load(before)
        if g['initial_verified_remaining']!=260: raise RuntimeError('Gift verification mismatch')
    else:
        if account['availableCredits']!=260: raise RuntimeError('Gift ledger needs reconciliation')
        save(before, {'initial_verified_remaining':260,'origin':'Prior 300-credit gift minus two verified 20 debits; current live API matches', 'at':utc()})

def upload_status(label):
    dest=STATE/(label+'.json')
    pending=load(STATE/(label+'-pending.json'))
    token=pending['token']
    req=request.Request(token['globalDomain'].rstrip('/')+'/ous/api/v2/upload/status',headers={'ous-token-v2':token['ousToken']})
    with request.build_opener(NoRedirect).open(req,timeout=35) as response: result=json.load(response)
    if 'c' in result and str(result['c'])!='0': raise RuntimeError('Upload status rejected')
    data=result.get('d',result)
    if int(data['status'])==5:
        if parse.urlparse(data['url']).scheme!='https': raise RuntimeError('Invalid input URL')
        save(dest,{'inputFile':pending['inputFile'],'inputSha256':pending['sha256'],'inputUrl':data['url'],'at':utc()})
    return {'uploaded':label,'status':data['status'],'sha256':pending['sha256']}

def upload(label, path):
    dest=STATE/(label+'.json')
    if dest.exists(): raise RuntimeError('Occupied upload identity; preserve/reuse')
    path=path.resolve()
    if not path.is_relative_to((STORE/'references').resolve()) or path.suffix.lower() not in ('.jpg','.png'):
        raise RuntimeError('Upload restricted to reviewed CC0 reference images')
    token=api('GET','/asset/v1/token')
    base=token['globalDomain'].rstrip('/')
    if parse.urlparse(base).scheme!='https': raise RuntimeError('Non-HTTPS upload refused')
    md5=hashlib.md5(path.read_bytes()).hexdigest()
    pending=STATE/(label+'-pending.json')
    if pending.exists(): raise RuntimeError('Pending upload preserved; query status rather than repeat')
    # Official asset_uploader.py block protocol; preserve token locally for status-only recovery.
    save(pending,{'token':token,'inputFile':str(path),'sha256':digest(path),'at':utc()})
    def post(endpoint,fields,content=None,name=None):
        if content is None:
            body=parse.urlencode(fields).encode();ctype='application/x-www-form-urlencoded'
        else:
            boundary='----rifle'+uuid.uuid4().hex
            body=b''.join((f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n').encode() for k,v in fields.items())
            body+=(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{name}"\r\nContent-Type: application/octet-stream\r\n\r\n').encode()+content+f'\r\n--{boundary}--\r\n'.encode()
            ctype='multipart/form-data; boundary='+boundary
        req=request.Request(base+endpoint,data=body,method='POST',headers={'ous-token-v2':token['ousToken'],'Content-Type':ctype})
        with request.build_opener(NoRedirect).open(req,timeout=40) as response: result=json.load(response)
        if 'c' in result and str(result['c'])!='0': raise RuntimeError('Upload rejected')
        return result.get('d',result)
    if path.stat().st_size<=int(token['blockSize']):
        post('/ous/api/v2/single/upload',{'md5':md5},path.read_bytes(),path.name)
    else:
        blocks=math.ceil(path.stat().st_size/int(token['blockSize']))
        init=post('/ous/api/v2/block/upload/init',{'md5':md5,'blocks':blocks,'size':path.stat().st_size,'name':path.name})
        if not init.get('deduplicated'):
            lack=init.get('lackBlocks')
            missing=set()
            for part in (lack if isinstance(lack,list) else str(lack).split(',')) if lack else range(1,blocks+1):
                nums=str(part).split('-');first=int(nums[0]);last=int(nums[-1])
                if not 1<=first<=last<=blocks: raise RuntimeError('Invalid upload block range')
                missing.update(range(first,last+1))
            with path.open('rb') as f:
                for n in sorted(missing):
                    f.seek((n-1)*int(token['blockSize']))
                    post('/ous/api/v2/block/upload/part',{'block':n},f.read(int(token['blockSize'])),path.name+'.part-'+str(n))
                    print(json.dumps({'upload':label,'block':n,'totalBlocks':blocks}),flush=True)
    return upload_status(label)

parser=argparse.ArgumentParser()
parser.add_argument('action',choices=('balance','upload','upload-status','quote','submit','poll','download'))
parser.add_argument('--input')
parser.add_argument('--label',default='ref-side')
parser.add_argument('--reference-labels',nargs='+',default=['ref-side','ref-opposite'])
args=parser.parse_args()
state_path=STATE/(LABEL+'.json')
state=load(state_path) if state_path.exists() else {'label':LABEL}
try:
    if args.action=='balance':
        account=balance(); save(STATE/'latest-balance.json',account);validated_gift(account)
        result={'availableCredits':account['availableCredits'],'snapshotAt':account['snapshotAt'],'gift_reconciled':True}
    elif args.action=='upload':
        if not args.label.replace('-','').isalnum(): raise RuntimeError('Invalid identity')
        result=upload(args.label,Path(args.input))
    elif args.action=='upload-status':
        if not args.label.replace('-','').isalnum(): raise RuntimeError('Invalid identity')
        result=upload_status(args.label)
    elif args.action=='quote':
        if state.get('submissionAttempted'): raise RuntimeError('Submission already attempted')
        account=balance(); validated_gift(account)
        inputs=[load(STATE/(x+'.json'))['inputUrl'] for x in args.reference_labels]
        # Current official G1 contract always delivers PBR; enablePbr is forbidden.
        body={'version':'G1','faceCount':300000,'outputFormat':['glb'],'aiPredictSize':False}
        body['img' if len(inputs)==1 else 'imgs']=inputs[0] if len(inputs)==1 else inputs
        plan={'source':1,'uniqueId':account['uniqueId'],'items':{'1':{'endpoint':{'method':'POST','path':'/lux3d/v1/generate/img-to-3d/task/create'},'parameters':{'pathParameters':'{}','queryParameters':'{}','body':json.dumps(body,separators=(',',':'))}}}}
        quote=api('POST','/lux3d/v1/pricing/openapi-quotes',plan)
        cost=quote['estimatedCreditsTotal']
        if not 0<float(cost)<=20 or sum(float(x) for x in quote['details'].values())!=float(cost):
            raise RuntimeError('Quote outside 20-credit cap or invalid details')
        state.update(request=body,quote=quote,accountAtQuote=account);save(state_path,state)
        result={'quoteCredits':cost,'availableCredits':account['availableCredits'],'expiresAt':quote['expiresAt']}
    elif args.action=='submit':
        if state.get('submissionAttempted'): raise RuntimeError('Never repeat an attempted submission')
        quote=state['quote'];account=balance();validated_gift(account)
        if datetime.fromisoformat(quote['expiresAt'].replace('Z','+00:00'))<=datetime.now(timezone.utc): raise RuntimeError('Quote expired')
        if quote['uniqueId']!=account['uniqueId'] or account['availableCredits']!=260: raise RuntimeError('Account/budget changed; stop')
        cost=float(quote['estimatedCreditsTotal'])
        if not 0<cost<=20: raise RuntimeError('Budget refused')
        with (STATE/(LABEL+'-reservation.lock')).open('x') as lock: lock.write(utc())
        state.update(submissionAttempted=True,reservedCredits=cost,balanceBefore=account['availableCredits'],attemptedAt=utc())
        save(state_path,state) # reserve before external mutation; never automatically retry
        task=api('POST','/lux3d/v1/generate/img-to-3d/task/create',state['request'])
        if not str(task).isdigit(): raise RuntimeError('Missing task ID; reservation retained')
        state['taskId']=task;save(state_path,state)
        result={'taskId':task,'reservedCredits':cost,'balanceAfterSubmit':balance()['availableCredits']}
    elif args.action in ('poll','download'):
        task=state['taskId']; reply=api('GET','/lux3d/v1/generate/task/get?taskid='+str(task))
        if str(reply.get('taskId'))!=str(task) or reply.get('bizId')!='LUX_3D': raise RuntimeError('Task ownership/identity response mismatch')
        state.update(lastResult=reply,lastCheckedAt=utc());save(state_path,state)
        result={'taskId':task,'status':reply['status'],'outputCount':len(reply.get('outputs',[]))}
        if args.action=='download':
            if int(reply['status'])!=3: raise RuntimeError('Task not successfully completed')
            saved=[]
            for item in reply.get('outputs',[]):
                uri=item.get('content','');parsed=parse.urlparse(uri)
                suffix=Path(parsed.path).suffix.lower()
                if parsed.scheme!='https' or suffix not in ('.glb','.zip'): continue
                dest=STORE/'incoming'/(LABEL+suffix)
                if dest.exists(): raise RuntimeError('Preserve occupied output')
                # Artifact requests carry no API credential.
                with request.urlopen(uri,timeout=45) as src, dest.open('xb') as f:
                    for chunk in iter(lambda:src.read(1024*1024),b''): f.write(chunk)
                saved.append({'file':str(dest),'bytes':dest.stat().st_size,'sha256':digest(dest)})
            if not saved: raise RuntimeError('No GLB/ZIP output found')
            account=balance();state.update(downloaded=saved,balanceAfter=account['availableCredits']);save(state_path,state)
            if state['balanceBefore']-account['availableCredits']>state['reservedCredits']: raise RuntimeError('Debit exceeds reservation')
            result.update(downloaded=saved,balanceAfter=account['availableCredits'])
    print(json.dumps(result,ensure_ascii=True))
except Exception as exc:
    # Do not expose request URLs, headers, credentials, account contexts or raw API messages.
    detail = str(exc) if isinstance(exc,RuntimeError) else ('HTTP '+str(exc.code) if isinstance(exc,error.HTTPError) else type(exc).__name__)
    print(json.dumps({'failed':True,'action':args.action,'error':detail}))
    sys.exit(1)
