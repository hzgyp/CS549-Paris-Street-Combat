"""One bounded UE FK retarget of owned D059 reload; no invented keyframes."""
import json
import math
import os
import sys
import traceback
from pathlib import Path
import unreal
sys.path.insert(0, str(Path(__file__).parent))
from weapon_animation_reuse_common import ROOT, STORE, SOURCE_RELOAD, RELOAD, output, guard, record
OUT = output(os.environ['CS549_ANIMATION_IDENTITY'])
r = {'status': 'retargeting', 'errors': [], 'packages': [], 'map_saved': False,
     'source': SOURCE_RELOAD, 'method': 'UE native FK retarget, original finger tracks copied without changes'}
(OUT / 'source.py').write_bytes(Path(__file__).read_bytes())
DIR = RELOAD.rsplit('/', 1)[0]


def save(asset):
    assert unreal.EditorAssetLibrary.save_loaded_asset(asset, only_if_is_dirty=False)
    r['packages'].append(record(asset.get_path_name().split('.')[0]))


try:
    guard()
    assert not hasattr(unreal, 'ParisBlueprintAuthoring')
    assert not unreal.EditorAssetLibrary.does_directory_exist(DIR), 'Preserve prior retarget trial'
    source_mesh = unreal.load_asset('/Game/Rifle_01/Character/Mesh/SK_Mannequin')
    target_mesh = unreal.load_asset('/Game/ParisCombat/Characters/Adaptation/Meshes/SK_WWII_US_Paratrooper_simple_UE582_v1')
    clip = unreal.load_asset(SOURCE_RELOAD)
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    rigs = []
    for label, mesh in (('Source', source_mesh), ('Allied', target_mesh)):
        rig = tools.create_asset('IK_PC_D059' + label + 'V1', DIR, unreal.IKRigDefinition, unreal.IKRigDefinitionFactory())
        assert rig
        c = unreal.IKRigController.get_controller(rig)
        assert c.set_skeletal_mesh(mesh)
        assert c.set_retarget_root('pelvis')
        # Explicit existing-bone chains; no IK goals or new skeleton/weights.
        for name, first, last in (('Spine','spine_01','spine_03'),('Head','neck_01','head'),
            ('LeftArm','clavicle_l','hand_l'),('RightArm','clavicle_r','hand_r'),
            ('LeftLeg','thigh_l','ball_l'),('RightLeg','thigh_r','ball_r')):
            assert str(c.add_retarget_chain(name, first, last, 'None')) == name
        rigs.append(rig)
        save(rig)
    rt = tools.create_asset('RTG_PC_D059AlliedV1', DIR, unreal.IKRetargeter, unreal.IKRetargetFactory())
    rc = unreal.IKRetargeterController.get_controller(rt)
    rc.set_ik_rig(unreal.RetargetSourceOrTarget.SOURCE, rigs[0])
    rc.set_ik_rig(unreal.RetargetSourceOrTarget.TARGET, rigs[1])
    rc.set_preview_mesh(unreal.RetargetSourceOrTarget.SOURCE, source_mesh)
    rc.set_preview_mesh(unreal.RetargetSourceOrTarget.TARGET, target_mesh)
    rc.add_default_ops()
    rc.auto_map_chains(unreal.AutoMapChainType.EXACT, True)
    rc.auto_align_all_bones(unreal.RetargetSourceOrTarget.TARGET)
    r['ops'] = []
    for i in range(rc.get_num_retarget_ops()):
        name = str(rc.get_op_name(i))
        # FK + pelvis only. No new procedural IK action or root locomotion.
        enabled = 'FK' in name or 'Pelvis' in name
        assert rc.set_retarget_op_enabled(i, enabled)
        r['ops'].append({'name': name, 'enabled': enabled})
    assert any(x['enabled'] and 'FK' in x['name'] for x in r['ops'])
    save(rt)
    args = unreal.IKRetargetBatchOperationInputs()
    args.set_editor_property('assets_to_retarget', [unreal.EditorAssetLibrary.find_asset_data(SOURCE_RELOAD)])
    for name, val in (('source_mesh',source_mesh),('target_mesh',target_mesh),('ik_retarget_asset',rt),
        ('search',clip.get_name()),('replace',RELOAD.rsplit('/',1)[1]),('target_path',DIR),
        ('include_referenced_assets',False),('overwrite_existing_files',False)):
        args.set_editor_property(name, val)
    assets = unreal.IKRetargetBatchOperation.run_batch_retarget(args)
    assert len(assets) == 1, assets
    result = unreal.load_asset(RELOAD)
    assert result and result.get_editor_property('skeleton') == target_mesh.get_editor_property('skeleton')
    # Retarget only arms/body. Preserve the source motion's finger local poses.
    count = unreal.AnimationLibrary.get_num_frames(clip)
    names = [str(n) for n in unreal.AnimationLibrary.get_animation_track_names(clip)
             if str(n).startswith(('index_', 'middle_', 'ring_', 'pinky_', 'thumb_'))]
    controller = result.get_editor_property('controller')
    r['finger_tracks_copied'] = names
    for name in names:
        keys = [unreal.AnimationLibrary.get_bone_pose_for_time(clip, name, clip.get_play_length()*i/count, False) for i in range(count+1)]
        assert controller.set_bone_track_keys(name, [t.translation for t in keys], [t.rotation for t in keys], [t.scale3d for t in keys], False)
    max_delta = 0
    for name in names:
        for fraction in (0,.15,.3,.5,.7,.85,.999):
            a = unreal.AnimationLibrary.get_bone_pose_for_time(clip,name,clip.get_play_length()*fraction,False)
            b = unreal.AnimationLibrary.get_bone_pose_for_time(result,name,result.get_play_length()*fraction,False)
            max_delta = max(max_delta,(a.translation-b.translation).length(),abs(a.rotation.x-b.rotation.x),abs(a.rotation.y-b.rotation.y),abs(a.rotation.z-b.rotation.z),abs(a.rotation.w-b.rotation.w))
    r['finger_local_max_delta'] = max_delta
    assert max_delta < .002, 'Retarget must not change existing source fingers'
    assert abs(result.get_play_length()-clip.get_play_length()) < .002
    save(result)
    r['duration'] = result.get_play_length()
    r['status'] = 'saved_unselected_existing_motion_derivative_requires_target_visual_gate'
except Exception:
    r['errors'].append(traceback.format_exc())
    r['status'] = 'failed'
finally:
    r['protected_files_unchanged'] = guard()
    (OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    unreal.SystemLibrary.quit_editor()
