"""External reference path bookkeeping correction only; same one 8-degree comparison."""
from pathlib import Path
p=Path(__file__).with_name('fit.py')
source=p.read_text(encoding='utf-8-sig')
source=source.replace("OUT=BASE/'stock_down_v1'","OUT=BASE/'stock_down_v2'")
needle="'inputs':[row(p) for p in paths]"
assert source.count(needle)==1
source=source.replace(needle,"'inputs':[row(p) if p.is_relative_to(ROOT) else {'path':str(p),'sha256':sha(p),'size_bytes':p.stat().st_size} for p in (*paths,ROOT/'Tools/Integration/GermanNPCTriggerLowerV7/fit.py')]")
exec(compile(source,str(Path(__file__)),'exec'))
