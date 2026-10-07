"""Private V11 native release, verified before Catalog selection; no Git push."""
import argparse,importlib.util,difflib
from datetime import datetime
from common import *
RELEASE='paris-native-playtest-20261006-german-grip-v11'
AID='paris-gameplay-native-playtest'
OUT=BASE/'publication_v1'
DEST=ROOT/'Assets/Sync/manifests/paris-gameplay-native-playtest.json'
spec=importlib.util.spec_from_file_location('german_native_transport',ROOT/'Tools/Integration/publish_native_playtest.py')
transport=importlib.util.module_from_spec(spec);spec.loader.exec_module(transport);transport.OUT=OUT

def publish():
    assert not OUT.exists(),'Preserve occupied publication'
    acl=transport.idle_and_acl();guards(True)
    for name in ('early_v1','compat_v1','fresh_v1'):
        proof=read(BASE/name/'result.json');assert proof['status'].startswith('passed_') and not proof['errors']
        assert read(BASE/name/'image_review.json')['native_originals_inspected']
    logfile=ROOT/'tmp/german-npc-formal-v14/ordinary_game_v2.log'
    assert read(Path(str(logfile)+'.exit.json'))['exit_code']==0
    log=logfile.read_text(encoding='utf-8-sig',errors='replace')
    assert log.count('PARIS_GERMAN_GRIP_READY')==3 and log.count('PARIS_ALLIED_GRIP_READY')==2
    assert 'PARIS_GERMAN_GRIP_FAILURE' not in log and 'PARIS_ALLIED_GRIP_FAILURE' not in log
    author=read(BASE/'author_v1/result.json');assert not author['errors'] and all(exact(f) for f in author['saved_files'])
    audit=read(BASE/'audit_v1/result.json')
    assert audit['status']=='passed_saved_dependency_closure' and not audit['errors'] and not audit['hard_missing_packages']
    previous_audit=read(STORE/'Evidence/AlliedNPCFormalV18/audit_v1/result.json')
    assert set(audit['external_dependencies'])-set(previous_audit['external_dependencies'])=={'/InterchangeAssets/gltf/MaterialInstances/MI_Default_Opaque_DS'},'Unexpected engine/plugin dependency'
    old=read(DEST);assert audit['missing_referencers']==old['known_vendor_soft_reference_gaps']
    catalog=read(ROOT/'Assets/Sync/CATALOG.json');selected=next(e for e in catalog['active_manifests'] if e['asset_id']==AID)
    assert selected['sha256']==sha(DEST)
    city={f['path']:f for f in read(ROOT/'Assets/Sync/manifests/france-liberation-content.json')['files']}
    others={f['path'] for e in catalog['active_manifests'] if e['asset_id']!=AID for f in read(ROOT/e['path'])['files']}
    files=[]
    for f in audit['files']:
        if f['path'] in city:assert f['sha256']==city[f['path']]['sha256'];continue
        assert exact(f) and f['path'] not in others;files.append(f)
    for folder,names in ((ROOT/'Unreal/ParisStreetCombat/Plugins/ParisGripBindingV18/Binaries/Win64',
            ('UnrealEditor-ParisGripBindingV18.dll','UnrealEditor.modules')),
            (PLUGIN/'Binaries/Win64',('UnrealEditor-ParisNPCGripV15.dll','UnrealEditor-ParisNPCGripV15Editor.dll','UnrealEditor.modules'))):
        files.extend(row(folder/n) for n in names)
    by_path={f['path']:f for f in files};assert len(by_path)==len(files)
    # Keep the existing manifest field/file ordering to make the reviewed patch small.
    old_paths={f['path'] for f in old['files']}
    ordered=[{**f,**by_path[f['path']]} for f in old['files'] if f['path'] in by_path]
    ordered.extend(f for f in sorted(files,key=lambda f:f['path']) if f['path'] not in old_paths)
    files=[{**f,'storage':'sftp','remote_path':f"/objects/sha256/{f['sha256'][:2]}/{f['sha256']}"} for f in ordered]
    assert old_paths.issubset(by_path),'Unexpected retired dependency; stop for review'
    OUT.mkdir(parents=True);write(OUT/'started.json',{'release':RELEASE,'previous_manifest_sha256':sha(DEST)})
    commands=[f'mkdir "/incoming/{RELEASE}"'];prefixes=set();downloads={};uploaded=[];reused=[]
    for f in files:
        h=f['sha256']
        if h in downloads:continue
        final=transport.SHARE/f['remote_path'].lstrip('/')
        if final.exists():reused.append(h)
        else:
            if h[:2] not in prefixes and not final.parent.exists():commands.append(f'mkdir "/objects/sha256/{h[:2]}"')
            prefixes.add(h[:2]);stage=f'/incoming/{RELEASE}/{h}.part'
            commands.extend([f'put "{(ROOT/f["path"]).as_posix()}" "{stage}"',f'rename "{stage}" "{f["remote_path"]}"']);uploaded.append(h)
        dest=OUT/'verified-downloads'/h;dest.parent.mkdir(parents=True,exist_ok=True)
        downloads[h]=(dest,f);commands.append(f'get "{f["remote_path"]}" "{dest.as_posix()}"')
    commands.append(f'rmdir "/incoming/{RELEASE}"');transport.batch(commands,'objects')
    for dest,f in downloads.values():transport.verify(dest,f);assert exact(f)
    now=datetime.now().astimezone().isoformat()
    allied_selection=dict(old['allied_npc_selection'])
    allied_selection.pop('player_german_ai_unchanged',None)
    allied_selection['accepted_allied_first_person_ai_unchanged']=True
    allied_selection['german_selection']='Separate German V11 policy below; no Allied parameters copied'
    manifest={**old,'asset_version':RELEASE,'published_at':now,
        'scope':'Approved FP V20, Allied V16 and German V11 WITH FineWoodV15 rifle as formal MVP visual baselines; private UE5.8.2 editor playtest, not full MVP/Shipping acceptance',
        'source':'Fresh saved-map closure, preserved approved policies and matching native display modules',
        'runtime_plugins':[p.replace('native Allied policy','native Allied/German policies') for p in old['runtime_plugins']]+['UE5.8.2 bundled InterchangeAssets glTF material parent; no downloaded/paid plugin'],
        'allied_npc_selection':allied_selection,
        'german_npc_selection':{'policy':'ParisGermanGripPolicy','class_package':CLASS,'config_package':DATA,
            'graph_package':GRAPH,'config_payload_sha256':sha(CONFIG),'rifle_class_package':GUN,'rifle_mesh_package':GUNMESH,
            'human_selected':'Yupu,6 October2026; previous refined German V11 adopted as MVP baseline',
            'covers':'Three present and later compatible same-class/subclass Germans (TeamId1) in maps with policy',
            'holding_rules':42,'source_mesh_rig_weights_materials_actions_unchanged':True,
            'allied_first_person_ai_unchanged':True,'runtime_python_required':False,
            'deferred_visuals':'Straight right index, small stock overlap/self-contact; no zero-contact claim',
            'retired_experiments':'V12/V13 unselected; failure and recovery evidence preserved',
            'full_motion_recoil_lifecycle_nearwall_fps_shipping_second_machine':'not verified by adoption'},
        'verification':{'method':'Authenticated immutable SFTP object/manifest readback SHA-256 and size verified before Catalog selection',
            'native_selection':'Three Germans and later spawn bind accepted V11; owned cleanup; actual V2 guns NoCollision; bounded native walk/conserved reload/Ready; existing Allied/FP regression; ordinary -game without Python/bridge',
            'dependency_audit':'No missing hard dependencies; unchanged supplier soft gaps',
            'second_machine_test':'not performed','shipping_build':'not built'},
        'files':files,'file_count':len(files),'size_bytes':sum(f['size_bytes'] for f in files)}
    candidate=OUT/(AID+'.json');write(candidate,manifest)
    assert not (transport.SHARE/'releases'/RELEASE).exists()
    returned=OUT/'verified-manifest.json';remote=f'/releases/{RELEASE}/{AID}.json'
    transport.batch([f'mkdir "/releases/{RELEASE}"',f'put "{candidate.as_posix()}" "{remote}"',f'get "{remote}" "{returned.as_posix()}"'],'manifest')
    assert sha(candidate)==sha(returned)
    probe=OUT/'crud.txt';probe.write_text('German V11 approved publication CRUD probe\n',encoding='utf-8')
    remoteprobe=f'/releases/{RELEASE}/_crud_probe';returned=OUT/'crud-returned.txt'
    transport.batch([f'mkdir "{remoteprobe}"',f'put "{probe.as_posix()}" "{remoteprobe}/probe.txt"',
        f'put "{probe.as_posix()}" "{remoteprobe}/probe.txt"',f'rename "{remoteprobe}/probe.txt" "{remoteprobe}/renamed.txt"',
        f'get "{remoteprobe}/renamed.txt" "{returned.as_posix()}"',f'rm "{remoteprobe}/renamed.txt"',f'rmdir "{remoteprobe}"'],'crud')
    assert sha(probe)==sha(returned) and transport.idle_and_acl()==acl
    guards(True)
    status={'status':'verified_pending_catalog_selection','asset_id':AID,'release':RELEASE,'verified_at':now,
        'file_count':len(files),'size_bytes':manifest['size_bytes'],'uploaded_unique_objects':len(uploaded),
        'uploaded_bytes':sum(downloads[h][1]['size_bytes'] for h in uploaded),'reused_unique_objects':len(reused),
        'verified_unique_objects':len(downloads),'manifest_sha256':sha(candidate),'previous_manifest_sha256':sha(DEST),
        'root_acl_unchanged':True,'shared_account_crud':'create/update/rename/read/delete verified; exact probes removed',
        'external_connectivity':'not retested','teammate_test':'not performed'}
    write(OUT/'publication.json',status);print(json.dumps(status))

def patches():
    status=read(OUT/'publication.json');assert sha(DEST)==status['previous_manifest_sha256']
    candidate=OUT/(AID+'.json');assert sha(candidate)==status['manifest_sha256']
    catalog=read(ROOT/'Assets/Sync/CATALOG.json');entry=next(e for e in catalog['active_manifests'] if e['asset_id']==AID)
    entry.update(asset_version=RELEASE,sha256=sha(candidate),file_count=status['file_count'],size_bytes=status['size_bytes'],release_manifest=f'/releases/{RELEASE}/{AID}.json')
    catalog['updated_at']=status['verified_at']
    public={**status,'status':'verified_private_sftp_catalog_selected','git_publication':'pending; no commit/push requested',
        'teammate_guide':'Docs/Development/TEAM_PLAYTEST_ZH.md','source_runtime_test':'Docs/Development/GERMAN_NPC_FORMAL_V14_RESULT_20261006.md'}
    parts=[]
    for path,after in ((DEST,candidate.read_text()),(ROOT/'Assets/Sync/CATALOG.json',json.dumps(catalog,indent=2)+'\n'),
            (ROOT/'Assets/Sync/NATIVE_PLAYTEST_PUBLICATION_STATUS.json',json.dumps(public,indent=2)+'\n')):
        diff=list(difflib.unified_diff(path.read_text(encoding='utf-8-sig').splitlines(),after.splitlines(),n=3))[2:]
        groups=[];current=[]
        for line in diff:
            if line.startswith('@@'):
                if current:groups.append(current)
                current=['@@']
            else:current.append(line)
        if current:groups.append(current)
        # Hunk boundaries are indivisible; generated manifest additions are one block.
        for group in groups:
            parts.append('\n'.join(['*** Begin Patch','*** Update File: '+path.as_posix(),*group,'*** End Patch'])+'\n')
    write(OUT/'patches.json',{'parts':parts});print(json.dumps({'parts':len(parts),'largest_lines':max(len(p.splitlines()) for p in parts)}))

def normalize():
    candidate=OUT/(AID+'.json');status=read(OUT/'publication.json')
    assert read(DEST)==read(candidate)
    original=DEST.read_bytes();formatted=original.replace(b'\r\n',b'\n').replace(b'\n',b'\r\n')
    assert hashlib.sha256(formatted).hexdigest()==status['manifest_sha256']
    DEST.write_bytes(formatted);assert sha(DEST)==sha(candidate)
    write(OUT/'format_verification.json',{'semantic_changes':False,'published_crlf_bytes_exact':True})

def finalize():
    status=read(OUT/'publication.json');assert sha(DEST)==status['manifest_sha256']
    selection=next(e for e in read(ROOT/'Assets/Sync/CATALOG.json')['active_manifests'] if e['asset_id']==AID)
    assert selection['sha256']==sha(DEST) and selection['asset_version']==RELEASE
    manifest=read(DEST);assert all(exact(f) for f in manifest['files'])
    pre=read(BASE/'preflight/result.json')
    allowed={MAP.resolve(),(ROOT/'Assets/Sync/CATALOG.json').resolve()}
    allowed.update((ROOT/f['path']).resolve() for f in pre['binary_files'])
    assert all(exact(f) or (ROOT/f['path']).resolve() in allowed for f in pre['guards'])
    assert exact(pre['descriptor']) and all(exact(f) for f in pre['baseline_files'])
    paths=dict.fromkeys(f['path'] for f in pre['guards']+manifest['files'])
    rows=[row(ROOT/p) for p in paths]
    write(BASE/'selected_v1/result.json',{'status':'formal_german_v11_with_rifle_and_private_sftp_verified',
        'files':rows,'file_count':len(rows),'manifest_sha256':sha(DEST),'release':RELEASE,
        'human_selection':'Previous refined V11 as MVP visual baseline by Yupu,6 October',
        'historical_guards_preserved':True,'source_dependencies_deleted':False,'git_commit_push':'not requested/not performed'})
    removed=0
    for f in manifest['files']:
        sample=OUT/'verified-downloads'/f['sha256']
        if sample.exists():transport.verify(sample,f);sample.unlink();removed+=1
    write(OUT/'final.json',{**status,'status':'formal_german_v11_with_rifle_and_private_sftp_verified',
        'removed_verified_temporary_samples':removed})
    print(json.dumps({'status':'formal_german_v11_with_rifle_and_private_sftp_verified','guard_count':len(rows),'removed_verified_temporary_samples':removed}))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['publish','patches','part','normalize','finalize']);parser.add_argument('--part',type=int,default=0)
    args=parser.parse_args()
    if args.mode=='publish':publish()
    elif args.mode=='patches':patches()
    elif args.mode=='part':print(read(OUT/'patches.json')['parts'][args.part],end='')
    elif args.mode=='normalize':normalize()
    else:finalize()
