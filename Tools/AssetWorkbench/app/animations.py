"""Local, bounded, serialized animation preparation. Never accepts shell/file input from HTTP."""
import hashlib,json,os,re,subprocess,threading,time,uuid
from pathlib import Path
from .security import WorkbenchError,safe_path,read_file,sha
from .models import validate_glb,MAX_MODEL_BYTES

class AnimationLibrary:
 def __init__(self,root,state):
  self.root=root;self.state=state;self.base=state/'animation-viewer-v1';self.lock=threading.Lock();self.active=None;self.catalog=None;self.catalog_stamp=None
 def pack(self,pid):
  path=self.state/'private-records/animation-packs.json'
  if not path.is_file():raise WorkbenchError('NOT_FOUND','动画目录尚未登记',404)
  stat=path.stat();stamp=(stat.st_mtime_ns,stat.st_size)
  if self.catalog_stamp!=stamp:
   self.catalog=json.loads(path.read_text(encoding='utf8'));self.catalog_stamp=stamp
  p=self.catalog['packs'].get(pid)
  if not p:raise WorkbenchError('NOT_FOUND','动画包不存在',404)
  return p
 def clip(self,pid,cid):
  if not re.fullmatch(r'[A-Za-z0-9_-]{1,80}',cid):raise WorkbenchError('NOT_FOUND','动作不存在',404)
  pack=self.pack(pid);clip=next((c for c in pack['clips'] if c['id']==cid),None)
  if not clip:raise WorkbenchError('NOT_FOUND','动作不存在',404)
  return pack,clip
 def directory(self,pid):
  p=self.pack(pid)
  return {'id':pid,'default_clip':p['default_clip'],'external_mannequin':p['external_mannequin'],'clips':[{k:c[k] for k in ('id','name','path')} for c in p['clips']]}
 def receipt(self,cid):
  # cid only reaches this method after exact lookup in the registered directory.
  direct=self.base/'cache'/cid/'glb-result.json'
  pointer=self.base/'cache'/cid/'current.json'
  if pointer.exists():direct=safe_path(self.root,json.loads(pointer.read_text())['receipt'])
  return json.loads(direct.read_text()) if direct.exists() else None
 def status(self,pid,cid):
  p,c=self.clip(pid,cid);r=self.receipt(cid)
  if r and r['status']=='ready' and r.get('source_sha256')!=c['sha256']:
   raise WorkbenchError('SOURCE_CHANGED','预览与当前登记动作不一致',409)
  if r and r['status']=='ready':
   scope='原始动作 · 中性材质'+(' · 外部预览人偶' if p['external_mannequin'] else '')
   return {'status':'ready','clip_id':cid,'model':{'id':'animation-'+cid,'file_url':f'/api/v1/animation-packs/{pid}/clips/{cid}/file','label':c['name'],'label_en':c['name'],'revision':'source animation','scope':scope,'scope_en':'Source animation · Neutral material'+(' · External preview mannequin' if p['external_mannequin'] else ''),'sha256':r['sha256']}}
  with self.lock:
   if self.active and self.active['clip_id']==cid:return dict(self.active)
  if r and r['status']=='failed':return {'status':'failed','clip_id':cid,'code':r.get('code','ANIMATION_PREPARATION_FAILED')}
  return {'status':'uncached','clip_id':cid}
 def file(self,pid,cid):
  self.status(pid,cid);r=self.receipt(cid)
  if not r or r['status']!='ready':raise WorkbenchError('ANIMATION_NOT_READY','动作尚未准备完成',409)
  path=Path(r['path'])
  try:relative=path.relative_to(self.root).as_posix() if path.is_absolute() else str(path)
  except ValueError:raise WorkbenchError('SOURCE_PATH_REJECTED','预览路径不在工作区',403)
  raw=read_file(self.root,relative,MAX_MODEL_BYTES)
  if sha(raw)!=r['sha256']:raise WorkbenchError('MODEL_CHANGED','动画预览哈希不一致',409)
  doc=validate_glb(raw)
  if not doc.get('animations'):raise WorkbenchError('ANIMATION_MISSING','动画缺失',422)
  return raw,r['sha256']
 def prepare(self,pid,cid,retry=False):
  pack,clip=self.clip(pid,cid);existing=self.status(pid,cid)
  if existing['status']=='ready' or (existing['status']=='failed' and not retry):return existing
  with self.lock:
   if self.active:
    if self.active['clip_id']==cid:return dict(self.active)
    raise WorkbenchError('ANIMATION_BUSY','正在准备其他动作，请稍候',409)
   self.active={'status':'preparing','phase':'native','clip_id':cid}
   threading.Thread(target=self._run,args=(pack,clip),daemon=True,name='asset-animation').start()
   return dict(self.active)
 def _run(self,pack,clip):
  cid=clip['id'];dest=self.base/'cache'/cid/uuid.uuid4().hex;dest.mkdir(parents=True,exist_ok=False);r={'status':'failed','code':'ANIMATION_PREPARATION_FAILED'}
  lockfile=None
  try:
   # OS lock also excludes another local workbench process from native preparation.
   import msvcrt
   lockfile=(self.base/'native-worker.lock').open('a+b');lockfile.seek(0);lockfile.write(b'0');lockfile.flush();lockfile.seek(0);msvcrt.locking(lockfile.fileno(),msvcrt.LK_NBLCK,1)
   project=safe_path(self.root,pack['project']);assert project.is_file(),'PROJECT_UNAVAILABLE'
   inputs=[{'file':str(safe_path(self.root,c['source_path'])),'sha256':c['sha256']} for c in [clip]+pack['meshes']]
   for item in inputs:assert sha(Path(item['file']).read_bytes())==item['sha256'],'SOURCE_CHANGED'
   request={'output':str(dest),'clip_path':clip['path'],'meshes':[m['path'] for m in pack['meshes']],'inputs':inputs}
   req=dest/'request.json';req.write_text(json.dumps(request));env={**os.environ,'AW_ANIMATION_REQUEST':str(req)}
   tools=self.root/'Tools/AssetWorkbench'
   ue=Path('C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe');blender=Path('C:/Program Files/Blender Foundation/Blender 5.2/blender.exe')
   def run(args,log,timeout):
    with log.open('w') as output:return subprocess.run(args,stdout=output,stderr=output,env=env,creationflags=subprocess.CREATE_NO_WINDOW,timeout=timeout).returncode
   code=run([str(ue),str(project),'-run=pythonscript','-script='+str(tools/'ue_prepare_animation.py'),'-AllowCommandletRendering','-d3d12','-unattended','-NoP4','-nosound','-NoSplash','-DDC=InstalledNoZenLocalFallback','-UDPMESSAGING_TRANSPORT_ENABLE=false','-abslog='+str(dest/'native-engine.log')],dest/'native.log',600)
   native=json.loads((dest/'native-result.json').read_text());assert native['status']=='exported',native.get('code','NATIVE_EXPORT_FAILED')
   with self.lock:self.active={'status':'preparing','phase':'convert','clip_id':cid}
   jobs=dest/'jobs.json';jobs.write_text(json.dumps([{'id':cid,'name':clip['name'],'fbx':str(dest/'source-action.fbx'),'fbx_sha256':native['fbx_sha256'],'output':str(dest)}]))
   run([str(blender),'--background','--disable-autoexec','--python',str(tools/'blender_animation_glb.py'),'--','--jobs',str(jobs)],dest/'blender.log',600)
   r=json.loads((dest/'glb-result.json').read_text());assert r['status']=='ready','GLB_VALIDATION_FAILED'
   raw=Path(r['path']).read_bytes();doc=validate_glb(raw);assert doc.get('animations'),'ANIMATION_MISSING'
   r.update(source_sha256=clip['sha256'],source_path=clip['path'],native_exit_code=code,native=native)
  except Exception as exc:
   r={'status':'failed','code':str(exc) if isinstance(exc,AssertionError) else 'ANIMATION_PREPARATION_FAILED','diagnostic':str(exc)}
  finally:
   result=dest/'result.json';result.write_text(json.dumps(r,indent=2))
   pointer=dest.parent/'current.json';temp=dest.parent/'current.tmp';temp.write_text(json.dumps({'receipt':result.relative_to(self.root).as_posix()}));temp.replace(pointer)
   if lockfile:lockfile.close()
   with self.lock:self.active=None
