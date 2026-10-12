"""Read-only authored fire system timing, defaults and emitter handles."""
import unreal,json
from pathlib import Path
out=Path(r'D:/0.Rutgers/CS549/Project-New/tmp/g1-player-death-20261011/fire-system-audit-v1');out.mkdir(exist_ok=True)
obj=unreal.load_asset('/Game/WW2City/Environment/Particle/Fire/Particle/NS_Fire_Small');r=dict(path=obj.get_path_name())
for key in ['warmup_time','warmup_tick_count','warmup_tick_delta','emitter_handles','exposed_parameters','fixed_bounds','scalability_overrides','effect_type','b_fixed_bounds','fixed_bounds_enabled']:
    try:r[key]=str(obj.get_editor_property(key))[:15000]
    except Exception as err:r[key+'_unavailable']=str(err)
r['available_methods']=[n for n in dir(obj) if any(s in n for s in ['emitter','parameter','warmup'])]
(out/'SYSTEM.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
unreal.log('PARIS_DEATH_FIRE_SYSTEM_READ_ONLY_COMPLETE')
