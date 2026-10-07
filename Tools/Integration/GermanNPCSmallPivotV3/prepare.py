"""User-rejected V2 correction: one small angular budget, never the full-arrow solve."""
import sys,math,struct,json,copy
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'GermanNPCGripV1'))
from common import *
V2=STORE/'Evidence/GermanNPCTriggerPivotV2'
OUT=STORE/'Evidence/GermanNPCSmallPivotV3/marked_rotation_v1'
assert not OUT.exists() and guards()==618
old=read(V2/'marked_rotation_v1/result.json')
reject=read(V2/'native_rotation_v1/result.json');assert not reject['errors']
for e in (old['v1_result'],old['v1_landmarks'],old['model']):assert sha(ROOT/e['path'])==e['sha256']
f=copy.deepcopy(old);angle=math.radians(-5);axis=f['axis_world']
q=[*(v*math.sin(angle/2) for v in axis),math.cos(angle/2)]
gun=f['source_gun_world'];pivot=f['pivot_world_cm']
new={'t':[pivot[i]+v for i,v in enumerate(tm.rotate(q,[gun['t'][i]-pivot[i] for i in range(3)]))],
     'q':tm.qmul(q,gun['q']),'s':gun['s']}
b=GLB.read_bytes();n=struct.unpack_from('<I',b,12)[0];g=json.loads(b[20:20+n]);bin_data=b[28+n:]
offset=read(ROOT/'tmp/german-rifle-ue-v1/preflight_v1.json')['native_import_offset_cm']
points=[]
for node in g['nodes']:
    if 'mesh' not in node:continue
    assert all(k not in node for k in ('matrix','rotation','scale'))
    for p in g['meshes'][node['mesh']]['primitives']:
        a=g['accessors'][p['attributes']['POSITION']];v=g['bufferViews'][a['bufferView']]
        assert a['componentType']==5126 and a['type']=='VEC3' and 'byteStride' not in v
        values=np.frombuffer(bin_data,dtype='<f4',count=a['count']*3,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,3).astype(float)
        values+=np.array(node.get('translation',[0,0,0]))
        points.extend(np.stack([values[:,2],values[:,0],values[:,1]],axis=1)*100+offset)
maximum=max(math.dist(tm.point(gun,p),tm.point(new,p)) for p in points)
assert maximum<8 and math.dist(tm.point(new,f['pivot_gun_cm']),pivot)<1e-8
stock_old=tm.point(gun,f['stock_gun_cm']);stock_new=tm.point(new,f['stock_gun_cm'])
target=f['stock_target_world_cm'];right=f['camera_right'];up=f['camera_up']
def screen_gap(p):
    delta=[p[i]-target[i] for i in range(3)]
    return math.hypot(sum(delta[i]*right[i] for i in range(3)),sum(delta[i]*up[i] for i in range(3)))
f.update({'method':'User rejects full-arrow37.6deg fit; ONE small5deg from V1, not another endpoint solve',
    'angle_deg':-5.,'new_gun_world':new,'stock_screen_gap_before_cm':screen_gap(stock_old),
    'stock_screen_gap_after_cm':screen_gap(stock_new),'whole_gun_max_vertex_displacement_cm':maximum,
    'whole_gun_vertex_count':len(points),'whole_gun_displacement_limit_cm':8,
    'v2_rejected_result':row(V2/'native_rotation_v1/result.json'),
    'renderer_template':row(ROOT/'Tools/Integration/GermanNPCTriggerPivotV2/ue_rotation.py'),
    'v2_marking_proof':row(V2/'marked_rotation_v1/result.json'),'contact_accepted':False})
assert guards()==618
write(OUT/'result.json',f)
print(json.dumps({k:f[k] for k in ('angle_deg','whole_gun_max_vertex_displacement_cm','whole_gun_vertex_count','stock_screen_gap_before_cm','stock_screen_gap_after_cm')}))
