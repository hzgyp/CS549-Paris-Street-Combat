"""Unsaved Allied V9/current functional-trigger fit; no live driver or FP edit."""
from pathlib import Path
entry=Path(__file__).with_name('ue_pivot_raise_v7_views.py')
source=entry.read_text(encoding='utf-8')
changes={
    'Unsaved whole-source frozen V6/V7 comparison; no FP binding or live NPC changes.':__doc__,
    'CS549_ALLIED_PIVOT_RAISE_V7_ID':'CS549_ALLIED_TRIGGER_FIT_V10_ID',
    'pivot_raise_trial_v7/result.json':'trigger_pad_v10d/result.json',
    'marked_web_v6/result.json':'pivot_rotate_native_v9/result.json',
    '(TRIAL,V6,Path(__file__))':"(TRIAL,V6,Path(__file__),entry,entry.with_name('ue_pivot_raise_v7b_views.py'))",
    'pivot_raise_v7_native_views_require_user_review':'trigger_fit_v10_native_views_require_user_review',
    "pose.set_only_owner_see(False)":"pose.set_only_owner_see(False)\n            pose.set_tickable_when_paused(True)\n            pose.set_component_tick_enabled(True)\n            pose.set_editor_property('visibility_based_anim_tick_option',unreal.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)\n            r['diagnostic_component_native_refresh_while_paused']=True",
    "if index==2 and not (OUT/'early_acceptance.json').is_file():return":"if index==2:\n            gate=OUT/'early_acceptance.json'\n            if not gate.is_file():return\n            assert read(gate)['accepted'],'Baseline render parity rejected; no candidate applied'",
    "    save()\ndef finish(error=None):":"    r['pose_apply_time']=time.monotonic()\n    save()\ndef finish(error=None):",
    "        if requested is None:\n            r['captures'].append(camera_for(name,axis,width))":"        if requested is None:\n            if time.monotonic()-r['pose_apply_time']<2:return\n            r['captures'].append(camera_for(name,axis,width))",
    "('after_trigger','right',30),('after_support','front',40),\n       ('after_support_right','right',40),('after_reverse','reverse',78)":
    "('after_trigger','right',30),('after_reverse_trigger','reverse',30),\n       ('after_top_trigger','top',30),('after_under_trigger','under',30),('after_reverse','reverse',78)",
    "'reverse':unreal.Vector(0,-1,0),'top':unreal.Vector(0,0,1)":"'reverse':unreal.Vector(0,-1,0),'top':unreal.Vector(0,0,1),'under':unreal.Vector(0,0,-1)",
    "if axis=='top':rot=unreal.Rotator(pitch=-90,yaw=0,roll=0)":"if axis=='top':rot=unreal.Rotator(pitch=-90,yaw=0,roll=0)\n    if axis=='under':rot=unreal.Rotator(pitch=90,yaw=0,roll=0)",
    "assert trial['preservation']['new_severe_edges']==0":"assert trial['contact_gate_passed'] and trial['final_contact']['actual_pad_to_blade_cm']<=.15\nassert sum(trial['final_contact']['digits']['index'].values())==0\nassert trial['preservation']['new_severe_edges']==0",
}
for old,new in changes.items():
    assert source.count(old)==1,'Frozen viewer contract changed: '+old
    source=source.replace(old,new)
for old,new,count in (
    ('PC_AlliedPivotRaiseV7Frozen','PC_AlliedTriggerFitV10Frozen',2),
    ('PC_AlliedPivotRaiseV7Capture','PC_AlliedTriggerFitV10Capture',2),
    ('PC_AlliedPivotRaiseV7Fill','PC_AlliedTriggerFitV10Fill',1)):
    assert source.count(old)==count
    source=source.replace(old,new)
exec(compile(source,str(entry)+':trigger_fit_v10','exec'),globals())
