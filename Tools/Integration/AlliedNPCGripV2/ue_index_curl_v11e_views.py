"""Unsaved requested rearward/index-tip comparison; blade contact remains failed."""
from pathlib import Path
entry=Path(__file__).with_name('ue_pivot_raise_v7_views.py')
source=entry.read_text(encoding='utf-8')
changes={
    'Unsaved whole-source frozen V6/V7 comparison; no FP binding or live NPC changes.':__doc__,
    'CS549_ALLIED_PIVOT_RAISE_V7_ID':'CS549_ALLIED_INDEX_CURL_V11_ID',
    'pivot_raise_trial_v7/result.json':'index_curl_v11e/result.json',
    'marked_web_v6/result.json':'trigger_fit_native_v10/result.json',
    '(TRIAL,V6,Path(__file__))':"(TRIAL,V6,Path(__file__),entry,entry.with_name('ue_trigger_fit_v10_views.py'))",
    'pivot_raise_v7_native_views_require_user_review':'index_curl_v11_native_comparison_contact_failed',
    "pose.set_only_owner_see(False)":"pose.set_only_owner_see(False)\n            pose.set_tickable_when_paused(True)\n            pose.set_component_tick_enabled(True)\n            pose.set_editor_property('visibility_based_anim_tick_option',unreal.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)\n            r['diagnostic_component_native_refresh_while_paused']=True",
    "if index==2 and not (OUT/'early_acceptance.json').is_file():return":"if index==2:\n            gate=OUT/'early_acceptance.json'\n            if not gate.is_file():return\n            assert read(gate)['accepted'],'Baseline render parity rejected; no candidate applied'",
    "    save()\ndef finish(error=None):":"    r['pose_apply_time']=time.monotonic()\n    save()\ndef finish(error=None):",
    "        if requested is None:\n            r['captures'].append(camera_for(name,axis,width))":"        if requested is None:\n            if time.monotonic()-r['pose_apply_time']<2:return\n            r['captures'].append(camera_for(name,axis,width))",
    "('after_trigger','right',30),('after_support','front',40),\n       ('after_support_right','right',40),('after_reverse','reverse',78)":
    "('after_trigger','right',30),('after_reverse_trigger','reverse',30),\n       ('after_top_trigger','top',30),('after_under_trigger','under',30),('after_reverse','reverse',78)",
    "'reverse':unreal.Vector(0,-1,0),'top':unreal.Vector(0,0,1)":"'reverse':unreal.Vector(0,-1,0),'top':unreal.Vector(0,0,1),'under':unreal.Vector(0,0,-1)",
    "if axis=='top':rot=unreal.Rotator(pitch=-90,yaw=0,roll=0)":"if axis=='top':rot=unreal.Rotator(pitch=-90,yaw=0,roll=0)\n    if axis=='under':rot=unreal.Rotator(pitch=90,yaw=0,roll=0)",
    "assert trial['preservation']['right_skin_cm']<.001":"assert trial['comparison_only'] and not trial['contact_gate_passed']\nassert trial['preservation']['right_wrist_matrix_error']<1e-8\nassert trial['preservation']['unaffected_skin_cm']<.001\nassert trial['preservation']['new_index_neighbor_self_pairs']==0\nassert trial['final_contact']['digits']['index']['stock']==0 and trial['final_contact']['digits']['index']['guard']==0",
}
for old,new in changes.items():
    assert source.count(old)==1,'Frozen viewer contract changed: '+old
    source=source.replace(old,new)
for old,new,count in (
    ('PC_AlliedPivotRaiseV7Frozen','PC_AlliedIndexCurlV11Frozen',2),
    ('PC_AlliedPivotRaiseV7Capture','PC_AlliedIndexCurlV11Capture',2),
    ('PC_AlliedPivotRaiseV7Fill','PC_AlliedIndexCurlV11Fill',1)):
    assert source.count(old)==count
    source=source.replace(old,new)
exec(compile(source,str(entry)+':index_curl_v11_comparison','exec'),globals())
