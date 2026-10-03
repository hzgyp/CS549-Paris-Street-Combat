"""Read-only reference-pose/material inspection for component-only forearm rendering."""
import json,os,sys,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from ue_first_person_view_runtime import VIEW,EVIDENCE
OUT=EVIDENCE/os.environ['CS549_FP_IDENTITY'];assert not OUT.exists();OUT.mkdir()
r={'scope':__doc__,'errors':[]}
try:
    cdo=unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class(VIEW));component=cdo.get_component_by_class(unreal.SkeletalMeshComponent)
    mesh=component.get_skeletal_mesh_asset()
    api=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actor=api.spawn_actor_from_class(unreal.SkeletalMeshActor,unreal.Vector())
    c=actor.skeletal_mesh_component;c.set_skeletal_mesh_asset(mesh)
    r['ref_bones']={n:list(c.get_socket_location(n).to_tuple()) for n in ('lowerarm_l','hand_l','middle_03_l','lowerarm_r','hand_r','middle_03_r','pelvis','spine_03')}
    r['materials']={}
    for slot in (2,8):
        material=c.get_material(slot);parent=material.get_editor_property('parent')
        while isinstance(parent,unreal.MaterialInstance):parent=parent.get_editor_property('parent')
        r['materials'][slot]={'instance':material.get_path_name(),'base':parent.get_path_name(),
            'blend_mode':str(parent.get_editor_property('blend_mode')),'attributes':parent.get_editor_property('use_material_attributes')}
    try:r['clothing_asset_count']=len(mesh.get_editor_property('mesh_clothing_assets'))
    except Exception as e:r['clothing_query']=str(e)
    api.destroy_actor(actor)
except Exception:r['errors'].append(traceback.format_exc())
(OUT/'result.json').write_text(json.dumps(r,indent=2));unreal.SystemLibrary.quit_editor()
