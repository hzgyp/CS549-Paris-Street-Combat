from __future__ import annotations

import base64
import io
import json
import os
import secrets
import threading
import time
import uuid
import wave
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import BaseModel, ConfigDict, Field
from PIL import Image

from .catalog import now, refresh
from .security import WorkbenchError, read_file, sha
from .store import Store
from .models import validate_glb, MAX_MODEL_BYTES
from .animations import AnimationLibrary
from .network import external_origin

Image.MAX_IMAGE_PIXELS = 100_000_000
ROOT = Path(__file__).resolve().parents[3]
WORKBENCH = Path(__file__).resolve().parents[1]


class SessionInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    token: str = Field(min_length=20, max_length=200)


class JobInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    kind: Literal['refresh_metadata', 'verify_local']
    bundle_id: str | None = None
    max_bytes: int = Field(default=1024**3, gt=0, le=8*1024**3)


class Envelope(BaseModel):
    snapshot_id: str
    generated_at: str
    data: Any


def create_app(root: Path = ROOT, state_dir: Path | None = None, token: str | None = None, port=8765, allowed_hosts: list[str] | None = None, shared=False, external_url: str | None = None):
    public_origin=external_origin(external_url,shared)
    root = root.resolve()
    state_dir = state_dir or root/'Assets/LocalWorking/AssetWorkbench'
    store = Store(state_dir/'cache/index.sqlite3')
    app = FastAPI(title='Paris Asset Workbench', docs_url=None, redoc_url=None, openapi_url=None)
    app.state.store, app.state.root = store, root
    app.state.bootstrap = token or secrets.token_urlsafe(32)
    app.state.sessions = {}
    app.state.port = port
    app.state.pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='asset-index')
    app.state.jobs_lock = threading.Lock()
    app.state.cancel = {}
    app.state.idempotency = {}
    animations=AnimationLibrary(root,state_dir)
    app.state.animations=animations
    authorities={f'{h.lower()}:{port}' for h in (allowed_hosts or ['127.0.0.1','localhost'])}
    loopback_authorities={f'127.0.0.1:{port}',f'localhost:{port}'}
    if public_origin:
        authorities.add(public_origin.removeprefix('http://'))

    @app.exception_handler(WorkbenchError)
    async def known_error(request, e):
        return JSONResponse({'code':e.code,'message':e.message,'retryable':e.code in ('INDEX_BUSY','SOURCE_CHANGED_DURING_SCAN')},status_code=e.status)

    @app.middleware('http')
    async def local_boundary(request: Request, call_next):
        host=request.headers.get('host','').lower()
        if host not in authorities:
            return JSONResponse({'code':'HOST_DENIED','message':'访问地址未登记'},status_code=403)
        origin=f'{request.url.scheme}://{host}'
        if request.url.path.startswith('/api/'):
            req_origin=request.headers.get('origin')
            if req_origin and req_origin!=origin:
                return JSONResponse({'code':'ORIGIN_DENIED','message':'来源不匹配'},status_code=403)
            session=app.state.sessions.get(request.cookies.get('aw_session',''))
            if request.url.path!='/api/v1/session':
                if not session or session['expires']<time.time():
                    return JSONResponse({'code':'SESSION_REQUIRED','message':'请使用带访问凭证的启动或共享链接'},status_code=401)
                if request.method not in ('GET','HEAD') and (req_origin!=origin or request.headers.get('x-csrf-token')!=session['csrf']):
                    return JSONResponse({'code':'CSRF_DENIED','message':'会话校验失败'},status_code=403)
            elif request.method=='POST' and req_origin!=origin:
                return JSONResponse({'code':'ORIGIN_DENIED','message':'会话必须由同源页面建立'},status_code=403)
        response=await call_next(request)
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['Referrer-Policy']='no-referrer'
        response.headers['Cache-Control']='no-store'
        response.headers['Content-Security-Policy']="default-src 'self'; img-src 'self' blob:; media-src 'self' blob:; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self' blob:; frame-ancestors 'none'"
        return response

    def sid(value):return store.active(value)
    def wrap(snapshot,data):return Envelope(snapshot_id=snapshot,generated_at=now(),data=data)

    def token_free_local(request:Request):
        # Local development opens directly; shared/network access still checks its token.
        return not shared and request.headers.get('host','').lower() in loopback_authorities

    def new_session():
        session_id,csrf=secrets.token_urlsafe(32),secrets.token_urlsafe(24)
        app.state.sessions[session_id]={'csrf':csrf,'expires':time.time()+24*3600}
        response=JSONResponse({'csrf':csrf})
        response.set_cookie('aw_session',session_id,httponly=True,samesite='strict',max_age=24*3600,path='/')
        return response

    @app.post('/api/v1/session')
    def login(payload: SessionInput, request:Request):
        if not token_free_local(request) and not secrets.compare_digest(payload.token,app.state.bootstrap):
            raise WorkbenchError('SESSION_REQUIRED','访问凭证无效',401)
        return new_session()

    @app.get('/api/v1/session')
    def session_status(request:Request):
        session=app.state.sessions.get(request.cookies.get('aw_session',''))
        if not session or session['expires']<time.time():
            if token_free_local(request):return new_session()
            raise WorkbenchError('SESSION_REQUIRED','会话已失效',401)
        return {'csrf':session['csrf']}

    @app.get('/api/v1/health')
    def health():
        try:active=store.active()
        except WorkbenchError:active=None
        return {'version':'1.0.0','mode':'shared_read_only' if shared else 'local_read_only','snapshot_id':active,'jobs':store.jobs()}

    @app.get('/api/v1/overview',response_model=Envelope)
    def overview(snapshot_id:str|None=None):
        s=sid(snapshot_id); info=store.info(s)
        homepage=store.list(s,'homepage')
        return wrap(s,{'stats':info['stats'],'created':info['created'],'digest':info['digest'],'elapsed_ms':info['elapsed_ms'],'git_head':info['git_head'],'builds':store.list(s,'builds'),'issues':store.list(s,'issues'),'homepage':homepage[0] if homepage else None})

    def page_rows(s,rows,cursor,limit,query_key):
        offset=0
        if cursor:
            try:
                c=json.loads(base64.urlsafe_b64decode(cursor.encode()))
                if c['snapshot']!=s or c['query']!=query_key:raise ValueError()
                offset=int(c['offset'])
                if offset<0:raise ValueError()
            except Exception:raise WorkbenchError('INVALID_CURSOR','分页游标与当前查询或快照不匹配',422)
        if not 1<=limit<=200:raise WorkbenchError('INVALID_LIMIT','每页须为1至200条',422)
        next_cursor=base64.urlsafe_b64encode(json.dumps({'snapshot':s,'query':query_key,'offset':offset+limit}).encode()).decode() if offset+limit<len(rows) else None
        return {'items':rows[offset:offset+limit],'total':len(rows),'next_cursor':next_cursor}

    @app.get('/api/v1/asset-options',response_model=Envelope)
    def asset_options(snapshot_id:str|None=None):
        s=sid(snapshot_id)
        return wrap(s,{'items':[{k:a.get(k) for k in ('id','name','name_en','owner')} for a in store.list(s,'assets')]})

    @app.get('/api/v1/assets',response_model=Envelope)
    def assets(q:str='',category:str='',origin:str='',lifecycle:str='',rights:str='',availability:str='',usage:str='',owner:str='',parent:str='',cursor:str|None=None,limit:int=50,snapshot_id:str|None=None):
        s=sid(snapshot_id); rows=store.list(s,'assets')
        filters=dict(category=category,origin=origin,lifecycle=lifecycle,rights=rights,availability=availability,owner=owner)
        for field,value in filters.items():
            if value:rows=[a for a in rows if a.get(field)==value]
        if usage:rows=[a for a in rows if (a.get('usage_status')==usage if usage in ('source_only','unregistered') else usage in a['build_ids'])]
        if parent:rows=[a for a in rows if a.get('parent_id')==parent or (parent=='root' and not a.get('parent_id'))]
        if q:rows=[a for a in rows if q.casefold() in ' '.join([a['name'],a['name_en'],a['id'],*a.get('aliases',[]),*[m['name'] for m in a.get('members',[])]]).casefold()]
        rows=[{k:v for k,v in a.items() if k!='members'} for a in rows]
        return wrap(s,page_rows(s,rows,cursor,limit,sha(json.dumps([q,filters,usage,parent],sort_keys=True).encode())))

    @app.get('/api/v1/assets/{asset_id}/members',response_model=Envelope)
    def asset_members(asset_id:str,q:str='',cursor:str|None=None,limit:int=50,snapshot_id:str|None=None):
        s=sid(snapshot_id);a=store.get(s,'assets',asset_id)
        rows=[m for m in a.get('members',[]) if q.casefold() in (m['name']+' '+m['path']).casefold()]
        return wrap(s,page_rows(s,rows,cursor,limit,sha((asset_id+q).encode())))

    @app.get('/api/v1/assets/{asset_id}',response_model=Envelope)
    def asset_detail(asset_id:str,snapshot_id:str|None=None):
        s=sid(snapshot_id); a=store.get(s,'assets',asset_id)
        a.pop('members',None)
        a['evidence']=[e for e in store.list(s,'evidence') if asset_id in e.get('asset_ids',[])]
        a['usage']=[u for u in store.list(s,'usage') if u['asset_id']==asset_id]
        builds={b['id']:b for b in store.list(s,'builds')}
        for usage in a['usage']:
            build=builds.get(usage['build_id'],{})
            usage.update(build_title=build.get('title',usage['build_id']),build_revision=build.get('revision'),game_sha256=build.get('game_sha256'))
        a['media']=[{k:v for k,v in m.items() if k not in ('path','rights_basis')} for m in store.list(s,'media') if m['id'] in a['media_ids']]
        a['bundle_details']=[b for b in store.list(s,'bundles') if b['id'] in a.get('bundles',[])]
        a['gameplay']=[{k:g[k] for k in ('id','title','kind','design_state','implementation','validation')} for g in store.list(s,'gameplay') if asset_id in g['asset_ids']]
        from .research_links import references_for
        a['historical_references']=references_for(store.list(s,'research'),'asset',asset_id)
        return wrap(s,a)

    @app.get('/api/v1/assets/{asset_id}/revisions',response_model=Envelope)
    def revisions(asset_id:str,snapshot_id:str|None=None):
        s=sid(snapshot_id); store.get(s,'assets',asset_id)
        return wrap(s,[x for x in store.list(s,'revisions') if x['asset_id']==asset_id])

    @app.get('/api/v1/comparisons',response_model=Envelope)
    def compare(left:str,right:str,snapshot_id:str|None=None):
        s=sid(snapshot_id); l=store.get(s,'revisions',left); r=store.get(s,'revisions',right)
        if l['asset_id']!=r['asset_id']:raise WorkbenchError('REVISION_MISMATCH','请选择同一资产的两个修订',422)
        def inventory(rev):
            return {f['path']:f for f in store.files(s,rev['file_bundle'],limit=100000)[0]} if rev.get('file_bundle') else {}
        lf,rf=inventory(l),inventory(r)
        changes=[dict(path=p,change='added' if p not in lf else 'removed' if p not in rf else 'changed') for p in sorted(lf.keys()|rf.keys()) if p not in lf or p not in rf or lf[p]['sha256']!=rf[p]['sha256']]
        same_model=bool(l.get('model_identity') and l.get('model_identity')==r.get('model_identity'))
        return wrap(s,{'left':l,'right':r,'same_model':same_model,'changes':changes[:1000],'change_count':len(changes),'comparison_scope':'整合证据与登记模型身份' if same_model else '登记文件与文档范围；未登记文件集合不做字节差异推断','matched_camera':False})

    @app.get('/api/v1/builds',response_model=Envelope)
    def builds(snapshot_id:str|None=None):
        s=sid(snapshot_id); return wrap(s,store.list(s,'builds'))

    @app.get('/api/v1/builds/{build_id}/usage',response_model=Envelope)
    def usage(build_id:str,snapshot_id:str|None=None):
        s=sid(snapshot_id); b=store.get(s,'builds',build_id)
        return wrap(s,{'build':b,'edges':[u for u in store.list(s,'usage') if u['build_id']==build_id],'assets':[{k:v for k,v in a.items() if k!='members'} for a in store.list(s,'assets') if build_id in a['build_ids']],'bundles':store.list(s,'bundles'),'recovery':[{k:v for k,v in r.items() if k!='files'} for r in store.list(s,'recovery')]})

    @app.get('/api/v1/bundles',response_model=Envelope)
    def bundles(snapshot_id:str|None=None):
        s=sid(snapshot_id);return wrap(s,store.list(s,'bundles'))

    @app.get('/api/v1/files',response_model=Envelope)
    def files(bundle:str|None=None,q:str='',offset:int=0,limit:int=50,snapshot_id:str|None=None):
        if offset<0 or not 1<=limit<=200:raise WorkbenchError('INVALID_LIMIT','文件分页范围错误',422)
        s=sid(snapshot_id); rows,total=store.files(s,bundle,q,offset,limit)
        return wrap(s,{'items':rows,'total':total,'offset':offset,'limit':limit})

    @app.get('/api/v1/evidence/{evidence_id}',response_model=Envelope)
    def evidence(evidence_id:str,snapshot_id:str|None=None):
        s=sid(snapshot_id);return wrap(s,store.get(s,'evidence',evidence_id))

    @app.get('/api/v1/sources/{source_id}/excerpt',response_model=Envelope)
    def excerpt(source_id:str,snapshot_id:str|None=None):
        s=sid(snapshot_id);return wrap(s,store.get(s,'sources',source_id))

    @app.get('/api/v1/templates',response_model=Envelope)
    def templates(snapshot_id:str|None=None):
        s=sid(snapshot_id);return wrap(s,store.list(s,'templates'))

    @app.get('/api/v1/gameplay',response_model=Envelope)
    def gameplay(q:str='',kind:str='',implementation:str='',snapshot_id:str|None=None):
        s=sid(snapshot_id);rows=store.list(s,'gameplay')
        if kind:rows=[g for g in rows if g['kind']==kind]
        if implementation:rows=[g for g in rows if g['implementation']['state']==implementation]
        if q:rows=[g for g in rows if q.casefold() in json.dumps({k:g.get(k) for k in ('id','title','summary','rules','steps','asset_ids','locations')},ensure_ascii=False).casefold()]
        return wrap(s,{'items':rows,'total':len(rows)})

    @app.get('/api/v1/research',response_model=Envelope)
    def research(q:str='',scope:str='',kind:str='',snapshot_id:str|None=None):
        s=sid(snapshot_id);rows=store.list(s,'research')
        if scope:rows=[r for r in rows if r['scope']==scope]
        if kind:rows=[r for r in rows if r['kind']==kind]
        if q:rows=[r for r in rows if q.casefold() in r['search_text']]
        return wrap(s,{'items':[{k:v for k,v in r.items() if k not in ('body','search_text')} for r in rows],'total':len(rows)})

    @app.get('/api/v1/research/{entry_id}',response_model=Envelope)
    def research_detail(entry_id:str,snapshot_id:str|None=None):
        s=sid(snapshot_id);r=store.get(s,'research',entry_id)
        r.pop('search_text',None)
        r['assets']=[{k:a.get(k) for k in ('id','name','name_en')} for a in store.list(s,'assets') if a['id'] in r['asset_ids']]
        r['gameplay']=[{k:g.get(k) for k in ('id','title')} for g in store.list(s,'gameplay') if g['id'] in r.get('gameplay_ids',[])]
        return wrap(s,r)

    @app.get('/api/v1/gameplay/{entry_id}',response_model=Envelope)
    def gameplay_detail(entry_id:str,snapshot_id:str|None=None):
        s=sid(snapshot_id);g=store.get(s,'gameplay',entry_id)
        g['assets']=[{k:a.get(k) for k in ('id','name','name_en','preview_id','category')} for a in store.list(s,'assets') if a['id'] in g['asset_ids']]
        from .research_links import references_for
        g['historical_references']=references_for(store.list(s,'research'),'gameplay',entry_id)
        return wrap(s,g)

    @app.get('/api/v1/templates/{template_id}',response_model=Envelope)
    def template(template_id:str,snapshot_id:str|None=None):
        s=sid(snapshot_id);return wrap(s,store.get(s,'templates',template_id))

    @app.get('/api/v1/issues',response_model=Envelope)
    def issues(severity:str='',q:str='',snapshot_id:str|None=None):
        s=sid(snapshot_id); rows=store.list(s,'issues')
        if severity:rows=[x for x in rows if x['severity']==severity]
        if q:rows=[x for x in rows if q.casefold() in json.dumps(x,ensure_ascii=False).casefold()]
        return wrap(s,rows)

    @app.get('/api/v1/models/{model_id}/file')
    def model_file(model_id:str,snapshot_id:str|None=None):
        s=sid(snapshot_id);m=store.get(s,'models',model_id)
        if m.get('audience')!='local_owner':raise WorkbenchError('RIGHTS_NOT_ESTABLISHED','该预览尚未登记本机受众许可',403)
        try:raw=read_file(root,m['path'],MAX_MODEL_BYTES)
        except OSError:raise WorkbenchError('MODEL_UNAVAILABLE','3D预览文件不可访问',404)
        if sha(raw)!=m['sha256']:raise WorkbenchError('MODEL_CHANGED','3D预览与登记版本不一致',409)
        validate_glb(raw)
        return Response(raw,media_type='model/gltf-binary',headers={'ETag':f'"{m["sha256"]}"'})

    @app.get('/api/v1/animation-packs/{pack_id}')
    def animation_directory(pack_id:str):
        return animations.directory(pack_id)

    @app.get('/api/v1/animation-packs/{pack_id}/clips/{clip_id}')
    def animation_status(pack_id:str,clip_id:str):
        return animations.status(pack_id,clip_id)

    @app.post('/api/v1/animation-packs/{pack_id}/clips/{clip_id}/prepare')
    def animation_prepare(pack_id:str,clip_id:str,retry:bool=False):
        return animations.prepare(pack_id,clip_id,retry)

    @app.get('/api/v1/animation-packs/{pack_id}/clips/{clip_id}/file')
    def animation_file(pack_id:str,clip_id:str):
        raw,digest=animations.file(pack_id,clip_id)
        return Response(raw,media_type='model/gltf-binary',headers={'ETag':f'"{digest}"'})

    @app.get('/api/v1/media/{media_id}')
    def media(media_id:str,request:Request,snapshot_id:str|None=None,original:bool=False):
        s=sid(snapshot_id); m=store.get(s,'media',media_id)
        if m.get('kind')=='supplier thumbnail':raise WorkbenchError('MEDIA_RETIRED','供应商宣传图已从平台移除',410)
        if m.get('audience')!='local_owner':raise WorkbenchError('RIGHTS_NOT_ESTABLISHED','该预览尚未登记本机受众许可',403)
        try:raw=read_file(root,m['path'],100*1024**2 if m['mime']=='audio/wav' else 50*1024**2)
        except OSError:raise WorkbenchError('MEDIA_UNAVAILABLE','预览原件不存在或不可访问',404)
        if sha(raw)!=m['sha256']:raise WorkbenchError('MEDIA_CHANGED','预览字节与登记版本不同',409)
        if m['mime']=='audio/wav':
            try:
                with wave.open(io.BytesIO(raw)) as w:
                    if not 1<=w.getnchannels()<=8:raise ValueError()
            except (wave.Error,ValueError):raise WorkbenchError('MIME_MISMATCH','不是有效WAV音频',422)
        elif m['mime'] in ('image/png','image/jpeg','image/webp'):
            try:
                with Image.open(io.BytesIO(raw)) as im:
                    if Image.MIME.get(im.format)!=m['mime'] or im.width*im.height>100_000_000:raise ValueError()
                    im.verify()
            except Exception:raise WorkbenchError('MIME_MISMATCH','图像签名或解码限制不通过',422)
        else:raise WorkbenchError('MIME_MISMATCH','不支持的媒体格式',403)
        if m.get('kind')=='historical reference' and not original:
            with Image.open(io.BytesIO(raw)) as im:
                im.thumbnail((1600,1600))
                output=io.BytesIO();im.convert('RGB').save(output,'JPEG',quality=85)
            return Response(output.getvalue(),media_type='image/jpeg',headers={'ETag':f'"{m["sha256"]}-1600"'})
        headers={'Accept-Ranges':'bytes','ETag':f'"{m["sha256"]}"'}
        range_value=request.headers.get('range')
        if range_value:
            try:
                if not range_value.startswith('bytes=') or ',' in range_value:raise ValueError()
                a,b=range_value[6:].split('-')
                start=int(a) if a else max(0,len(raw)-int(b)); end=min(int(b),len(raw)-1) if a and b else len(raw)-1
                if not 0<=start<=end<len(raw):raise ValueError()
            except ValueError:return Response(status_code=416,headers={'Content-Range':f'bytes */{len(raw)}'})
            headers['Content-Range']=f'bytes {start}-{end}/{len(raw)}'
            return Response(raw[start:end+1],media_type=m['mime'],status_code=206,headers=headers)
        return Response(raw,media_type=m['mime'],headers=headers)

    def work(job,payload,cancel):
        job['status']='running'; store.job(job)
        try:
            if payload.kind=='refresh_metadata':
                result=refresh(root,store,cancel.is_set)
                job.update(snapshot_id=result['id'],coverage=result['stats'],navigation_index=result['navigation_index'],status='degraded' if any(i['severity']=='error' for i in store.list(result['id'],'issues')) else 'succeeded')
            else:
                s=job['snapshot_id']; rows,_=store.files(s,payload.bundle_id,limit=100000)
                checked,bytes_read,failures=0,0,[]
                for f in rows:
                    if cancel.is_set():raise WorkbenchError('CANCELLED','任务已取消')
                    try:
                        raw=read_file(root,f['path'],payload.max_bytes-bytes_read)
                        bytes_read+=len(raw)
                        if len(raw)!=f['size_bytes'] or sha(raw)!=f['sha256']:failures.append({'path':f['path'],'reason':'hash_or_size_mismatch'})
                        else:checked+=1
                    except (OSError,WorkbenchError) as e:failures.append({'path':f['path'],'reason':e.code if isinstance(e,WorkbenchError) else 'unavailable'})
                job.update(status='succeeded' if not failures else 'degraded',coverage={'checked_files':checked,'total_files':len(rows),'bytes_read':bytes_read},failures=failures,verification_scope='本机文件；不是远端发布核验')
        except Exception as e:
            job.update(status='cancelled' if isinstance(e,WorkbenchError) and e.code=='CANCELLED' else 'failed',error=e.message if isinstance(e,WorkbenchError) else '索引任务失败，请查看本机诊断',code=e.code if isinstance(e,WorkbenchError) else 'INTERNAL_ERROR')
            (state_dir/'runs').mkdir(parents=True,exist_ok=True)
            (state_dir/'runs'/f'{job["id"]}-error.txt').write_text(repr(e),encoding='utf-8')
        finally:
            job['finished']=now();store.job(job)

    @app.post('/api/v1/index/jobs')
    def start_job(payload:JobInput,request:Request):
        key=request.headers.get('idempotency-key','')
        if not key or len(key)>200:raise WorkbenchError('INVALID_IDEMPOTENCY_KEY','任务需要幂等键',422)
        with app.state.jobs_lock:
            if key in app.state.idempotency:
                old=app.state.idempotency[key]
                if old['payload']!=payload.model_dump():raise WorkbenchError('IDEMPOTENCY_CONFLICT','幂等键已用于不同任务',409)
                return next(x for x in store.jobs() if x['id']==old['id'])
            if any(j['status'] in ('queued','running') for j in store.jobs()):raise WorkbenchError('INDEX_BUSY','已有索引任务，请等待或取消',409)
            job=dict(id=uuid.uuid4().hex,kind=payload.kind,status='queued',created=now())
            if payload.kind=='verify_local':
                if not payload.bundle_id:raise WorkbenchError('BUNDLE_REQUIRED','必须选择一个登记文件组',422)
                s=store.active();rows,total=store.files(s,payload.bundle_id,limit=100000)
                if not total:raise WorkbenchError('NOT_FOUND','登记文件组不存在',404)
                size=sum(f['size_bytes'] for f in rows)
                if size>payload.max_bytes:raise WorkbenchError('VERIFICATION_LIMIT',f'登记文件约{size:,}字节，超过本次{payload.max_bytes:,}字节限额，尚未启动',422)
                job['snapshot_id']=s
            cancel=threading.Event();app.state.cancel[job['id']]=cancel
            store.job(job);app.state.idempotency[key]={'id':job['id'],'payload':payload.model_dump()}
            app.state.pool.submit(work,job.copy(),payload,cancel)
            return job

    @app.get('/api/v1/index/jobs/{job_id}')
    def get_job(job_id:str):
        result=next((j for j in store.jobs() if j['id']==job_id),None)
        if not result:raise WorkbenchError('NOT_FOUND','任务不存在',404)
        return result

    @app.post('/api/v1/index/jobs/{job_id}/cancel')
    def cancel_job(job_id:str):
        if job_id not in app.state.cancel:raise WorkbenchError('NOT_FOUND','任务不在当前进程中',404)
        app.state.cancel[job_id].set()
        return {'id':job_id,'cancellation_requested':True}

    @app.get('/{path:path}')
    def frontend(path:str):
        if path.startswith('api/'):
            raise WorkbenchError('NOT_FOUND','接口不存在',404)
        dist=WORKBENCH/'frontend/dist'
        if path.startswith('assets/') and Path(path).suffix:
            from .security import safe_path
            candidate=safe_path(dist,path)
            if not candidate.is_file():raise WorkbenchError('NOT_FOUND','静态文件不存在',404)
            return FileResponse(candidate)
        if not (dist/'index.html').is_file():return Response('Frontend build is not ready.',status_code=503)
        return FileResponse(dist/'index.html')

    return app
