"""Correct the pure helper's missing Matrix import; keep failed V11 evidence."""
from pathlib import Path
entry=Path(__file__).with_name('blender_index_curl_v11.py')
source=entry.read_text(encoding='utf-8')
for old,new in (
    ('from mathutils import Vector, Quaternion','from mathutils import Vector, Quaternion, Matrix'),
    ("OUT=BASE/'index_curl_v11'","OUT=BASE/'index_curl_v11b'"),
    ("Path(__file__).with_name('common.py'))","Path(__file__).with_name('common.py'),entry)"),
    ('index_curl_v11_local_geometry_pass','index_curl_v11b_local_geometry_pass')):
    assert source.count(old)==1,old
    source=source.replace(old,new)
exec(compile(source,str(entry)+':v11b','exec'),globals())
