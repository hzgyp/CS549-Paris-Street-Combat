"""New-only shared health/death/reset graphs and separate six-Character test map."""
import hashlib
import json
import traceback
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT = STORE / 'Evidence/P2/Lifecycle'
OUT.mkdir(exist_ok=True)
stride = '-ParisStrideScene=true' in unreal.SystemLibrary.get_command_line()
DEST = OUT / ('stride_scene_v1.json' if stride else 'authoring_v1.json')
MAP = '/Game/ParisCombat/Tests/Integration/' + ('P2_CharacterStride_20261001' if stride else 'P2_CharacterLifecycle_20261001')
if DEST.exists() or unreal.EditorAssetLibrary.does_asset_exist(MAP):
    raise RuntimeError('Preserve prior drafts/evidence; no overwrite')
report = {'engine': unreal.SystemLibrary.get_engine_version(), 'assets': [], 'actors': [], 'errors': []}
def checkpoint():
    DEST.write_text(json.dumps(report, indent=2), encoding='utf-8')
checkpoint()
try:
    bridge = {'assets':[],'compiler_messages':[]} if stride else json.loads(unreal.ParisBlueprintAuthoring.create_lifecycle_draft())
    assert 'error' not in bridge, bridge
    report['compiler_messages'] = bridge['compiler_messages']
    for path in bridge['assets']:
        assert unreal.EditorAssetLibrary.save_loaded_asset(unreal.load_asset(path), only_if_is_dirty=False)
        report['assets'].append(path)
    checkpoint()
    assert unreal.EditorLevelLibrary.new_level(MAP)
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    floor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(200,160,-5))
    floor.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'))
    floor.static_mesh_component.set_collision_profile_name('BlockAll')
    floor.set_actor_scale3d(unreal.Vector(30,30,.1))
    for rot in ((-35,-135,0),(-20,45,0)):
        light=actors.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,400),unreal.Rotator(*rot))
        component=light.get_component_by_class(unreal.DirectionalLightComponent)
        component.set_intensity(10)
        component.set_cast_shadows(False)
    base='/Game/ParisCombat/Blueprints/Characters/LifecycleDraft/'
    allied='/Game/ParisCombat/Characters/Adaptation/Meshes/'
    german='/Game/ParisCombat/Animation/RetargetDraft/GermanTranslationV1/'
    for i,(faction,variant) in enumerate((('Allied','A'),('Allied','B'),('Allied','A'),('German','A'),('German','B'),('German','A'))):
        cls=unreal.load_class(None,base+('BP_PCPlayerV2.BP_PCPlayerV2_C' if i==0 else 'BP_PCNPCV2.BP_PCNPCV2_C'))
        a=actors.spawn_actor_from_class(cls,unreal.Vector((i%3)*240,(i//3)*300,120))
        name=(allied+('SK_WWII_US_Paratrooper_simple_UE582_v1' if variant=='A' else 'SK_WWII_US_Paratrooper_simpleB_UE582_v1')) if faction=='Allied' else german+'SK_PC_German_'+variant+'_Translation_v1'
        unreal.ParisBlueprintAuthoring.configure_draft_character(a,unreal.load_asset(name),
            unreal.load_asset('/Game/ParisCombat/Animation/DirectionalDraft/ABP_PC_'+faction+('_Stride_v1' if stride else '')))
        a.set_editor_property('TeamId',1 if faction=='Allied' else 2)
        a.set_editor_property('RoleId','Player' if i==0 else 'DiagnosticNPC')
        a.set_actor_label(('P2_Stride_' if stride else 'P2_Lifecycle_')+'%d_%s_%s'%(i+1,faction,variant))
        report['actors'].append({'label':a.get_actor_label(),'class':cls.get_path_name(),'mesh':name,'team':a.get_editor_property('TeamId'),
            'anim_class':a.get_component_by_class(unreal.SkeletalMeshComponent).get_editor_property('anim_class').get_path_name()})
    assert unreal.EditorLevelLibrary.save_current_level()
    report['assets'].append(MAP)
    report['map']=MAP
    report['files']=[]
    for p in report['assets']:
        relative=p.split('.')[0].removeprefix('/Game/')+('.umap' if p==MAP else '.uasset')
        f=STORE/'Content'/relative
        report['files'].append({'path':relative,'size':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
    report['result']='saved_drafts_not_full_P2_acceptance'
except Exception:
    report['errors'].append(traceback.format_exc())
    report['result']='fail_preserve_partial_drafts'
checkpoint()
if report['errors']:
    raise RuntimeError(report['errors'][0])
unreal.log('CS549_LIFECYCLE_AUTHOR_DONE')
