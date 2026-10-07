"""Unsaved fixed-grip right-arm comparison, approved FP directional analogue."""
from pathlib import Path
entry=Path(__file__).with_name('ue_pivot_raise_v7_views.py')
source=entry.read_text(encoding='utf-8')
changes={
    'Unsaved whole-source frozen V6/V7 comparison; no FP binding or live NPC changes.':__doc__,
    'CS549_ALLIED_PIVOT_RAISE_V7_ID':'CS549_ALLIED_FP_WRIST_V14_ID',
    'pivot_raise_trial_v7/result.json':'fp_wrist_v14/result.json',
    'marked_web_v6/result.json':'firing_assembly_native_v13/result.json',
    '(TRIAL,V6,Path(__file__))':"(TRIAL,V6,Path(__file__),entry)",
    'pivot_raise_v7_native_views_require_user_review':'fp_wrist_v14_native_comparison_requires_review',
    "assert trial['preservation']['right_skin_cm']<.001":"assert trial['comparison_only'] and trial['comparison_gate_passed']\nassert trial['preservation']['digit_skin_cm']<.001\nassert trial['before_gun_world']==trial['after_gun_world']",
    "pose.set_only_owner_see(False)":"pose.set_only_owner_see(False)\n            pose.set_tickable_when_paused(True)\n            pose.set_component_tick_enabled(True)\n            pose.set_editor_property('visibility_based_anim_tick_option',unreal.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)\n            r['diagnostic_component_native_refresh_while_paused']=True",
    "if index==2 and not (OUT/'early_acceptance.json').is_file():return":"if index==2:\n            gate=OUT/'early_acceptance.json'\n            if not gate.is_file():return\n            assert read(gate)['accepted'],'Baseline render parity rejected; no candidate applied'",
    "    save()\ndef finish(error=None):":"    r['pose_apply_time']=time.monotonic()\n    save()\ndef finish(error=None):",
    "        if requested is None:\n            r['captures'].append(camera_for(name,axis,width))":"        if requested is None:\n            if time.monotonic()-r['pose_apply_time']<2:return\n            r['captures'].append(camera_for(name,axis,width))",
    "views=[('before_right','right',78),('before_trigger','right',30),\n       ('after_right','right',78),('after_front','front',78),('after_top','top',78),\n       ('after_trigger','right',30),('after_support','front',40),\n       ('after_support_right','right',40),('after_reverse','reverse',78),\n       ('after_context','right',155),('before_context','right',155)]":
    "views=[('before_right','right',180),('before_wrist','right',55),\n       ('after_right','right',180),('after_front','front',180),('after_top','top',230),\n       ('after_wrist','right',55),('after_reverse_wrist','reverse',55),\n       ('after_elbow','front',65),('after_shoulder','right',70),('after_reverse','reverse',180),\n       ('after_context','right',260),('before_context','right',260),\n       ('after_body_right','right',340),('after_body_front','front',340),('before_elbow','front',65)]",
    "    base=next(c for c in previous['captures'] if c['file']=='after_right.png')\n    center=unreal.Vector(*base['target_cm'])\n    if name.endswith('_trigger'):center=unreal.Vector(*trial['pad_world_cm'])\n    if 'support' in name:\n        center=unreal.Vector(*trial['after_bones']['hand_l']['t'])\n    if 'context' in name:\n        center=(center+unreal.Vector(*trial['before_bones']['spine_03']['t']))/2":
    "    butt=unreal.Vector(*trial['butt_target_world_cm'])\n    muzzle=unreal.Vector(*trial['muzzle_after_cm'])\n    center=(butt+muzzle)/2\n    if 'wrist' in name:center=(unreal.Vector(*trial['before_bones']['hand_r']['t'])+unreal.Vector(*trial['before_bones']['lowerarm_r']['t']))/2\n    if 'elbow' in name:center=unreal.Vector(*trial['after_bones']['lowerarm_r']['t'])\n    if 'shoulder' in name:center=unreal.Vector(*trial['before_bones']['upperarm_r']['t'])\n    if 'context' in name:center=(center+unreal.Vector(*trial['before_bones']['spine_03']['t']))/2\n    if 'body' in name:center=(unreal.Vector(*trial['before_bones']['head']['t'])+unreal.Vector(*trial['before_bones']['root']['t']))/2",
}
for old,new in changes.items():
    assert source.count(old)==1,'Frozen viewer contract changed: '+old
    source=source.replace(old,new)
for old,new,count in (
    ('PC_AlliedPivotRaiseV7Frozen','PC_AlliedFPWristV14Frozen',2),
    ('PC_AlliedPivotRaiseV7Capture','PC_AlliedFPWristV14Capture',2),
    ('PC_AlliedPivotRaiseV7Fill','PC_AlliedFPWristV14Fill',1)):
    assert source.count(old)==count;source=source.replace(old,new)
exec(compile(source,str(entry)+':fp_wrist_v14','exec'),globals())
