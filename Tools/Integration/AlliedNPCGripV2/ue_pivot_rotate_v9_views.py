"""Frozen V7-to-V9 extra2-degree pivot raise; no V8 translation or source edits."""
from pathlib import Path
entry=Path(__file__).with_name('ue_pivot_raise_v7_views.py')
source=entry.read_text(encoding='utf-8')
changes={
    "CS549_ALLIED_PIVOT_RAISE_V7_ID":"CS549_ALLIED_PIVOT_ROTATE_V9_ID",
    "pivot_raise_trial_v7/result.json":"pivot_rotate_trial_v9/result.json",
    "marked_web_v6/result.json":"pivot_raise_native_v7b/result.json",
    "(TRIAL,V6,Path(__file__))":"(TRIAL,V6,Path(__file__),entry,entry.with_name('ue_pivot_raise_v7b_views.py'))",
    "pivot_raise_v7_native_views_require_user_review":"pivot_rotate_v9_native_views_require_user_review",
    "pose.set_only_owner_see(False)":"pose.set_only_owner_see(False)\n            pose.set_tickable_when_paused(True)\n            pose.set_component_tick_enabled(True)\n            pose.set_editor_property('visibility_based_anim_tick_option',unreal.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)\n            r['diagnostic_component_native_refresh_while_paused']=True",
    "if index==2 and not (OUT/'early_acceptance.json').is_file():return":
    "if index==2:\n            gate=OUT/'early_acceptance.json'\n            if not gate.is_file():return\n            assert read(gate)['accepted'],'Baseline render parity rejected; no candidate applied'",
    "    save()\ndef finish(error=None):":"    r['pose_apply_time']=time.monotonic()\n    save()\ndef finish(error=None):",
    "        if requested is None:\n            r['captures'].append(camera_for(name,axis,width))":
    "        if requested is None:\n            if time.monotonic()-r['pose_apply_time']<1:return\n            r['captures'].append(camera_for(name,axis,width))",
    "('after_trigger','right',30),('after_support','front',40),\n       ('after_support_right','right',40),('after_reverse','reverse',78)":
    "('after_trigger','right',30),('after_reverse','reverse',78)",
}
for old,new in changes.items():
    assert source.count(old)==1,'Verified frozen viewer contract changed: '+old
    source=source.replace(old,new)
for old,new,count in (
    ('PC_AlliedPivotRaiseV7Frozen','PC_AlliedPivotRotateV9Frozen',2),
    ('PC_AlliedPivotRaiseV7Capture','PC_AlliedPivotRotateV9Capture',2),
    ('PC_AlliedPivotRaiseV7Fill','PC_AlliedPivotRotateV9Fill',1)):
    assert source.count(old)==count
    source=source.replace(old,new)
exec(compile(source,str(entry),'exec'),globals())
