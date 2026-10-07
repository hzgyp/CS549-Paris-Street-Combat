"""Actual collision enum comparison only; earlier no-capture result retained."""
from pathlib import Path
entry=Path(__file__).with_name('ue_views.py').read_text(encoding='utf-8-sig')
needle="exec(compile(source,str(Path(__file__)),'exec'))"
extra="source=source.replace(\"str(c.get_collision_enabled())=='CollisionEnabled.NO_COLLISION'\",\"c.get_collision_enabled()==unreal.CollisionEnabled.NO_COLLISION\")\n"+needle
assert entry.count(needle)==1
entry=entry.replace(needle,extra)
exec(compile(entry,str(Path(__file__)),'exec'))
