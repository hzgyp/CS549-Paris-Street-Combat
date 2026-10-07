"""Marked fingertip only: existing distal curl with index root untouched."""
from pathlib import Path
entry=Path(__file__).with_name('blender_index_curl_v11.py')
source=entry.read_text(encoding='utf-8')
changes={
    'from mathutils import Vector, Quaternion':'from mathutils import Vector, Quaternion, Matrix',
    "OUT=BASE/'index_curl_v11'":"OUT=BASE/'index_curl_v11c'",
    "Path(__file__).with_name('common.py'))":"Path(__file__).with_name('common.py'),entry)",
    'index_curl_v11_local_geometry_pass':'index_curl_v11c_local_geometry_pass',
    "for clip in ('owner_idle','owner_reload'):":"for clip in ('owner_reload',):",
    "for phase,sample in poses['clips'][clip]['samples'].items():":"for phase,sample in poses['clips'][clip]['samples'].items():\n            if phase!='2.2':continue\n            for distal_mode in ('tip_only','two_distal'):",
}
for old,new in changes.items():
    assert source.count(old)==1,old
    source=source.replace(old,new)
# Nest the bounded interpolation loop under the two explicit distal scopes.
start=source.index('            src={n:mat(t)')
end=source.index('    assert best is not None',start)
source=source[:start]+''.join('    '+line if line.strip() else line for line in source[start:end].splitlines(keepends=True))+source[end:]
old='q=qb.slerp(qs,strength);local[:3,:3]=np.array(q.to_matrix(),float)*scale'
new="q=qb if n=='index_01_r' or (distal_mode=='tip_only' and n=='index_02_r') else qb.slerp(qs,strength)\n                        local[:3,:3]=np.array(q.to_matrix(),float)*scale"
assert source.count(old)==1;source=source.replace(old,new)
start=source.index('                    direction0=')
end=source.index('                    row=',start)
source=source[:start]+'''                    oldq=Quaternion(tuple(encode(bones['index_03_r'])['q'][j] for j in (3,0,1,2)))
                    newq=Quaternion(tuple(encode(candidate['index_03_r'])['q'][j] for j in (3,0,1,2)))
                    bend=math.degrees(oldq.rotation_difference(newq).angle)
'''+source[end:]
source=source.replace("'strength':strength,","'strength':strength,'distal_mode':distal_mode,")
source=source.replace('bend>=10','bend>=5')
exec(compile(source,str(entry)+':v11c','exec'),globals())
