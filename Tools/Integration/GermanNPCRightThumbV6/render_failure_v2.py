"""Diagnostic world initialization only; keep failed contact/previous render receipt."""
from pathlib import Path
source=Path(__file__).with_name('render_failure.py').read_text(encoding='utf-8-sig')
source=source.replace("OUT=BASE/'failure_views_v1'","OUT=BASE/'failure_views_v2'")
needle="scene.world.color=(.055,.07,.085)"
assert source.count(needle)==1
source=source.replace(needle,"scene.world=bpy.data.worlds.new('DiagnosticWorld');"+needle)
exec(compile(source,str(Path(__file__)),'exec'))
