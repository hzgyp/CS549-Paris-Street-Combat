"""Retire one superseded development ZIP; preserve current/course/native bytes."""
from pathlib import Path
from datetime import datetime
import hashlib, importlib.util, json, os, shutil, stat, subprocess, sys

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'tmp/sftp-package-retirement-20261017'
PROOF=ROOT/'Docs/Development/TutorialSftpRetirementV1'
SHARE=ROOT/'Assets/LocalShared/SFTP'
OLD='paris-g1-playtest-20261011-gameplay-v1'
CURRENT='paris-tutorial-20261017-v1'
GAME='3bb90f646cbbfb3652bab5fcab23c0af2b3bd2d7add577028e6810a9c5576967'
OLDID='paris-g1-packaged-playtest'
read=lambda p:json.loads(Path(p).read_text('utf-8-sig'))

def write(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def file(p):
 p=Path(p).resolve();s=p.stat()
 return dict(path=str(p),size_bytes=s.st_size,sha256=sha(p),identity=[s.st_dev,s.st_ino,s.st_mtime_ns])
def remote_file(p,expected):
 p=Path(p).resolve();s=p.stat();assert s.st_size==expected['size_bytes']
 return dict(path=str(p),size_bytes=s.st_size,sha256=expected['sha256'],identity=[s.st_dev,s.st_ino,s.st_mtime_ns],content_via_authenticated_readback=True)
def verify(r,content=True):
 p=Path(r['path']);s=p.stat()
 assert s.st_size==r['size_bytes'],str(p)
 if 'identity' in r:assert [s.st_dev,s.st_ino,s.st_mtime_ns]==r['identity'],str(p)
 if content:assert sha(p)==r['sha256'],str(p)
def verify_many(rows):
 checked=set()
 for r in rows:
  p=Path(r['path']);s=p.stat();key=(s.st_dev,s.st_ino,s.st_mtime_ns,s.st_size)
  verify(r,key not in checked);checked.add(key)
def target(p):
 p=Path(p);assert p.resolve().is_relative_to(SHARE.resolve())
 for q in [p,*p.parents]:
  assert not q.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT,str(q)
  if q==SHARE:break
 return p
def acl():
 raw=subprocess.check_output(['pwsh','-NoProfile','-Command',"(Get-Acl -LiteralPath '"+str(SHARE)+"').Sddl"],text=True).strip()
 return hashlib.sha256(raw.encode()).hexdigest()
def batch(commands,label):
 profile=Path(os.environ['USERPROFILE'])
 p=subprocess.run(['sftp','-b','-','-P','22222','-B','262144','-R','64',
  '-i',str(profile/'.ssh/cs549_sftp_ed25519'),'-o','UserKnownHostsFile='+str(profile/'.ssh/known_hosts_cs549'),
  '-o','StrictHostKeyChecking=yes','-o','IdentitiesOnly=yes','cs549sftp@127.0.0.1'],
  input='\n'.join(commands)+'\n',text=True,capture_output=True)
 (OUT/(label+'.log')).write_text(p.stdout+'\n'+p.stderr,'utf-8');assert p.returncode==0,'Preserve/read private SFTP log '+label

def protected_download_aliases(f):
 selected={r['asset_id']:r for r in f['catalog']['active_manifests']}
 for aid,r in [('paris-tutorial-packaged-release',f['current']),('paris-g1-course-review-package',f['course'])]:
  alias=SHARE/'releases'/selected[aid]['asset_version']/Path(r['path']).name
  original=next(x for x in f['protected'] if x['path']==str((SHARE/r['remote_path'].lstrip('/')).resolve()))
  s=target(alias).stat()
  assert [s.st_dev,s.st_ino,s.st_mtime_ns]==original['identity'] and s.st_size==r['size_bytes'],'Preserve exact protected download alias'

def preflight():
 assert not (OUT/'FREEZE.json').exists(),'Preserve prior attempt; inspect before retry'
 OUT.mkdir(parents=True,exist_ok=True);PROOF.mkdir(parents=True,exist_ok=True)
 cat=read(ROOT/'Assets/Sync/CATALOG.json');selected={r['asset_id']:r for r in cat['active_manifests']}
 oldmeta=ROOT/selected[OLDID]['path'];old=read(oldmeta)['files'][0]
 assert selected[OLDID]['asset_version']==OLD and old['size_bytes']==8499470074
 current=read(ROOT/selected['paris-tutorial-packaged-release']['path'])['files'][0]
 course=read(ROOT/selected['paris-g1-course-review-package']['path'])['files'][0]
 assert current['sha256']=='f145c2e06bdc2aeeafc48397575552f91c661dacf3702135fec57c0d2957ab55'
 assert course['sha256']=='7a8c225ad66ea673e20d0259324c3b5fef25be25bb66fcdddb5344533bd26d7d'
 consumers=[]
 for r in cat['active_manifests']:
  d=read(ROOT/r['path']);assert sha(ROOT/r['path'])==r['sha256']
  assert OLDID not in d.get('dependencies',[]),'Preserve an active dependency'
  if any(x.get('remote_path')==old['remote_path'] for x in d['files']):consumers.append(r['asset_id'])
 assert consumers==[OLDID]
 alias='/releases/'+OLD+'/'+Path(old['path']).name
 targets=[remote_file(target(SHARE/alias.lstrip('/')),old),remote_file(target(SHARE/old['remote_path'].lstrip('/')),old)]
 assert all(r['sha256']==old['sha256'] and r['size_bytes']==old['size_bytes'] for r in targets)
 assert targets[0]['identity'][:2]==targets[1]['identity'][:2]
 assert (SHARE/alias.lstrip('/')).stat().st_nlink==2,'Unknown extra hardlink consumer'
 original=file(ROOT/old['path']);assert original['sha256']==old['sha256']
 assert original['identity'][:2]!=targets[0]['identity'][:2],'Recovery must be physically independent of server object'
 recovery=OUT/'recovery'/Path(old['path']).name;recovery.parent.mkdir(exist_ok=True)
 if not recovery.exists():os.link(original['path'],recovery)
 else:assert sha(recovery)==old['sha256']
 users=Path(os.environ['LOCALAPPDATA'])/'ParisStreetCombat'
 protected=[file(p) for p in sorted(users.rglob('*')) if p.is_file()]
 for r in [current,course]:
  p=SHARE/r['remote_path'].lstrip('/');x=remote_file(p,r);protected.append(x)
 for p in [ROOT/'PLAY_CURRENT_G1.cmd',ROOT/'Docs/Development/CURRENT_TUTORIAL_RELEASE.json',ROOT/'Docs/Development/CURRENT_TUTORIAL_SOURCE_PENDING.json']:
  protected.append(file(p))
 copied=[];commands=[];packages=[]
 for label,r in [('old',old),('current',current),('course',course)]:
  path=OUT/('authenticated-'+label+'.zip');commands.append(f'get "{r["remote_path"]}" "{path.as_posix()}"')
  packages.append(dict(path=str(path),size_bytes=r['size_bytes'],sha256=r['sha256']))
 for aid in [OLDID,'paris-tutorial-packaged-release','paris-g1-course-review-package']:
  s=selected[aid];out=OUT/('returned-'+aid+'.json')
  commands.append(f'get "{s["release_manifest"]}" "{out.as_posix()}"');copied.append((out,s['sha256']))
 commands += [f'ls -ln "{alias}"',f'ls -ln "{old["remote_path"]}"',f'ls -ln "/releases/{CURRENT}/{Path(current["path"]).name}"']
 print('Authenticate/read back3 exact packages before retirement; preserve server ACL.',flush=True)
 batch(commands,'authenticated-preflight')
 verify_many(packages)
 for path,digest in copied:assert sha(path)==digest
 hud=read(SHARE/'releases/paris-g1-playtest-20261009-hud-v3/paris-g1-packaged-playtest.json')['files'][0]
 assert not (SHARE/hud['remote_path'].lstrip('/')).exists()
 assert not (SHARE/'releases/paris-g1-playtest-20261009-hud-v3'/Path(hud['path']).name).exists()
 f=dict(status='exact_old_development_zip_ready',catalog=cat,catalog_sha256=sha(ROOT/'Assets/Sync/CATALOG.json'),
  targets=targets,remote_targets=[alias,old['remote_path']],original_local=original,recovery=file(recovery),protected=protected,
  manifests=[file(ROOT/r['path']) for r in cat['active_manifests']],old_manifest=selected[OLDID],root_acl=acl(),
  current=current,course=course,authenticated_packages=packages,hud_already_absent=True,free_before=shutil.disk_usage(SHARE).free)
 write(OUT/'FREEZE.json',f)
 inventory=dict(schema_version=1,status=f['status'],authorization='Human requests obsolete SFTP package cleanup and development Git push17October2026',
  retired_asset_id=OLDID,retired_version=OLD,targets=[dict(path=p,sha256=old['sha256'],size_bytes=old['size_bytes']) for p in f['remote_targets']],
  recovery=dict(path=str(recovery),sha256=old['sha256'],size_bytes=old['size_bytes']),
  protected=['Current tutorial1.0','AudioV2 instructor package','all native/runtime objects and old manifests','all actual human saves/settings'],
  active_consumers_before=consumers,hud_previous_absence_not_new_deletion=True,coursework_delivery=False)
 write(PROOF/'INVENTORY.json',inventory)
 (PROOF/'CATALOG.json.before').write_bytes((ROOT/'Assets/Sync/CATALOG.json').read_bytes())
 print(dict(status=f['status'],remote_files=2,unique_archive_bytes=old['size_bytes'],user_files=len(protected)-5),flush=True)

def retire():
 f=read(OUT/'FREEZE.json');assert f['status']=='exact_old_development_zip_ready'
 assert not (OUT/'RETIREMENT_DONE.json').exists()
 assert sha(ROOT/'Assets/Sync/CATALOG.json')==f['catalog_sha256']
 assert read(ROOT/'Assets/Sync/CATALOG.json')==f['catalog'],'Reconcile Catalog drift before deleting anything'
 for x in f['targets']:verify(x,False)
 verify_many([f['original_local'],f['recovery']]+f['manifests']+f['authenticated_packages'])
 for r in f['protected']:verify(r,False)
 protected_download_aliases(f)
 assert acl()==f['root_acl']
 for p in f['targets']:target(p['path'])
 batch([f'rm "{p}"' for p in f['remote_targets']],'delete-exact-old-development-zip')
 assert all(not Path(r['path']).exists() for r in f['targets'])
 # Catalog retirement preserves every other active selection and original manifest.
 cat=read(ROOT/'Assets/Sync/CATALOG.json');cat['active_manifests']=[r for r in cat['active_manifests'] if r['asset_id']!=OLDID]
 assert cat['active_manifests']==[r for r in f['catalog']['active_manifests'] if r['asset_id']!=OLDID]
 cat['updated_at']=datetime.now().astimezone().isoformat();write(ROOT/'Assets/Sync/CATALOG.json',cat)
 # Catalog is byte-pinned in Git; preserve its existing Windows line endings.
 if b'\r\n' in (PROOF/'CATALOG.json.before').read_bytes():
  p=ROOT/'Assets/Sync/CATALOG.json';p.write_bytes(p.read_bytes().replace(b'\n',b'\r\n'))
 result=dict(schema_version=1,status='superseded_development_archive_retired',retired_version=OLD,retired_asset_id=OLDID,
  removed_remote_paths=f['remote_targets'],removed_named_files=2,unique_archive_bytes=f['recovery']['size_bytes'],
  current_release=CURRENT,current_download='/releases/'+CURRENT+'/'+Path(f['current']['path']).name,
  current_archive_sha256=f['current']['sha256'],current_archive_bytes=f['current']['size_bytes'],
  recovery=f['recovery'],original_manifest=f['old_manifest'],source_native_course_metadata_preserved=True,
  already_absent_hud_not_counted=True,coursework_delivery=False)
 write(OUT/'RETIREMENT_DONE.json',result)
 write(ROOT/'Assets/Sync/retired/PACKAGED_PLAYTEST_RETIREMENT_20261017.json',result)
 # Public recovery metadata contains no file bytes, credentials or human saves.
 public=dict(result);public['recovery']={k:result['recovery'][k] for k in ['path','size_bytes','sha256']}
 write(PROOF/'RESULT.json',public)
 print(dict(status=result['status'],removed_remote_files=2,active_assets=len(cat['active_manifests'])),flush=True)

def guides():
 f=read(OUT/'FREEZE.json');r=read(OUT/'RETIREMENT_DONE.json');download=r['current_download'];digest=r['current_archive_sha256'];size=r['current_archive_bytes']
 texts={
 'DOWNLOAD_README.md':f'''# Paris tutorial1.0 — teammate playtest

Download `{download}` ({size:,} bytes; SHA256 `{digest}`). Extract the complete ZIP into a writable Windows x64 folder and run `PLAY_TUTORIAL.cmd`. Keep all extracted subfolders. Python and Unreal Editor are unnecessary for this package. This is the unchanged17October human-reviewed tutorial Game `{GAME}`.

Language: Simplified Chinese and English; Esc opens menus/settings and audio controls. E interacts/recruits/picks up; while injured, stop moving and hold H for3 seconds to use a medical kit. Follow the on-screen tutorial. Existing local saves/settings remain in `%LOCALAPPDATA%/ParisStreetCombat/G1MedicalGuidanceMusic20261017`; the archive contains no personal saves. Keep your current save folder when switching packages.

Please review the tutorial, recruitment/checkpoints, prone directional/mouse movement, FP grenade action, medical drop/pickup/healing and audio/UI. Record language, resolution, tutorial step, expected/actual behavior and reproduction steps. Second-machine play remains pending until a teammate actually tests. This guide is development collaboration, not coursework delivery.
''',
 'DOWNLOAD_README_ZH.md':f'''# 教学正式版1.0：组员试玩说明

SFTP下载：`{download}`。大小：{size:,}字节（约8.27GB）。SHA256：`{digest}`。

完整下载ZIP，解压到Windows电脑上有写入权限的文件夹，运行根目录的 `PLAY_TUTORIAL.cmd`。保留解压出的全部子目录，无需安装Python或Unreal Editor。此包原样采用10月17日已人工验收版本，Game为 `{GAME}`。

支持简体中文和英语；Esc打开菜单、语言与声音设置。E交互/招募/拾取；受伤后停止移动，按住H三秒使用医疗包回血，其他操作跟随屏幕教学。存档/设置位于 `%LOCALAPPDATA%/ParisStreetCombat/G1MedicalGuidanceMusic20261017`，分发包不含个人存档；更换包时保留已有存档目录。

建议复核：完整教学、招募与checkpoint、匍匐左右/斜向和鼠标转向、第一人称投掷、医疗包掉落/拾取/回血、音乐与提示界面。反馈请写语言、分辨率、所在教学步骤、预期与实际结果、复现方法。组员电脑实际试玩尚待完成。此为项目开发协作试玩说明。
'''}
 for name,text in texts.items():(OUT/name).write_text(text,'utf-8',newline='\n')
 tombstone={k:r[k] for k in ['status','retired_version','removed_remote_paths','current_release','current_download','current_archive_sha256','current_archive_bytes','coursework_delivery']}
 write(OUT/'RETIRED_20261017.json',tombstone)
 commands=[]
 for local,remote in [(OUT/n,'/releases/'+CURRENT+'/'+n) for n in texts]+[(OUT/'RETIRED_20261017.json','/releases/'+OLD+'/RETIRED_20261017.json')]:
  assert not (SHARE/remote.lstrip('/')).exists(),'Preserve an existing publication'
  commands += [f'put "{local.as_posix()}" "{remote}"',f'get "{remote}" "{(OUT/("readback-"+local.name)).as_posix()}"']
 batch(commands,'guides-and-retirement-readback')
 for local in [*(OUT/n for n in texts),OUT/'RETIRED_20261017.json']:assert sha(local)==sha(OUT/('readback-'+local.name))
 for name in texts:shutil.copyfile(OUT/name,PROOF/name)
 print('Bilingual teammate guides and retirement sidecar authenticated/read back.',flush=True)

def verify_final():
 f=read(OUT/'FREEZE.json');r=read(OUT/'RETIREMENT_DONE.json')
 for x in f['protected']:
  verify(x,not x.get('content_via_authenticated_readback',False))
 protected_download_aliases(f)
 verify_many([f['original_local'],f['recovery']]+f['manifests'])
 assert all(not Path(x['path']).exists() for x in f['targets']) and acl()==f['root_acl']
 cat=read(ROOT/'Assets/Sync/CATALOG.json');assert cat['active_manifests']==[x for x in f['catalog']['active_manifests'] if x['asset_id']!=OLDID]
 r.update(root_acl_unchanged=True,authenticated_package_hashes_before_pass=True,protected_remote_identities_after_exact=True,local_user_manifest_hashes_after_exact=True,free_after=shutil.disk_usage(SHARE).free,
  observed_volume_free_delta=shutil.disk_usage(SHARE).free-f['free_before'],measurement='Whole-volume concurrent activity; unique archive size is not a guaranteed volume delta.')
 write(OUT/'VERIFIED.json',r)
 public=read(PROOF/'RESULT.json');public.update({k:r[k] for k in ['root_acl_unchanged','authenticated_package_hashes_before_pass','protected_remote_identities_after_exact','local_user_manifest_hashes_after_exact','free_after','observed_volume_free_delta','measurement']});write(PROOF/'RESULT.json',public)
 print(dict(status='exact_retirement_and_protected_bytes_pass',unique_archive_bytes=r['unique_archive_bytes'],observed_free_delta=r['observed_volume_free_delta']),flush=True)

def clean_readbacks():
 f=read(OUT/'FREEZE.json');assert read(OUT/'VERIFIED.json')['protected_remote_identities_after_exact']
 preserved=[f['original_local'],dict(f['current'],path=str(ROOT/f['current']['path'])),dict(f['course'],path=str(ROOT/f['course']['path']))]
 verify_many(preserved)
 rows=f['authenticated_packages'];verify_many(rows)
 assert [Path(x['path']).name for x in rows]==['authenticated-old.zip','authenticated-current.zip','authenticated-course.zip']
 for x,y in zip(rows,preserved):
  assert x['sha256']==y['sha256'] and x['size_bytes']==y['size_bytes']
  p=Path(x['path']);assert p.parent==OUT and not p.is_symlink();p.unlink()
 receipt=dict(status='three_owned_duplicate_readbacks_removed_after_hash_verification',removed_files=rows,
  retained_exact_copies=[dict(path=y['path'],sha256=y['sha256'],size_bytes=y['size_bytes']) for y in preserved],
  server_deletion_scope_unchanged=True,personal_or_course_upload=False)
 write(OUT/'READBACK_DUPLICATE_CLEANUP.json',receipt)
 print(dict(status=receipt['status'],files=len(rows)),flush=True)

def documents():
 r=read(OUT/'VERIFIED.json');f=read(OUT/'FREEZE.json')
 en=f'''# Tutorial1.0 teammate download and obsolete development archive retirement

17 October2026. The human requested Git commit/push, obsolete SFTP package cleanup and the latest teammate playtest path. Tutorial1.0 remains the unchanged reviewed145-source/Game `{GAME}`. No build/cook, engine entry, model/action edit, save migration or coursework delivery occurred.

Current SFTP download: `{r['current_download']}`. Archive size:{r['current_archive_bytes']:,} bytes; SHA256 `{r['current_archive_sha256']}`. Extract the complete ZIP and run `PLAY_TUTORIAL.cmd`. The bilingual teammate instructions are under this release as `DOWNLOAD_README.md` and `DOWNLOAD_README_ZH.md`, and in `Docs/Development/TutorialSftpRetirementV1/`. No Python/Editor is needed. Actual teammate/second-machine play remains pending.

Only the11October superseded development ZIP was removed from SFTP: its named release alias and SHA object, two directory entries for one{r['unique_archive_bytes']:,}-byte body. The former `paris-g1-packaged-playtest` selection is deactivated, its exact manifest retained, and every other active Catalog selection unchanged. The old release directory, original manifests/guides, source/native/runtime resources and AudioV2 instructor package remain preserved. The older HUD ZIP/object were already absent and are not counted as new deletions. A dated sidecar redirects teammates; all3 new text files passed authenticated upload/readback SHA checks.

Pinned-host authenticated SFTP returned all3 package bodies before deletion and their full SHA/size matched. The retired archive has a physically independent verified local original plus a protected local recovery link recorded in the inventory. After deletion, protected server file identities/mtime/size, original user/control/manifest hashes and root ACL remained exact; no second server-content hash is claimed. Retirement-phase whole-volume free-space change was{r['observed_volume_free_delta']:,} bytes; concurrent disk activity may affect it. The three task-owned verification downloads were removed only after matching exact retained local copies; all logs/receipts stay retained. Details: `TutorialSftpRetirementV1/INVENTORY.json`, `RESULT.json`, `Assets/Sync/retired/PACKAGED_PLAYTEST_RETIREMENT_20261017.json` and private task receipts. Git publication and platform readback receipts follow separately; unrelated main-worktree edits/index are preserved.
'''
 zh=f'''# 教学正式版1.0组员下载与SFTP旧开发包清理

2026年10月17日。当前教学正式版仍为已验收source145/Game `{GAME}`，没有重建、动作/模型修改或存档迁移。

组员SFTP下载：`{r['current_download']}`，{r['current_archive_bytes']:,}字节（约8.27GB），SHA256 `{r['current_archive_sha256']}`。完整解压后运行 `PLAY_TUTORIAL.cmd`，无需Python或Unreal Editor。中英文试玩说明在同目录 `DOWNLOAD_README.md` / `DOWNLOAD_README_ZH.md`，并在本项目TutorialSftpRetirementV1中保留。组员电脑实际试玩仍待完成。

本次只撤下10月11日旧开发试玩ZIP的下载文件名与SHA对象，共2个远程文件名，对应同一份{r['unique_archive_bytes']:,}字节归档；Catalog取消旧开发包的可用选择，其原始清单保留，其他全部当前选择不变。原发布目录/清单/说明、源码/原生资源/运行资源和AudioV2老师评审包未动。更早HUD包本来就不存在，不冒称本次删除。新增退役说明及中英文下载指南均经过认证SFTP回读校验。

删除前通过固定主机密钥的认证SFTP完整读回三份包并验证SHA/大小；旧包有独立本地原件及精确恢复链接。删除后当前/评审包的服务器文件身份、时间/大小、原用户与清单/控制文件字节、根权限均保持一致，不冒称再做了一轮服务器全文哈希。清理阶段全盘空闲观测变化{r['observed_volume_free_delta']:,}字节，受并行活动影响。三份临时校验下载均匹配保留的同字节本地原件后才删除，日志与记录保留。开发Git提交及平台刷新回执另记，不覆盖主工作区其他窗口尚未完成的修改。
'''
 for suffix,text in [('',en),('_ZH',zh)]:
  p=ROOT/('Docs/Development/MissionLoopV1/TUTORIAL_SFTP_RETIREMENT_RESULT_20261017'+suffix+'.md');p.write_text(text,'utf-8',newline='\n')
 # Update only the current tutorial's documentation links in the local platform.
 p=ROOT/'Assets/Registry/gameplay/designs.json';d=read(p);g=next(x for x in d['entries'] if x['id']=='g1-tutorial')
 for rel,title in [('Docs/Development/TutorialSftpRetirementV1/DOWNLOAD_README.md','Tutorial1.0 teammate download'),('Docs/Development/TutorialSftpRetirementV1/DOWNLOAD_README_ZH.md','教学正式版组员下载'),('Docs/Development/MissionLoopV1/TUTORIAL_SFTP_RETIREMENT_RESULT_20261017.md','Obsolete development archive retirement'),('Docs/Development/MissionLoopV1/TUTORIAL_SFTP_RETIREMENT_RESULT_20261017_ZH.md','旧开发试玩包清理记录')]:
  assert not any(x.get('path')==rel for x in g['documents'])
  g['documents'].append(dict(path=rel,registered_sha256=sha(ROOT/rel),title={'en':title,'zh':title}))
 write(p,d);print('Bilingual result and bounded tutorial document registrations written.',flush=True)

if __name__=='__main__':globals()[sys.argv[1]]()
