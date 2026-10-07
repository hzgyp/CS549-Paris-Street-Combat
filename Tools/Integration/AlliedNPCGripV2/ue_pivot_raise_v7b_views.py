"""Source-verified display-only refresh correction; exact unchanged V7 candidate."""
from pathlib import Path
entry=Path(__file__).with_name('ue_pivot_raise_v7_views.py')
source=entry.read_text(encoding='utf-8')
changes={
    "(TRIAL,V6,Path(__file__))":"(TRIAL,V6,Path(__file__),entry)",
    "pose.set_only_owner_see(False)":"pose.set_only_owner_see(False)\n            pose.set_tickable_when_paused(True)\n            pose.set_component_tick_enabled(True)\n            pose.set_editor_property('visibility_based_anim_tick_option',unreal.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)\n            r['diagnostic_component_native_refresh_while_paused']=True",
    "if index==2 and not (OUT/'early_acceptance.json').is_file():return":
    "if index==2:\n            gate=OUT/'early_acceptance.json'\n            if not gate.is_file():return\n            assert read(gate)['accepted'],'Baseline render parity rejected; no candidate applied'",
    "    save()\ndef finish(error=None):":"    r['pose_apply_time']=time.monotonic()\n    save()\ndef finish(error=None):",
    "        if requested is None:\n            r['captures'].append(camera_for(name,axis,width))":
    "        if requested is None:\n            if time.monotonic()-r['pose_apply_time']<1:return\n            r['captures'].append(camera_for(name,axis,width))",
}
for old,new in changes.items():
    assert source.count(old)==1,'Display correction source contract changed'
    source=source.replace(old,new)
exec(compile(source,str(entry),'exec'),globals())
