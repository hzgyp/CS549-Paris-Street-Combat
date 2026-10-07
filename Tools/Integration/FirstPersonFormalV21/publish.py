"""Publish the human-approved first-person selection as verified immutable SFTP objects.

The old one-time publisher is never invoked. Only its authenticated transport,
byte verification and idle/ACL helpers are reused under this new identity.
"""
import argparse
import difflib
import importlib.util
from datetime import datetime
from formal_common import *

RELEASE = 'paris-native-playtest-20261005-fp-v20'
AID = 'paris-gameplay-native-playtest'
OUT = BASE/'publication_v1'
DEST = ROOT/'Assets/Sync/manifests/paris-gameplay-native-playtest.json'
spec = importlib.util.spec_from_file_location('previous_transport',ROOT/'Tools/Integration/publish_native_playtest.py')
transport = importlib.util.module_from_spec(spec); spec.loader.exec_module(transport)
transport.OUT = OUT


def publish():
    assert not OUT.exists(),'Preserve occupied publication identity'
    acl = transport.idle_and_acl()
    guards = check_protected(True); assert not guards['mismatches'],guards
    fresh = read(BASE/'fresh_v2/result.json')
    assert fresh['status']=='passed_fresh_saved_native_regression' and not fresh['errors']
    assert read(BASE/'ordinary_game_v1/result.json')['status']=='passed_ordinary_saved_game_native_auto_bind'
    assert read(BASE/'fresh_v2/image_review.json')['actual_all_views_inspected']
    author = read(BASE/'author_v1/result.json'); assert all(exact(f) for f in author['saved_files'])
    assert read(BASE/'author_guard_verification_v2/result.json')['status']=='passed_authorized_exact_map_alias_only'
    audit = read(BASE/'audit_v1/result.json')
    assert audit['status'].startswith('passed_saved_dependency_closure') and not audit['errors'] and not audit['hard_missing_packages']
    old = read(DEST)
    assert audit['missing_referencers']==old['known_vendor_soft_reference_gaps'],'Unknown new supplier gap'
    assert all(p.startswith(('/Engine/','/Script/','/ACLPlugin/','/Niagara/','/MeshModelingToolsetExp/')) for p in audit['external_dependencies'])
    catalog = read(ROOT/'Assets/Sync/CATALOG.json')
    selected = next(e for e in catalog['active_manifests'] if e['asset_id']==AID)
    assert sha(DEST)==selected['sha256']
    city = {f['path']:f for f in read(ROOT/'Assets/Sync/manifests/france-liberation-content.json')['files']}
    others = {f['path'] for e in catalog['active_manifests'] if e['asset_id']!=AID
        for f in read(ROOT/e['path'])['files']}
    files=[]
    for item in audit['files']:
        if item['path'] in city:
            assert item['sha256']==city[item['path']]['sha256'],item['path']
            assert (ROOT/item['path']).stat().st_size==item['size_bytes'],item['path']
            continue
        assert exact(item),item['path']
        assert item['path'] not in others,item['path']
        files.append(item)
    files += [row(PLUGIN/'Binaries/Win64'/name) for name in ('UnrealEditor-ParisGripBindingV18.dll','UnrealEditor.modules')]
    assert len({f['path'] for f in files})==len(files)
    files = [{**f,'storage':'sftp','remote_path':f"/objects/sha256/{f['sha256'][:2]}/{f['sha256']}"} for f in sorted(files,key=lambda f:f['path'])]
    OUT.mkdir(parents=True)
    write(OUT/'started.json',{'release':RELEASE,'previous_manifest_sha256':sha(DEST),'root_acl_sha256':hashlib.sha256(acl.encode()).hexdigest()})
    commands=[f'mkdir "/incoming/{RELEASE}"'];prefixes=set();downloads={};uploaded=[];reused=[]
    for f in files:
        h=f['sha256']
        if h in downloads:continue
        final=transport.SHARE/f['remote_path'].lstrip('/')
        if final.exists():reused.append(h)
        else:
            if h[:2] not in prefixes and not final.parent.exists():commands.append(f'mkdir "/objects/sha256/{h[:2]}"')
            prefixes.add(h[:2]);stage=f'/incoming/{RELEASE}/{h}.part'
            commands += [f'put "{(ROOT/f["path"]).as_posix()}" "{stage}"',f'rename "{stage}" "{f["remote_path"]}"'];uploaded.append(h)
        dest=OUT/'verified-downloads'/h;dest.parent.mkdir(parents=True,exist_ok=True)
        downloads[h]=(dest,f);commands.append(f'get "{f["remote_path"]}" "{dest.as_posix()}"')
    commands.append(f'rmdir "/incoming/{RELEASE}"');transport.batch(commands,'objects')
    for dest,f in downloads.values():transport.verify(dest,f);assert exact(f)
    now=datetime.now().astimezone().isoformat()
    manifest={**old,'asset_version':RELEASE,'published_at':now,
        'scope':'Human-approved V20 first-person display; private UE5.8.2 editor playtest, not complete action/FPS/MVP or Shipping acceptance',
        'source':'Fresh saved-map hard/soft closure plus approved first-person native runtime module',
        'runtime_plugins':['UE5.8.2 bundled ACLPlugin/Niagara/MeshModelingToolsetExp','ParisGripBindingV18 approved native display; Win64 editor module supplied by this manifest; generic source in Git'],
        'runtime_python_required':False,'runtime_editor_bridge_required':False,
        'first_person_selection':{'actor':'ParisFirstPersonApprovedActor','config_package':PACKAGE,
            'config_payload_sha256':CONFIG_SHA,'human_approved':'Yupu, 5 October 2026',
            'plan':'Docs/Development/FIRST_PERSON_FORMAL_V21_20261005.md','source_reload_unchanged':True,
            'sleeves':'known/deferred','full_return_lifecycle_nearwall_fps_shipping':'not accepted by this adoption'},
        'retired_paths':[{'path':f['path'],'reason':'No longer reachable from selected map; retain locally pending separate reference/recovery review'}
            for f in old['files'] if f['path'] not in {e['path'] for e in files}],
        'verification':{'method':'All final immutable objects and manifest authenticated SFTP download/SHA-256/size verified before Catalog selection',
            'dependency_audit':'No missing hard dependencies; unchanged five supplier soft gaps recorded',
            'native_selection':'Fresh saved map auto-binds without Python preparation; short left movement and one conserved original reload observed',
            'second_machine_test':'not performed','shipping_build':'not built'},
        'files':files,'file_count':len(files),'size_bytes':sum(f['size_bytes'] for f in files)}
    write(OUT/(AID+'.json'),manifest)
    remote=f'/releases/{RELEASE}/{AID}.json';returned=OUT/'verified-manifest.json'
    assert not (transport.SHARE/'releases'/RELEASE).exists()
    transport.batch([f'mkdir "/releases/{RELEASE}"',f'put "{(OUT/(AID+".json")).as_posix()}" "{remote}"',
        f'get "{remote}" "{returned.as_posix()}"'],'manifest')
    assert sha(returned)==sha(OUT/(AID+'.json'))
    probe=OUT/'crud.txt';probe.write_text('Approved FP publication CRUD probe\n',encoding='utf-8')
    remoteprobe=f'/releases/{RELEASE}/_crud_probe';returnedprobe=OUT/'crud-returned.txt'
    transport.batch([f'mkdir "{remoteprobe}"',f'put "{probe.as_posix()}" "{remoteprobe}/probe.txt"',
        f'put "{probe.as_posix()}" "{remoteprobe}/probe.txt"',f'rename "{remoteprobe}/probe.txt" "{remoteprobe}/renamed.txt"',
        f'get "{remoteprobe}/renamed.txt" "{returnedprobe.as_posix()}"',f'rm "{remoteprobe}/renamed.txt"',f'rmdir "{remoteprobe}"'],'crud')
    assert sha(probe)==sha(returnedprobe) and transport.idle_and_acl()==acl
    assert not check_protected(True)['mismatches'] and all(exact(f) for f in files)
    status={'status':'verified_pending_catalog_selection','release':RELEASE,'asset_id':AID,
        'file_count':len(files),'size_bytes':manifest['size_bytes'],'uploaded_unique_objects':len(uploaded),
        'uploaded_bytes':sum(downloads[h][1]['size_bytes'] for h in uploaded),'reused_unique_objects':len(reused),
        'verified_unique_objects':len(downloads),'manifest_sha256':sha(OUT/(AID+'.json')),
        'root_acl_unchanged':True,'shared_account_crud':'create/update/rename/read/delete verified; exact probes removed',
        'previous_manifest_sha256':sha(DEST),'external_connectivity':'not retested','teammate_test':'not performed','verified_at':now}
    write(OUT/'publication.json',status);print(json.dumps(status))


def patch():
    status=read(OUT/'publication.json');assert status['status']=='verified_pending_catalog_selection'
    assert sha(DEST)==status['previous_manifest_sha256']
    src=OUT/(AID+'.json');assert sha(src)==status['manifest_sha256']
    manifest=read(src);catalog=read(ROOT/'Assets/Sync/CATALOG.json')
    entry=next(e for e in catalog['active_manifests'] if e['asset_id']==AID)
    assert entry['sha256']==status['previous_manifest_sha256']
    entry.update(asset_version=RELEASE,sha256=sha(src),file_count=manifest['file_count'],size_bytes=manifest['size_bytes'],release_manifest=f'/releases/{RELEASE}/{AID}.json')
    catalog['updated_at']=status['verified_at']
    replacements={DEST:src.read_text(),ROOT/'Assets/Sync/CATALOG.json':json.dumps(catalog,indent=2)+'\n'}
    public_status={**status,'status':'verified_private_sftp_catalog_selected',
        'git_publication':'pending; no commit/push requested this turn',
        'teammate_guide':'Docs/Development/TEAM_PLAYTEST_ZH.md',
        'source_runtime_test':'Docs/Development/FIRST_PERSON_FORMAL_V21_RESULT_20261005.md'}
    replacements[ROOT/'Assets/Sync/NATIVE_PLAYTEST_PUBLICATION_STATUS.json']=json.dumps(public_status,indent=2)+'\n'
    print('*** Begin Patch')
    for path,content in replacements.items():
        print('*** Update File: '+path.as_posix())
        delta=list(difflib.unified_diff(path.read_text(encoding='utf-8-sig').splitlines(),content.splitlines(),n=3))
        for line in delta[2:]:
            if line.startswith('@@'):print('@@')
            else:print(line)
    print('*** End Patch')


def patch_init():
    """Bounded apply_patch inputs; never truncate/overwrite the selected JSON."""
    status=read(OUT/'publication.json');assert sha(DEST)==status['previous_manifest_sha256']
    candidate=OUT/(AID+'.json');assert sha(candidate)==status['manifest_sha256']
    assert not (OUT/'patch_set_v2.json').exists(),'Preserve patch-set identity'
    old=read(DEST);new=read(candidate);by_path={f['path']:f for f in new['files']}
    current=DEST.read_text(encoding='utf-8-sig');parts=[];sections=[]
    def block(item):return '\n'.join('    '+line for line in json.dumps(item,indent=2).splitlines())
    def wrap(lines):return '\n'.join(['*** Begin Patch','*** Update File: '+DEST.as_posix(),*lines,'*** End Patch'])+'\n'
    for index,item in enumerate(old['files']):
        assert item['path'] in by_path,'Retired record needs separate reviewed patch'
        suffix=',' if index<len(old['files'])-1 else ''
        before=block(item)+suffix;after=block(by_path[item['path']])+suffix
        assert current.count(before)==1,item['path']
        if before==after:continue
        sections += ['@@',*['-'+line for line in before.splitlines()],*['+'+line for line in after.splitlines()]]
        current=current.replace(before,after,1)
        if len(sections)>240:parts.append(wrap(sections));sections=[]
    if sections:parts.append(wrap(sections))
    # Records now use candidate order/values. Remaining new entries/header changes
    # fit one bounded diff; Catalog/status remain untouched until this final part.
    catalog=read(ROOT/'Assets/Sync/CATALOG.json');entry=next(e for e in catalog['active_manifests'] if e['asset_id']==AID)
    assert entry['sha256']==status['previous_manifest_sha256']
    entry.update(asset_version=RELEASE,sha256=sha(candidate),file_count=new['file_count'],size_bytes=new['size_bytes'],release_manifest=f'/releases/{RELEASE}/{AID}.json')
    catalog['updated_at']=status['verified_at']
    public_status={**status,'status':'verified_private_sftp_catalog_selected','git_publication':'pending; no commit/push requested this turn',
        'teammate_guide':'Docs/Development/TEAM_PLAYTEST_ZH.md','source_runtime_test':'Docs/Development/FIRST_PERSON_FORMAL_V21_RESULT_20261005.md'}
    replacements=[(DEST,current,candidate.read_text()),(ROOT/'Assets/Sync/CATALOG.json',(ROOT/'Assets/Sync/CATALOG.json').read_text(encoding='utf-8-sig'),json.dumps(catalog,indent=2)+'\n'),
        (ROOT/'Assets/Sync/NATIVE_PLAYTEST_PUBLICATION_STATUS.json',(ROOT/'Assets/Sync/NATIVE_PLAYTEST_PUBLICATION_STATUS.json').read_text(encoding='utf-8-sig'),json.dumps(public_status,indent=2)+'\n')]
    lines=['*** Begin Patch']
    for path,before,after in replacements:
        lines.append('*** Update File: '+path.as_posix())
        for line in list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:]:lines.append('@@' if line.startswith('@@') else line)
    lines.append('*** End Patch');parts.append('\n'.join(lines)+'\n')
    write(OUT/'patch_set_v2.json',{'parts':parts,'target_manifest_sha256':sha(candidate)})
    print(json.dumps({'parts':len(parts),'target_manifest_sha256':sha(candidate)}))


def patch_part():
    data=read(OUT/'patch_set_v2.json');assert data['target_manifest_sha256']==read(OUT/'publication.json')['manifest_sha256']
    print(data['parts'][args.part],end='')


def finalize():
    status=read(OUT/'publication.json');assert sha(DEST)==status['manifest_sha256']
    entry=next(e for e in read(ROOT/'Assets/Sync/CATALOG.json')['active_manifests'] if e['asset_id']==AID)
    assert entry['sha256']==sha(DEST) and entry['asset_version']==RELEASE
    manifest=read(DEST);assert all(exact(f) for f in manifest['files'])
    rows=guarded_rows()
    rows=[row(ROOT/f['path']) for f in rows]
    rows += [row(ROOT/f['path']) for f in manifest['files'] if f['path'] not in {e['path'] for e in rows}]
    write(BASE/'selected_v1/result.json',{'status':'formal_native_selection_and_private_sftp_verified','files':rows,
        'file_count':len(rows),'manifest_sha256':sha(DEST),'release':RELEASE,'historical_guards_preserved':True,
        'human_acceptance':'current first-person appearance','remaining_gates':['sleeves_deferred','full_return','lifecycle','near_wall','fps','shipping','second_machine'],
        'git_commit_push':'not requested/not performed'})
    # Only exact disposable authenticated transfer samples, not asset/recovery backups.
    removed=0
    for f in manifest['files']:
        sample=OUT/'verified-downloads'/f['sha256']
        if sample.exists():transport.verify(sample,f);sample.unlink();removed+=1
    write(OUT/'final.json',{**status,'status':'formal_native_selection_and_private_sftp_verified','removed_verified_temporary_samples':removed})
    print(json.dumps({'status':'formal_native_selection_and_private_sftp_verified','guard_count':len(rows),'removed_verified_temporary_samples':removed}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=('publish','patch','patch_init','patch_part','finalize'))
    parser.add_argument('--part',type=int,default=0);args=parser.parse_args()
    globals()[args.mode]()
