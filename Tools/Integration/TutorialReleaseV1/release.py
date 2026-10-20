"""Adopt the exact human-reviewed tutorial; bounded local retirement and private development release."""
from pathlib import Path
from datetime import datetime
import hashlib,json,os,shutil,subprocess,sys,zipfile,stat,importlib.util

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'tmp/tutorial-release-v1-20261017'
TASK=ROOT/'tmp/g1-medical-guidance-music-playtest-20261017'
PROOF=ROOT/'Docs/Development/TutorialReleaseV1'
RELEASE='paris-tutorial-20261017-v1'
FORMAL=ROOT/'Releases/Paris-Tutorial-1.0-20261017'
SOURCE=ROOT/'Unreal/Variants/G1MedicalGuidanceMusic20261017'
NORMAL=ROOT/'tmp/Playtest-G1-Medical-Guidance-Music-20261017'
SHARE=ROOT/'Assets/LocalShared/SFTP'
GAME='3bb90f646cbbfb3652bab5fcab23c0af2b3bd2d7add577028e6810a9c5576967'
MANIFEST='faa136ed3bbafa07e93253b3c6faefab6eb4380cc06e657ee9d3c67baa0a9c91'
CURVE='Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisProneNativeCurves.inl'
INNER='Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'
read=lambda p:json.loads(Path(p).read_text('utf-8-sig'))
def write(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def row(p):
 p=Path(p).resolve();return dict(path=str(p),size_bytes=p.stat().st_size,sha256=sha(p))
def verify(r):
 p=Path(r['path']);assert p.stat().st_size==r['size_bytes'] and sha(p)==r['sha256'],str(p)
def verify_many(rows):
 cache={}
 for r in rows:
  p=Path(r['path']);s=p.stat();key=(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)
  if key not in cache:cache[key]=sha(p)
  assert s.st_size==r['size_bytes'] and cache[key]==r['sha256'],str(p)
def files(p):return sorted(x for x in Path(p).rglob('*') if x.is_file())
def idle():
 cmd="@(Get-CimInstance Win32_Process|Where-Object {$_.Name -match 'UnrealEditor|WW2France|UnrealBuildTool|AutomationTool|ShaderCompileWorker'}).Count"
 assert subprocess.check_output(['pwsh','-NoProfile','-Command',cmd],text=True).strip()=='0','Preserve other engine/build owner'
def no_reparse(p):
 p=Path(p);assert p.resolve().is_relative_to(ROOT)
 for q in [p,*p.parents]:
  if q==ROOT:break
  if q.exists():assert not q.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT,str(q)
def freeze():
 idle();assert not OUT.exists();OUT.mkdir();PROOF.mkdir(exist_ok=False)
 d=read(TASK/'DELIVERY.json');assert d['game_sha256']==GAME and sha(SOURCE/'SOURCE_MANIFEST.json')==MANIFEST
 assert read(TASK/'CHECKS.json')['status']=='pass_selected_medical_guidance_music_checks'
 assert read(TASK/'RESERVATION.json')['status']=='finished'
 for r in read(SOURCE/'SOURCE_MANIFEST.json')['files']:verify(dict(r,path=str(SOURCE/'Project'/r['path'])))
 assert sha(NORMAL/INNER)==GAME
 for name in ['CURRENT_DEVELOPMENT_BASELINE.json','CURRENT_TUTORIAL_SOURCE_PENDING.json','CURRENT_MEDICAL_GUIDANCE_MUSIC_PLAYTEST_REVIEW.json']:
  shutil.copyfile(ROOT/'Docs/Development'/name,PROOF/(name+'.before'))
 for p in ['Assets/Sync/CATALOG.json','Assets/Registry/registry.json','Assets/Registry/gameplay/designs.json','HANDOFF_CURRENT.md']:
  shutil.copyfile(ROOT/p,OUT/('before-'+Path(p).name))
 users=Path.home()/'AppData/Local/ParisStreetCombat'
 old=read(TASK/'FREEZE.json');guards=[]
 for r in old['guards']:
  p=Path(r['path']).resolve()
  if p.suffix.lower() in {'.json','.cmd'}:continue
  verify(r);guards.append(r)
 user_files=[row(p) for p in files(users)]
 f=dict(created=datetime.now().astimezone().isoformat(),authorization='Human accepts medical teaching/music and requests tutorial formal release, intermediate build cleanup and development Git/SFTP sync; no coursework delivery.',user_files=user_files,guards=guards,source_manifest=MANIFEST,game_sha256=GAME,pending_sha256=sha(ROOT/'Docs/Development/CURRENT_TUTORIAL_SOURCE_PENDING.json'),old_baseline=read(PROOF/'CURRENT_DEVELOPMENT_BASELINE.json.before'),normal_files=[row(p) for p in files(NORMAL)])
 write(OUT/'FREEZE.json',f);print(dict(status='frozen',user_files=len(user_files),saves=sum(x['path'].endswith('.sav') for x in user_files),guards=len(guards)),flush=True)
def local():
 idle();f=read(OUT/'FREEZE.json');assert not FORMAL.exists();FORMAL.mkdir(parents=True)
 for p in files(NORMAL):
  q=FORMAL/p.relative_to(NORMAL);q.parent.mkdir(parents=True,exist_ok=True)
  if p.suffix.lower() in {'.json','.ini','.txt','.cmd','.md','.log'}:shutil.copyfile(p,q)
  else:os.link(p,q)
 shutil.copyfile(FORMAL/'PLAY_MEDICAL_GUIDANCE_MUSIC.cmd',FORMAL/'PLAY_TUTORIAL.cmd')
 version=dict(release=RELEASE,version='1.0',scope='Formal tutorial development release',game_sha256=GAME,source_manifest_sha256=MANIFEST,source_files=145,human_accepted=['medical teaching guidance','contextual background music'],user_dir='G1MedicalGuidanceMusic20261017',save_prefix='ParisCheckpointHistoryV1',coursework_delivery=False)
 write(FORMAL/'VERSION.json',version)
 (FORMAL/'README_EN.md').write_text('Paris tutorial1.0 — private three-member development release. Extract all and run PLAY_TUTORIAL.cmd. Windows x64; no Python or Editor needed. E interacts/picks up; when injured, stop moving and hold H for3 seconds to restore up to50 health. Esc opens menus/settings; audio controls and English/Simplified Chinese are available. Existing actual local saves/settings are used unchanged. No personal saves/settings are included in the distributable. Full-map, stress, Editor/PIE and second-machine acceptance are not claimed. Asset/audio credits remain in the package. Source restoration requires the external private resources and city/native dependencies listed in the release manifest.\n','utf-8')
 (FORMAL/'README_ZH.md').write_text('巴黎教学阶段正式版1.0。完整解压后运行 PLAY_TUTORIAL.cmd；无需Python或编辑器。E交互/拾取；受伤后停止移动，长按H三秒恢复最多50生命。Esc打开菜单、声音和中英文设置。沿用当前实际存档及设置，不重置、不赠送资源。分发包不含个人存档和设置。医疗提示与配乐已人工通过；没有扩大为全地图、压力、Editor/PIE或第二台机器验收。模型、动画、音频权利/鸣谢保留。仅三名组员的开发协作，不是课程提交。\n','utf-8')
 write(OUT/'LOCAL.json',dict(**version,entry='Releases/Paris-Tutorial-1.0-20261017/PLAY_TUTORIAL.cmd',directory=str(FORMAL),normal_trial_retained=True,user_files_changed=False))
 print('Exact reviewed Game staged as local tutorial1.0; current human UserDir unchanged.',flush=True)
def archive():
 f=read(OUT/'FREEZE.json');assert sha(FORMAL/INNER)==GAME
 p=OUT/'Paris-Tutorial-1.0-20261017.zip';assert not p.exists();members=[]
 with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,compresslevel=1,allowZip64=True) as z:
  for i,x in enumerate(files(FORMAL)):
   rel=x.relative_to(FORMAL).as_posix();assert 'Saved/' not in rel
   z.write(x,rel);members.append(dict(path=rel,size_bytes=x.stat().st_size,sha256=sha(x)))
   if i%40==0:print('Archive members written',i+1,flush=True)
 with zipfile.ZipFile(p) as z:
  assert len(z.infolist())==len(members)
  for r in members:
   with z.open(r['path']) as s:assert hashlib.file_digest(s,'sha256').hexdigest()==r['sha256']
 source_zip=OUT/'Matching-Source-145.zip'
 with zipfile.ZipFile(source_zip,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for r in read(SOURCE/'SOURCE_MANIFEST.json')['files']:z.write(SOURCE/'Project'/r['path'],'Project/'+r['path'])
  z.write(SOURCE/'SOURCE_MANIFEST.json','SOURCE_MANIFEST.json')
 with zipfile.ZipFile(source_zip) as z:
  for r in read(SOURCE/'SOURCE_MANIFEST.json')['files']:
   with z.open('Project/'+r['path']) as s:assert hashlib.file_digest(s,'sha256').hexdigest()==r['sha256']
 resources=[]
 for x in files(FORMAL/'Windows/WW2FranceLiberation'):
  rel=x.relative_to(FORMAL/'Windows/WW2FranceLiberation').as_posix()
  if rel.startswith(('Audio/','Equipment/','UI/')):resources.append(dict(**row(x),restore_path=rel))
 resources += [dict(**row(SOURCE/'Project'/CURVE),restore_path=CURVE),dict(**row(source_zip),restore_path='Matching-Source-145.zip')]
 native={}
 for name in ['tmp/g1-thumb-polish-playtest-20261017/NATIVE_MANIFEST.json','tmp/g1-medical-playtest-20261017/NATIVE_MANIFEST.json']:
  for r in read(ROOT/name)['files']:
   x=Path(r['path']).resolve();verify(r);parts=x.as_posix().split('/Content/');assert len(parts)==2
   native['Content/'+parts[1]]=dict(**row(x),restore_path='Content/'+parts[1])
 write(OUT/'PACKAGE.json',dict(archive=row(p),members=members,resources=resources,native=list(native.values()),source_archive=row(source_zip),package_file_count=len(members),package_size_bytes=sum(r['size_bytes'] for r in members)))
 print(dict(status='archives_fully_readback_verified',archive_bytes=p.stat().st_size,members=len(members),runtime_resources=len(resources),native_overlay=len(native)),flush=True)
def recovery():
 idle();f=read(OUT/'FREEZE.json');targets=[]
 for n in range(1,9):
  for name in ['Runtime','Runtime_stage_v2']:
   p=TASK/('game_v'+str(n))/name
   if p.is_dir():targets.append(p)
 assert len(targets)==7
 lookup={};cache={}
 def fastrow(p):
  s=p.stat();key=(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)
  if key not in cache:cache[key]=sha(p)
  return dict(path=str(p.resolve()),size_bytes=s.st_size,sha256=cache[key])
 for p in files(FORMAL):
  r=fastrow(p);lookup[(r['size_bytes'],r['sha256'])]=str(p.resolve())
 records=[];unique={};target_rows=[]
 for target in targets:
  no_reparse(target);rs=[]
  for p in files(target):
   no_reparse(p);r=fastrow(p);key=(r['size_bytes'],r['sha256'])
   if key in lookup:r['retained_path']=lookup[key]
   else:unique.setdefault(r['sha256'],str(p.resolve()));r['archive_member']=r['sha256']
   records.append(r);rs.append(r)
  target_rows.append(dict(path=str(target.resolve()),files=len(rs),size_bytes=sum(r['size_bytes'] for r in rs)))
 archive=OUT/'INTERMEDIATE_UNIQUE_RECOVERY.zip';assert not archive.exists()
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as z:
  for h,p in unique.items():z.write(p,h)
 with zipfile.ZipFile(archive) as z:
  for h in unique:
   with z.open(h) as s:assert hashlib.file_digest(s,'sha256').hexdigest()==h
 verify_many([dict(r,path=r['retained_path']) for r in records if 'retained_path' in r])
 plan=dict(status='recovery_fully_verified',scope='Only7 explicitly inventoried generated Runtime directories in this build task; source/log/images/UserDirs/native/cache/old normals remain.',targets=target_rows,records=records,recovery_archive=row(archive),unique_objects=len(unique),logical_bytes=sum(r['size_bytes'] for r in records))
 write(PROOF/'RETIREMENT_INVENTORY.json',plan);write(OUT/'RECOVERY_READY.json',dict(status='pass',inventory_sha256=sha(PROOF/'RETIREMENT_INVENTORY.json')))
 print(dict(targets=len(targets),files=len(records),unique_objects=len(unique),logical_bytes=plan['logical_bytes'],recovery_bytes=archive.stat().st_size),flush=True)
def predelete():
 idle();f=read(OUT/'FREEZE.json');plan=read(PROOF/'RETIREMENT_INVENTORY.json')
 assert sha(PROOF/'RETIREMENT_INVENTORY.json')==read(OUT/'RECOVERY_READY.json')['inventory_sha256']
 verify_many(f['user_files']+f['guards']+f['normal_files']+plan['records'])
 for t in plan['targets']:no_reparse(t['path']);assert Path(t['path']).resolve().is_relative_to(TASK)
 verify(plan['recovery_archive']);assert sha(FORMAL/INNER)==GAME
 write(OUT/'PREDELETE.json',dict(status='pass',inventory_sha256=sha(PROOF/'RETIREMENT_INVENTORY.json'),free_bytes=shutil.disk_usage(ROOT).free))
 print('Exact inventory/recovery/users/native/idle predelete gates pass.',flush=True)
def afterdelete():
 f=read(OUT/'FREEZE.json');p=read(PROOF/'RETIREMENT_INVENTORY.json');assert all(not Path(t['path']).exists() for t in p['targets'])
 verify_many(f['user_files']+f['guards']+f['normal_files'])
 assert sha(FORMAL/INNER)==GAME and sha(NORMAL/INNER)==GAME
 before=read(OUT/'PREDELETE.json')['free_bytes'];after=shutil.disk_usage(ROOT).free
 write(PROOF/'RETIREMENT_RESULT.json',dict(status='pass_exact_retirement_and_protection',targets=len(p['targets']),logical_removed_bytes=p['logical_bytes'],free_before=before,free_after=after,observed_free_delta=after-before,measurement_scope='Whole-volume concurrent activity and hardlinks; not logical bytes freed.',original_user_files=len(f['user_files']),original_saves=sum(r['path'].endswith('.sav') for r in f['user_files']),guards=len(f['guards']),recovery_archive=p['recovery_archive']))
 print(read(PROOF/'RETIREMENT_RESULT.json'),flush=True)
if __name__=='__main__':globals()[sys.argv[1]]()
