"""Use the platform's authenticated Refresh index operation, never print its token."""
from pathlib import Path
import json,urllib.request,http.cookiejar,uuid,time
root=Path(__file__).resolve().parents[3]
session=json.loads((root/'Assets/LocalWorking/AssetWorkbench/runtime/session.json').read_text('utf-8'))
origin=f"http://127.0.0.1:{session['port']}"
client=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
def call(path,data=None,headers=None):
    raw=json.dumps(data).encode() if data is not None else None
    req=urllib.request.Request(origin+path,data=raw,headers=dict({'Origin':origin,'Content-Type':'application/json'},**(headers or {})))
    with client.open(req,timeout=30) as response:return json.load(response)
csrf=call('/api/v1/session',dict(token=session['token']))['csrf']
job=call('/api/v1/index/jobs',dict(kind='refresh_metadata'),{'x-csrf-token':csrf,'idempotency-key':str(uuid.uuid4())})
out=root/'tmp/g1-grenade-equip-20261011/INDEX_REFRESH.json'
for _ in range(20):
    job=call('/api/v1/index/jobs/'+job['id'])
    out.write_text(json.dumps(job,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    if job['status'] not in ['queued','running']:break
    time.sleep(2)
assert job['status']=='succeeded',job.get('status')
print('PLATFORM REFRESH',job['status'],job.get('snapshot_id'))
