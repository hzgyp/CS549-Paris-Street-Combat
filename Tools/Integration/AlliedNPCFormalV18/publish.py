"""Adoption-specific immutable publication and bounded metadata patches."""
import argparse,difflib
from datetime import datetime
from common import *

RELEASE='paris-native-playtest-20261006-allied-grip-v16'
AID='paris-gameplay-native-playtest'
OUT=BASE/'publication_v1'
DEST=ROOT/'Assets/Sync/manifests/paris-gameplay-native-playtest.json'
spec=importlib.util.spec_from_file_location('allied_transport',ROOT/'Tools/Integration/publish_native_playtest.py')
transport=importlib.util.module_from_spec(spec);spec.loader.exec_module(transport);transport.OUT=OUT

def publish():
    assert not OUT.exists(),'Preserve occupied publication'
    acl=transport.idle_and_acl();guards(True,True)
    for name in ('early_v2','fresh_v1'):
        proof=read(BASE/name/'result.json')
        assert proof['status']=='passed_two_allies_and_future_native_binding' and not proof['errors']
        assert read(BASE/name/'image_review.json')['both_native_views_inspected']
    game_log=ROOT/'tmp/allied-npc-formal-v18/ordinary_game_v1.log'
    receipt=read(Path(str(game_log)+'.exit.json'))
    assert receipt['exit_code']==0
    text=game_log.read_text(encoding='utf-8-sig',errors='replace')
    assert text.count('PARIS_ALLIED_GRIP_READY')==2 and 'PARIS_ALLIED_GRIP_FAILURE' not in text
    author=read(BASE/'author_v1/result.json');assert not author['errors'] and all(exact(f) for f in author['saved_files'])
    audit=read(BASE/'audit_v1/result.json')
    assert audit['status']=='passed_saved_dependency_closure' and not audit['errors'] and not audit['hard_missing_packages']
    old=read(DEST);assert audit['missing_referencers']==old['known_vendor_soft_reference_gaps'],'Unexpected dependency gap'
    catalog=read(ROOT/'Assets/Sync/CATALOG.json')
    selected=next(e for e in catalog['active_manifests'] if e['asset_id']==AID)
    assert selected['sha256']==sha(DEST)
    city={f['path']:f for f in read(ROOT/'Assets/Sync/manifests/france-liberation-content.json')['files']}
    others={f['path'] for e in catalog['active_manifests'] if e['asset_id']!=AID for f in read(ROOT/e['path'])['files']}
    files=[]
    for item in audit['files']:
        if item['path'] in city:
            assert item['sha256']==city[item['path']]['sha256'];continue
        assert exact(item) and item['path'] not in others;files.append(item)
    for folder,names in ((ROOT/'Unreal/ParisStreetCombat/Plugins/ParisGripBindingV18/Binaries/Win64',
                         ('UnrealEditor-ParisGripBindingV18.dll','UnrealEditor.modules')),
                        (PLUGIN/'Binaries/Win64',('UnrealEditor-ParisNPCGripV15.dll','UnrealEditor-ParisNPCGripV15Editor.dll','UnrealEditor.modules'))):
        files.extend(row(folder/name) for name in names)
    assert len({f['path'] for f in files})==len(files)
    files=[{**f,'storage':'sftp','remote_path':f"/objects/sha256/{f['sha256'][:2]}/{f['sha256']}"} for f in sorted(files,key=lambda f:f['path'])]
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
    manifest={**old,'asset_version':RELEASE,'published_at':now,
        'scope':'Human-approved FP V20 and all standard Allied NPC V16 grips; private UE5.8.2 editor playtest, not complete motion/FPS/MVP/Shipping acceptance',
        'source':'Fresh saved-map closure and both native display modules; current authorized shared combatant revision retained',
        'runtime_plugins':old['runtime_plugins']+['ParisNPCGripV15 native Allied policy and existing-pose adapter; Win64 editor/runtime module bytes supplied; generic source in Git'],
        'allied_npc_selection':{'policy':'ParisAlliedGripPolicy','class_package':CLASS,'config_package':DATA,
            'graph_package':GRAPH,'config_payload_sha256':sha(CONFIG),'human_approved':'Yupu,6 October2026',
            'covers':'Both existing and later same-class/subclass Allied NPCs in maps with the policy',
            'source_mesh_rig_weights_materials_actions_unchanged':True,'player_german_ai_unchanged':True,
            'old_grip':'Unselected presentation; original dependencies/recovery history retained',
            'full_motion_recoil_lifecycle_nearwall_fps_shipping_second_machine':'not verified by adoption'},
        'retired_paths':[{'path':f['path'],'reason':'No longer map-reachable; retain originals/history pending separate recovery audit'} for f in old['files'] if f['path'] not in {i['path'] for i in files}],
        'verification':{'method':'Authenticated immutable SFTP object/manifest readback SHA-256 and size verified before Catalog selection',
            'native_selection':'Both existing Allies and later spawn bind accepted V16; destroy cleanup; ordinary saved -game without Python/bridge',
            'dependency_audit':'No missing hard dependencies; unchanged supplier soft gaps',
            'second_machine_test':'not performed','shipping_build':'not built'},
        'files':files,'file_count':len(files),'size_bytes':sum(f['size_bytes'] for f in files)}
    candidate=OUT/(AID+'.json');write(candidate,manifest)
    assert not (transport.SHARE/'releases'/RELEASE).exists()
    remote=f'/releases/{RELEASE}/{AID}.json';returned=OUT/'verified-manifest.json'
    transport.batch([f'mkdir "/releases/{RELEASE}"',f'put "{candidate.as_posix()}" "{remote}"',f'get "{remote}" "{returned.as_posix()}"'],'manifest')
    assert sha(candidate)==sha(returned)
    probe=OUT/'crud.txt';probe.write_text('Allied approved publication CRUD probe\n',encoding='utf-8')
    remoteprobe=f'/releases/{RELEASE}/_crud_probe';probe_returned=OUT/'crud-returned.txt'
    transport.batch([f'mkdir "{remoteprobe}"',f'put "{probe.as_posix()}" "{remoteprobe}/probe.txt"',
        f'put "{probe.as_posix()}" "{remoteprobe}/probe.txt"',f'rename "{remoteprobe}/probe.txt" "{remoteprobe}/renamed.txt"',
        f'get "{remoteprobe}/renamed.txt" "{probe_returned.as_posix()}"',f'rm "{remoteprobe}/renamed.txt"',f'rmdir "{remoteprobe}"'],'crud')
    assert sha(probe)==sha(probe_returned) and transport.idle_and_acl()==acl
    guards(True,True)
    status={'status':'verified_pending_catalog_selection','asset_id':AID,'release':RELEASE,'verified_at':now,
        'file_count':len(files),'size_bytes':manifest['size_bytes'],'uploaded_unique_objects':len(uploaded),
        'uploaded_bytes':sum(downloads[h][1]['size_bytes'] for h in uploaded),'reused_unique_objects':len(reused),
        'verified_unique_objects':len(downloads),'manifest_sha256':sha(candidate),'previous_manifest_sha256':sha(DEST),
        'root_acl_unchanged':True,'shared_account_crud':'create/update/rename/read/delete verified; exact probes removed',
        'external_connectivity':'not retested','teammate_test':'not performed'}
    write(OUT/'publication.json',status);print(json.dumps(status))

def patch_init():
    status=read(OUT/'publication.json');assert sha(DEST)==status['previous_manifest_sha256']
    candidate=OUT/(AID+'.json');assert sha(candidate)==status['manifest_sha256']
    assert not (OUT/'patches.json').exists()
    old=read(DEST);new=read(candidate);by_path={f['path']:f for f in new['files']}
    current=DEST.read_text(encoding='utf-8-sig');parts=[]
    def block(item):return '\n'.join('    '+line for line in json.dumps(item,indent=2).splitlines())
    for index,item in enumerate(old['files']):
        assert item['path'] in by_path,'Review retired path separately'
        suffix=',' if index<len(old['files'])-1 else ''
        before=block(item)+suffix;after=block(by_path[item['path']])+suffix
        assert current.count(before)==1,item['path']
        if before==after:continue
        lines=['*** Begin Patch','*** Update File: '+DEST.as_posix(),'@@',
            *['-'+line for line in before.splitlines()],*['+'+line for line in after.splitlines()],'*** End Patch']
        parts.append('\n'.join(lines)+'\n');current=current.replace(before,after,1)
    catalog=read(ROOT/'Assets/Sync/CATALOG.json');entry=next(e for e in catalog['active_manifests'] if e['asset_id']==AID)
    entry.update(asset_version=RELEASE,sha256=sha(candidate),file_count=new['file_count'],size_bytes=new['size_bytes'],release_manifest=f'/releases/{RELEASE}/{AID}.json')
    catalog['updated_at']=status['verified_at']
    public_status={**status,'status':'verified_private_sftp_catalog_selected','git_publication':'pending; no commit/push requested',
        'teammate_guide':'Docs/Development/TEAM_PLAYTEST_ZH.md','source_runtime_test':'Docs/Development/ALLIED_NPC_FORMAL_V18_RESULT_20261006.md'}
    replacements=[(DEST,current,candidate.read_text()),(ROOT/'Assets/Sync/CATALOG.json',(ROOT/'Assets/Sync/CATALOG.json').read_text(encoding='utf-8-sig'),json.dumps(catalog,indent=2)+'\n'),
        (ROOT/'Assets/Sync/NATIVE_PLAYTEST_PUBLICATION_STATUS.json',(ROOT/'Assets/Sync/NATIVE_PLAYTEST_PUBLICATION_STATUS.json').read_text(encoding='utf-8-sig'),json.dumps(public_status,indent=2)+'\n')]
    lines=['*** Begin Patch']
    for path,before,after in replacements:
        lines.append('*** Update File: '+path.as_posix())
        for line in list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:]:lines.append('@@' if line.startswith('@@') else line)
    lines.append('*** End Patch');parts.append('\n'.join(lines)+'\n')
    write(OUT/'patches.json',{'parts':parts});print(json.dumps({'parts':len(parts)}))

def finalize():
    status=read(OUT/'publication.json');assert sha(DEST)==status['manifest_sha256']
    entry=next(e for e in read(ROOT/'Assets/Sync/CATALOG.json')['active_manifests'] if e['asset_id']==AID)
    assert entry['sha256']==sha(DEST) and entry['asset_version']==RELEASE
    manifest=read(DEST);assert all(exact(f) for f in manifest['files'])
    pre=read(BASE/'preflight/result.json');allowed={MAP.resolve(),(ROOT/'Assets/Sync/CATALOG.json').resolve()}
    assert all(exact(f) or (ROOT/f['path']).resolve() in allowed for f in pre['guards'])
    rows=[row(ROOT/f['path']) for f in pre['guards']]
    paths={f['path'] for f in rows}
    rows.extend(row(ROOT/f['path']) for f in manifest['files'] if f['path'] not in paths)
    rows.append(row(DESCRIPTOR))
    write(BASE/'selected_v1/result.json',{'status':'formal_allied_native_selection_and_private_sftp_verified',
        'files':rows,'file_count':len(rows),'manifest_sha256':sha(DEST),'release':RELEASE,
        'human_acceptance':'Current Allied V16 appearance/preview by Yupu,6 October',
        'historical_guards_preserved':True,'source_model_dependencies_deleted':False,'git_commit_push':'not requested/not performed'})
    removed=0
    for f in manifest['files']:
        sample=OUT/'verified-downloads'/f['sha256']
        if sample.exists():transport.verify(sample,f);sample.unlink();removed+=1
    write(OUT/'final.json',{**status,'status':'formal_allied_native_selection_and_private_sftp_verified','removed_verified_temporary_samples':removed})
    print(json.dumps({'status':'formal_allied_native_selection_and_private_sftp_verified','guard_count':len(rows),'removed_verified_temporary_samples':removed}))

def normalize():
    # Formatting-only exception: do not change any published semantic value.
    status=read(OUT/'publication.json');candidate=OUT/(AID+'.json')
    assert read(DEST)==read(candidate) and sha(candidate)==status['manifest_sha256']
    original=DEST.read_bytes();formatted=original.replace(b'\r\n',b'\n').replace(b'\n',b'\r\n')
    assert hashlib.sha256(formatted).hexdigest()==status['manifest_sha256']
    DEST.write_bytes(formatted);assert sha(DEST)==status['manifest_sha256']
    write(OUT/'format_verification.json',{'semantic_changes':False,'published_manifest_bytes_exact':True})
    print('Exact published CRLF manifest bytes; formatting only')

def group_patches():
    original=read(OUT/'patches.json')['parts'];parts=[];hunks=[];lines=0
    assert not (OUT/'patches_v2.json').exists()
    for part in original[:-1]:
        body=part.splitlines()[2:-1]
        assert body[0]=='@@'
        hunks.extend(body);lines+=len(body)
        if lines>=240:
            parts.append('\n'.join(['*** Begin Patch','*** Update File: '+DEST.as_posix(),*hunks,'*** End Patch'])+'\n')
            hunks=[];lines=0
    if hunks:parts.append('\n'.join(['*** Begin Patch','*** Update File: '+DEST.as_posix(),*hunks,'*** End Patch'])+'\n')
    parts.append(original[-1]);write(OUT/'patches_v2.json',{'parts':parts})
    print(json.dumps({'parts':len(parts),'original_parts':len(original),'reason':'Field-order formatting grouped; verified values unchanged'}))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['publish','patch-init','group-patches','part','normalize','finalize']);parser.add_argument('--part',type=int,default=0)
    args=parser.parse_args()
    if args.mode=='publish':publish()
    elif args.mode=='patch-init':patch_init()
    elif args.mode=='group-patches':group_patches()
    elif args.mode=='part':print(read(OUT/'patches_v2.json')['parts'][args.part],end='')
    elif args.mode=='normalize':normalize()
    else:finalize()
