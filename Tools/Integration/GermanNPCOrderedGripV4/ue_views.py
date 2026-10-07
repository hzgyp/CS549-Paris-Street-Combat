"""New unsaved German frozen full-mesh comparison; no source driver or asset writes."""
from pathlib import Path
template=Path(__file__).resolve().parents[1]/'AlliedNPCGripV2/ue_pivot_raise_v7_views.py'
source=template.read_text(encoding='utf-8-sig')
changes={
    "sys.path.insert(0,str(Path(__file__).parent))":"sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'GermanNPCGripV1'))",
    "from common import *":"from common import *\nBASE=STORE/'Evidence/GermanNPCOrderedGripV4'",
    'CS549_ALLIED_PIVOT_RAISE_V7_ID':'CS549_GERMAN_ORDERED_GRIP_ID',
    "TRIAL=BASE/'pivot_raise_trial_v7/result.json'":"TRIAL=BASE/'offline_v6/result.json'",
    "V6=BASE/'marked_web_v6/result.json'":"V6=STORE/'Evidence/GermanNPCSmallPivotV3/small_rotation_v1/result.json'",
    "assert not trial['errors'] and trial['inputs_unchanged'] and trial['guards_after']==611":"assert not trial['errors'] and trial['guards_after']==618",
    "assert trial['preservation']['new_severe_edges']==0":"assert trial['new_severe_edges']==0",
    "assert trial['preservation']['right_skin_cm']<.001":"assert trial['right_gun_hand_matrix_error']<1e-8 and trial['digit_local_matrix_error']<1e-8",
    "assert all(sha(ROOT/p)==h for p,h in trial['input_hashes'].items())":"assert all(sha(ROOT/e['path'])==e['sha256'] for e in trial['inputs'])",
    "(TRIAL,V6,Path(__file__))":"(TRIAL,V6,Path(__file__),template)",
    "'pivot_raise_v7_native_views_require_user_review'":"'german_ordered_static_views_require_user_review'",
    "assert time.monotonic()-start<300":"assert time.monotonic()-start<240",
    "'PC_City_Ally1'":"'PC_City_Enemy1'",
    "assert 'RifleAttachmentV3' in gun.get_class().get_name()":"assert 'GermanRifleAttachmentV2' in gun.get_class().get_name()",
    "assert 'SK_WWII_US_Paratrooper_simple_UE582_v1' in soldier.mesh.get_skeletal_mesh_asset().get_path_name()":"assert 'SK_PC_German_A_Translation_v1' in soldier.mesh.get_skeletal_mesh_asset().get_path_name()",
    "assert 'SM_M1_Garand' in c.get_editor_property('static_mesh').get_path_name()":"assert 'SM_PC_GermanRifleV15' in c.get_editor_property('static_mesh').get_path_name()\n            assert str(c.get_collision_enabled())=='CollisionEnabled.NO_COLLISION'",
    "pose.set_only_owner_see(False)":"pose.set_only_owner_see(False)\n            pose.set_tickable_when_paused(True)\n            pose.set_component_tick_enabled(True)\n            pose.set_editor_property('visibility_based_anim_tick_option',unreal.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)",
    "    save()\ndef finish(error=None):":"    r['pose_apply_time']=time.monotonic()\n    save()\ndef finish(error=None):",
    "        if requested is None:\n            r['captures'].append(camera_for(name,axis,width))":"        if requested is None:\n            if time.monotonic()-r['pose_apply_time']<2:return\n            r['captures'].append(camera_for(name,axis,width))",
    "        if index==2 and not (OUT/'early_acceptance.json').is_file():return":"        if index==2:\n            gate=OUT/'early_acceptance.json'\n            if not gate.is_file():return\n            assert read(gate)['accepted'],'Frozen baseline parity rejected'",
    "expected_stage='before' if name.startswith('before') else 'after'":"expected_stage=name.split('_')[0]",
    "if axis=='top':rot=unreal.Rotator(pitch=-90,yaw=0,roll=0)":"if axis=='top':rot=unreal.Rotator(pitch=-90,yaw=soldier.get_actor_rotation().yaw,roll=0)",
}
oldviews=source[source.index('views=['):source.index('\n\ndef xyz')]
changes[oldviews]="""views=[('before_right','right',78),('before_top','top',78),
       ('first_right','right',78),('first_top','top',78),
       ('after_front','front',100),('after_right','right',100),('after_top','top',100),
       ('after_reverse','reverse',100),('after_trigger','right',30),('after_reverse_trigger','reverse',30),
       ('after_palm','top',40),('after_support','right',40),('after_support_top','top',40),
       ('after_context','right',170),('after_body','front',290)]"""
oldcamera=source[source.index("    base=next(c for c in previous['captures']"):source.index('    eye=center+direction*250')]
changes[oldcamera]="""    hand=(unreal.Vector(*trial[stage+'_bones']['hand_r']['t'])+unreal.Vector(*trial[stage+'_bones']['hand_l']['t']))/2
    center=hand
    if 'trigger' in name:center=unreal.Vector(*tm.point(trial[stage+'_gun_world'],trial['trigger_pivot_gun_cm']))
    if 'palm' in name:center=unreal.Vector(*tm.point(trial[stage+'_gun_world'],trial['stock_pivot_gun_cm']))
    if 'support' in name:center=unreal.Vector(*trial['left_palm_target_world_cm'])
    if 'context' in name:center=(center+unreal.Vector(*trial['before_bones']['spine_03']['t']))/2
    if 'body' in name:center=(unreal.Vector(*trial['before_bones']['head']['t'])+unreal.Vector(*trial['before_bones']['root']['t']))/2
    direction={'front':soldier.get_actor_forward_vector(),'right':soldier.get_actor_right_vector(),
               'reverse':-soldier.get_actor_right_vector(),'top':unreal.Vector(0,0,1)}[axis]
"""
changes["try:\n    container=actors.spawn_actor_from_class"]="""try:
    original=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='PC_City_Enemy1')
    assert original.get_editor_property('WeaponAppearance') is None
    cls=unreal.EditorAssetLibrary.load_blueprint_class('/Game/ParisCombat/Weapons/GermanRifleUEV1/BP_PC_GermanRifleAttachmentV2')
    staged=actors.spawn_actor_from_class(cls,original.get_actor_location(),unreal.Rotator())
    staged.set_editor_property('GripMesh',original.mesh);staged.set_editor_property('Combatant',original);staged.set_owner(original)
    assert staged.attach_to_component(original.mesh,'hand_r',unreal.AttachmentRule.KEEP_RELATIVE,unreal.AttachmentRule.KEEP_RELATIVE,unreal.AttachmentRule.KEEP_RELATIVE,False)
    original.set_editor_property('WeaponAppearance',staged)
    container=actors.spawn_actor_from_class"""
for old,new in changes.items():
    assert source.count(old)==1,old
    source=source.replace(old,new)
source=source.replace('PC_AlliedPivotRaiseV7','PC_GermanOrderedGripV4')
exec(compile(source,str(Path(__file__)),'exec'))
