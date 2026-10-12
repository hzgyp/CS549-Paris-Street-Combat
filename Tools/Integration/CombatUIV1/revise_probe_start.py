"""Choose the actual Ready Begin button rather than assuming old menu selection zero."""
from pathlib import Path
p=Path(__file__).with_name('ParisCombatUIProbe.cpp')
t=p.read_text('utf-8')
old='Tap(PC,EKeys::Escape);Tap(PC,EKeys::Enter);'
assert t.count(old)==3,t.count(old)
t=t.replace(old,'Tap(PC,EKeys::Escape);Click(PC,960,772);')
old='Tap(PC,EKeys::Enter);Go(10);'
assert t.count(old)==1
t=t.replace(old,'Click(PC,960,772);Go(10);')
p.write_text(t,encoding='utf-8')
