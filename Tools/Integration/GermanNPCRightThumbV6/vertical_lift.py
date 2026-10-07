"""One different pure-elevation thumb root fit; preserve original transverse heading."""
from pathlib import Path
entry=Path(__file__).with_name('root_lift.py').read_text(encoding='utf-8-sig')
needle="exec(compile(source,str(Path(__file__)),'exec'))"
extra='''source=source.replace("OUT=BASE/'root_lift_v1'","OUT=BASE/'vertical_lift_v2'")
source=source.replace("    rotation=Vector(a).rotation_difference(Vector(b))", """    radius=float(np.linalg.norm(a))
    height=float(b@up);assert abs(height)<radius
    transverse=a-up*(a@up);transverse/=np.linalg.norm(transverse)
    b=transverse*np.sqrt(radius*radius-height*height)+up*height
    target=root+b
    rotation=Vector(a).rotation_difference(Vector(b))""")
source=source.replace("existing_idle_root_lift","existing_idle_vertical_lift")
'''+needle
assert entry.count(needle)==1
entry=entry.replace(needle,extra)
exec(compile(entry,str(Path(__file__)),'exec'))
