"""Fresh bridge-disabled native draft/class/mode/default/dependency verification."""
import hashlib
import json
import re
import traceback
from pathlib import Path
import unreal

ROOT=Path(__file__).resolve().parents[2]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
command=unreal.SystemLibrary.get_command_line()
stride='-ParisStride=true' in command
identity=re.search(r'-ParisReopenIdentity=(\w+)(?:\s|$)',command)
DEST=STORE/('Evidence/P2/Lifecycle/'+(identity.group(1) if identity else 'fresh_reopen_v1')+'.json')
if DEST.exists():
    raise RuntimeError('Refusing existing fresh-load report')
report={'engine':unreal.SystemLibrary.get_engine_version(),'assets':[],'actors':[],'errors':[]}
try:
    assert not hasattr(unreal,'ParisBlueprintAuthoring'), 'Bridge must be disabled'
    registry=unreal.AssetRegistryHelpers.get_asset_registry()
    dep=unreal.AssetRegistryDependencyOptions(include_hard_package_references=True,include_soft_package_references=True)
    authored=[json.loads((STORE/p).read_text(encoding='utf-8')) for p in (
        'Evidence/P2/Retarget/directional_author_v1.json','Evidence/P2/Lifecycle/authoring_v1.json')]
    if stride:
        authored += [json.loads((STORE/p).read_text(encoding='utf-8')) for p in (
            'Evidence/P2/Retarget/stride_author_v1.json','Evidence/P2/Lifecycle/stride_scene_v1.json')]
    for author in authored:
        assert not author.get('errors')
        for path in author['assets']:
            package=path.split('.')[0]
            asset=unreal.load_asset(path)
            assert asset, path
            deps=[str(x) for x in registry.get_dependencies(package,dep)]
            assert not any('ParisEditorBridge' in x for x in deps), deps
            if isinstance(asset,unreal.Blueprint):
                unreal.BlueprintEditorLibrary.compile_blueprint(asset)
                assert asset.generated_class(), path
            item={'path':package,'dependencies':deps}
            if isinstance(asset,unreal.Skeleton) and 'Translation' in path:
                # Runtime reference/mode inspection is separately measured in
                # each fresh v5 process; this bridge-disabled pass checks identity.
                item['mode_evidence']='Evidence/P2/Movement/movement_probe_v5_German_A_60.json'
                mode=json.loads((STORE/item['mode_evidence']).read_text(encoding='utf-8'))
                ref=next(m for m in mode['references'] if 'SK_PC_German_A_Translation' in m['mesh'])
                item['translation_modes']={b['name']:b['translation_retarget_mode'] for b in ref['bones'] if b['name'] in ('root','pelvis')}
                assert item['translation_modes']=={'root':0,'pelvis':0} and ref['skeleton']==asset.get_path_name()
            report['assets'].append(item)
        for f in author['files']:
            p=STORE/'Content'/f['path']
            assert p.stat().st_size==f['size'] and hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256'], f['path']
    author=authored[-1] if stride else authored[1]
    assert unreal.EditorLevelLibrary.load_level(author['map'])
    expected={a['label']:a for a in author['actors']}
    for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        if a.get_actor_label() not in expected:
            continue
        e=expected[a.get_actor_label()]
        m=a.get_component_by_class(unreal.SkeletalMeshComponent)
        assert a.get_class().get_path_name()==e['class'] and m.get_skinned_asset().get_path_name().split('.')[0]==e['mesh']
        if 'anim_class' in e:
            assert m.get_editor_property('anim_class').get_path_name()==e['anim_class']
        assert a.get_editor_property('Health')==100 and not a.get_editor_property('IsDead')
        report['actors'].append({'label':a.get_actor_label(),'class':a.get_class().get_path_name(),
            'mesh':m.get_skinned_asset().get_path_name(),'animation':m.get_editor_property('anim_class').get_path_name(),
            'health':a.get_editor_property('Health'),'team':a.get_editor_property('TeamId')})
    assert len(report['actors'])==6
    report['result']='pass_fresh_bridge_disabled'
except Exception:
    report['errors'].append(traceback.format_exc())
    report['result']='fail'
DEST.write_text(json.dumps(report,indent=2),encoding='utf-8')
assert not report['errors'], report['errors']
unreal.log('CS549_DIRECTIONAL_LIFECYCLE_REOPEN_DONE')
