"""Existing read-only project inspector; no native setters/save."""
import unreal,json
from pathlib import Path
out=Path(r'D:/0.Rutgers/CS549/Project-New/tmp/g1-player-death-20261011/fire-system-audit-v2');out.mkdir(exist_ok=True)
obj=unreal.load_asset('/Game/WW2City/Environment/Particle/Fire/Particle/NS_Fire_Small')
result=json.loads(unreal.ParisMuzzleFlashLibrary.inspect_purchased_system(obj))
(out/'DEFAULTS.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
unreal.log('PARIS_DEATH_FIRE_DEFAULTS_READ_ONLY_COMPLETE')
