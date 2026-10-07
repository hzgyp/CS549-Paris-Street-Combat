"""Same12deg bound in radians; preserve floating display-boundary failure."""
from pathlib import Path
source=Path(__file__).with_name('offline_fit_v4.py').read_text(encoding='utf-8-sig')
source=source.replace("OUT=BASE/'offline_v4'","OUT=BASE/'offline_v5'")
old="exec(compile(source,str(Path(__file__)), 'exec'))"
new="source=source.replace(\"assert abs(r['measured_pitch_deg'])<=12\",\"assert abs(pitch)<=math.radians(12)\")\n"+old
assert source.count(old)==1
source=source.replace(old,new)
exec(compile(source,str(Path(__file__)), 'exec'))
