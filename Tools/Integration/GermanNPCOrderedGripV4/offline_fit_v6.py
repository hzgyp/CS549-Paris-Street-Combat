"""Different coupled assembly mechanism, not a fixed-hand pitch retry."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent))
from arm_fit import integrate
source=Path(__file__).with_name('offline_fit_v4.py').read_text(encoding='utf-8-sig')
source=source.replace("OUT=BASE/'offline_v4'","OUT=BASE/'offline_v6'")
needle="exec(compile(source,str(Path(__file__)), 'exec'))"
extra="""source=source.replace("assert abs(r['measured_pitch_deg'])<=12","assert abs(pitch)<=math.radians(12)")
oldblock=source[source.index('    before=contacts(g0,'):source.index('except Exception:')]
source=source.replace(oldblock,"    r['guards_after']=guards()\\n    integrate(dict(globals(),print=print))\\n")
"""+needle
assert source.count(needle)==1
source=source.replace(needle,extra)
exec(compile(source,str(Path(__file__)), 'exec'))
