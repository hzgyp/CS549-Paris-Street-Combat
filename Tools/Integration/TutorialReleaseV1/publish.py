"""Pinned-host private development publication; never touches old release aliases."""
from release import *

AID='paris-tutorial-packaged-release'
RID='paris-tutorial-runtime-resources'
NID='paris-tutorial-native-overlay'
def batch(commands,label):
 spec=importlib.util.spec_from_file_location('tutorial_sftp',ROOT/'Tools/Integration/publish_native_playtest.py')
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.OUT=OUT;m.batch(commands,label)
def upload():
 p=read(OUT/'PACKAGE.json');assert not (OUT/'PUBLICATION.json').exists()
 assert not (SHARE/'releases'/RELEASE).exists(),'Preserve immutable remote release'
 assets=[dict(p['archive'],kind='archive'),*[dict(x,kind='runtime') for x in p['resources']],*[dict(x,kind='native') for x in p['native']]]
 acl=subprocess.check_output(['pwsh','-NoProfile','-Command',"(Get-Acl -LiteralPath '"+str(SHARE)+"').Sddl"],text=True).strip()
 write(OUT/'SFTP_STARTED.json',dict(release=RELEASE,root_acl_sha256=hashlib.sha256(acl.encode()).hexdigest(),created=datetime.now().astimezone().isoformat()))
 dest=OUT/'sftp-readbacks';dest.mkdir(exist_ok=False);commands=[f'mkdir "/incoming/{RELEASE}"'];prefixes=set();objects={}
 for r in assets:
  verify(r);h=r['sha256'];remote=f'/objects/sha256/{h[:2]}/{h}';r.update(storage='sftp',remote_path=remote)
  if h in objects:continue
  path=SHARE/remote.lstrip('/');objects[h]=r
  if not path.exists():
   if not path.parent.exists() and h[:2] not in prefixes:commands.append(f'mkdir "/objects/sha256/{h[:2]}"')
   prefixes.add(h[:2]);part=f'/incoming/{RELEASE}/{h}.part'
   commands.extend([f'put "{Path(r["path"]).as_posix()}" "{part}"',f'rename "{part}" "{remote}"'])
  commands.append(f'get "{remote}" "{(dest/h).as_posix()}"')
 commands.append(f'rmdir "/incoming/{RELEASE}"')
 print('Authenticated object upload/reuse and full final readback:',len(objects),'objects',flush=True)
 batch(commands,'sftp-final-objects')
 for h,r in objects.items():verify(dict(r,path=str(dest/h)))
 common=dict(schema_version=1,asset_version=RELEASE,owner='Yupu Guo',published_at=datetime.now().astimezone().isoformat(),license_record='Assets/Sync/RIGHTS.md',sharing_status='owner_attested_private_three_member_original_and_derivative_sharing',recipients=['Yupu Guo','Yuqi Pu','Jingdi Wu'],game_sha256=GAME,source_variant=SOURCE.relative_to(ROOT).as_posix(),source_manifest_sha256=MANIFEST,verification=dict(method='Pinned-host authenticated SFTP full final object and named archive readback SHA256/size',human_review='Medical teaching and contextual music explicitly accepted; tutorial formal adoption requested',second_machine='Pending',coursework_delivery=False))
 manifests=[]
 for aid,kind in [(AID,'archive'),(RID,'runtime'),(NID,'native')]:
  selected=[]
  for r in assets:
   if r['kind']!=kind:continue
   x=dict(r);x.pop('kind');x['path']=Path(x['path']).relative_to(ROOT).as_posix();selected.append(x)
  m=dict(common,asset_id=aid,scope='Private tutorial1.0 development collaboration; no course submission or old remote replacement',dependencies=['france-liberation-content','paris-gameplay-native-playtest','paris-grenade-grips','paris-crouch-transitions','paris-medical-pouch'] if kind=='native' else [],files=selected,file_count=len(selected),size_bytes=sum(x['size_bytes'] for x in selected))
  if kind=='archive':m.update(entry='Extract all; PLAY_TUTORIAL.cmd',archive_members=p['members'],runtime_python_required=False,runtime_editor_bridge_required=False)
  if kind=='runtime':m.update(restoration='Copy restore_path into a new matching145-source Project. Matching-Source-145.zip is a complete private source snapshot including licensed curves. No current Game rebuild is claimed.')
  if kind=='native':m.update(restoration='Overlay restore_path after restoring Catalog-selected city/native dependencies. Matching145 Editor rebuild/dependency audit and second-machine verification remain required.')
  target=OUT/(aid+'.json');write(target,m);manifests.append((aid,target,m))
 alias=f'/releases/{RELEASE}/{Path(p["archive"]["path"]).name}'
 commands=[f'mkdir "/releases/{RELEASE}"',f'ln "{assets[0]["remote_path"]}" "{alias}"',f'get "{alias}" "{(OUT/"named-archive-readback.zip").as_posix()}"']
 for aid,path,m in manifests:
  remote=f'/releases/{RELEASE}/{path.name}';commands.extend([f'put "{path.as_posix()}" "{remote}"',f'get "{remote}" "{(OUT/("returned-"+path.name)).as_posix()}"'])
 print('Verify named archive alias and release manifests',flush=True);batch(commands,'sftp-release-alias-manifests')
 verify(dict(p['archive'],path=str(OUT/'named-archive-readback.zip')))
 for aid,path,m in manifests:assert sha(path)==sha(OUT/('returned-'+path.name))
 current_acl=subprocess.check_output(['pwsh','-NoProfile','-Command',"(Get-Acl -LiteralPath '"+str(SHARE)+"').Sddl"],text=True).strip();assert acl==current_acl
 record=dict(status='authenticated_final_objects_alias_manifests_verified',release=RELEASE,download=alias,archive=p['archive'],game_sha256=GAME,source_manifest_sha256=MANIFEST,objects=len(objects),root_acl_unchanged=True,old_remote_releases_untouched=True,coursework_delivery=False,manifests=[dict(asset_id=aid,path=str(path),sha256=sha(path),release_manifest=f'/releases/{RELEASE}/{path.name}') for aid,path,m in manifests])
 write(OUT/'PUBLICATION.json',record);print(dict(status=record['status'],download=alias,bytes=p['archive']['size_bytes']),flush=True)
def catalog():
 r=read(OUT/'PUBLICATION.json');assert r['status']=='authenticated_final_objects_alias_manifests_verified'
 catalog=read(ROOT/'Assets/Sync/CATALOG.json');before=dict(catalog);write(OUT/'CATALOG_IMMEDIATELY_BEFORE.json',catalog)
 for x in r['manifests']:
  aid=x['asset_id'];assert not any(y['asset_id']==aid for y in catalog['active_manifests'])
  m=read(x['path']);path='Assets/Sync/manifests/'+aid+'.json';write(ROOT/path,m)
  catalog['active_manifests'].append(dict(asset_id=aid,asset_version=RELEASE,path=path,sha256=sha(ROOT/path),file_count=m['file_count'],size_bytes=m['size_bytes'],release_manifest=x['release_manifest']))
 catalog['updated_at']=datetime.now().astimezone().isoformat();write(ROOT/'Assets/Sync/CATALOG.json',catalog)
 contract=dict(schema_version=1,asset_version=RELEASE,game_sha256=GAME,source_snapshot=SOURCE.relative_to(ROOT).as_posix()+'/Project',source_manifest=(SOURCE/'SOURCE_MANIFEST.json').relative_to(ROOT).as_posix(),source_manifest_sha256=MANIFEST,source_files=145,public_source_files=144,external_source_files=[dict(path=CURVE,sha256=sha(SOURCE/'Project'/CURVE),size_bytes=(SOURCE/'Project'/CURVE).stat().st_size,manifest='Assets/Sync/manifests/'+RID+'.json',reason='Licensed native animation curve data stays private')],runtime_manifest='Assets/Sync/manifests/'+RID+'.json',native_overlay_manifest='Assets/Sync/manifests/'+NID+'.json',package_manifest='Assets/Sync/manifests/'+AID+'.json',development_only=True,second_machine='pending',no_matching_editor_acceptance=True)
 write(ROOT/'Assets/Sync/TUTORIAL_SOURCE_CONTRACT_20261017.json',contract)
 print('Three new verified development manifests selected; all older Catalog records retained.',flush=True)
if __name__=='__main__':globals()[sys.argv[1]]()
