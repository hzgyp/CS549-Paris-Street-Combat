"""Unsaved fitted assembly horizontal firing comparison, both arms/source materials."""
from pathlib import Path
entry=Path(__file__).with_name('ue_pivot_raise_v7_views.py')
source=entry.read_text(encoding='utf-8')
changes={
    'Unsaved whole-source frozen V6/V7 comparison; no FP binding or live NPC changes.':__doc__,
    'CS549_ALLIED_PIVOT_RAISE_V7_ID':'CS549_ALLIED_FIRING_ASSEMBLY_V13_ID',
    'pivot_raise_trial_v7/result.json':'firing_assembly_v13/result.json',
    'marked_web_v6/result.json':'tip_curl_native_v12/result.json',
    '(TRIAL,V6,Path(__file__))':"(TRIAL,V6,Path(__file__),entry)",
    'pivot_raise_v7_native_views_require_user_review':'firing_assembly_v13_native_comparison_requires_review',
    "assert trial['preservation']['right_skin_cm']<.001":"assert trial['comparison_only'] and trial['comparison_gate_passed']\nassert max(trial['preservation']['hand_relative_gun_matrix_errors'].values())<.001\nassert max(trial['preservation']['digit_skin_rigid_tracking_cm'].values())<.05",
    "pose.set_only_owner_see(False)":"pose.set_only_owner_see(False)\n            pose.set_tickable_when_paused(True)\n            pose.set_component_tick_enabled(True)\n            pose.set_editor_property('visibility_based_anim_tick_option',unreal.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)\n            r['diagnostic_component_native_refresh_while_paused']=True",
    "if index==2 and not (OUT/'early_acceptance.json').is_file():return":"if index==2:\n            gate=OUT/'early_acceptance.json'\n            if not gate.is_file():return\n            assert read(gate)['accepted'],'Baseline render parity rejected; no candidate applied'",
    "    save()\ndef finish(error=None):":"    r['pose_apply_time']=time.monotonic()\n    save()\ndef finish(error=None):",
    "        if requested is None:\n            r['captures'].append(camera_for(name,axis,width))":"        if requested is None:\n            if time.monotonic()-r['pose_apply_time']<2:return\n            r['captures'].append(camera_for(name,axis,width))",
    "views=[('before_right','right',78),('before_trigger','right',30),\n       ('after_right','right',78),('after_front','front',78),('after_top','top',78),\n       ('after_trigger','right',30),('after_support','front',40),\n       ('after_support_right','right',40),('after_reverse','reverse',78),\n       ('after_context','right',155),('before_context','right',155)]":
    "views=[('before_right','right',160),('before_trigger','right',30),\n       ('after_right','right',160),('after_front','front',160),('after_top','top',160),\n       ('after_trigger','right',30),('after_reverse_trigger','reverse',30),\n       ('after_support','right',45),('after_shoulder','right',50),('after_reverse','reverse',160),\n       ('after_context','right',240),('before_context','right',240),\n       ('after_body_right','right',290),('after_body_front','front',290),('before_shoulder','right',50)]",
    "    base=next(c for c in previous['captures'] if c['file']=='after_right.png')\n    center=unreal.Vector(*base['target_cm'])\n    if name.endswith('_trigger'):center=unreal.Vector(*trial['pad_world_cm'])\n    if 'support' in name:\n        center=unreal.Vector(*trial['after_bones']['hand_l']['t'])\n    if 'context' in name:\n        center=(center+unreal.Vector(*trial['before_bones']['spine_03']['t']))/2":
    "    # Fixed overview camera, full before/after assembly; details follow actual stage.\n    butt=unreal.Vector(*trial['butt_target_world_cm'])\n    muzzle=unreal.Vector(*trial['muzzle_after_cm'])\n    center=(butt+muzzle)/2\n    if name.endswith('_trigger'):\n        baseline=read(BASE/'tip_curl_v12/result.json')\n        center=unreal.Vector(*(baseline['pad_world_cm'] if stage=='before' else trial['pad_world_cm']))\n    if 'support' in name:center=unreal.Vector(*trial[stage+'_bones']['hand_l']['t'])\n    if 'shoulder' in name:\n        center=unreal.Vector(*tm.point(trial[stage+'_gun_world'],trial['butt_local_cm']))\n    if 'context' in name:center=(center+unreal.Vector(*trial['before_bones']['spine_03']['t']))/2\n    if 'body' in name:\n        center=(unreal.Vector(*trial['before_bones']['head']['t'])+unreal.Vector(*trial['before_bones']['root']['t']))/2",
}
for old,new in changes.items():
    assert source.count(old)==1,'Frozen viewer contract changed: '+old
    source=source.replace(old,new)
for old,new,count in (
    ('PC_AlliedPivotRaiseV7Frozen','PC_AlliedFiringAssemblyV13Frozen',2),
    ('PC_AlliedPivotRaiseV7Capture','PC_AlliedFiringAssemblyV13Capture',2),
    ('PC_AlliedPivotRaiseV7Fill','PC_AlliedFiringAssemblyV13Fill',1)):
    assert source.count(old)==count;source=source.replace(old,new)
exec(compile(source,str(entry)+':firing_assembly_v13','exec'),globals())
