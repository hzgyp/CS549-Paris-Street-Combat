"""Select actual underside toward fixed left palm, not camera-facing wood."""
import sys
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).parent))
from common import *
sys.path.insert(0,str(ROOT/'Tools/Integration/WeaponTriggerAlignmentV2'))
from blender_contact_common import mat,transform
import marked_web_math as fitting
import transform_math as tm

out=BASE/'marked_web_surface_v6c'
assert not out.exists()
out.mkdir(parents=True)
oldpath=BASE/'marked_web_measure_v6b/result.json'
geompath=BASE/'marked_web_measure_v6b/source_geometry.npz'
old=read(oldpath)
assert not old['errors'] and old['inputs_unchanged'] and old['guards_after']==611
previous=read(BASE/'fit_v5/result.json')
g=np.load(geompath)
marks=old['landmarks']
web=np.array(tm.point(previous['after']['bones']['hand_r'],marks['right_web_region']['hand_local_cm']))
neck=np.array(tm.point(previous['after']['gun_world'],marks['stock_neck_region']['gun_local_cm']))
delta=web-neck
delta[1]=0
assert delta[0]<0 and delta[2]<0 and np.linalg.norm(delta)<=4
points=transform(g['gun_local_cm'],mat(previous['after']['gun_world']))+delta
origin=points.mean(0)
stockids=next(c['triangle_ids'] for c in read(STORE/'Evidence/WeaponTriggerAlignmentV1/topology_v1/result.json')['components'] if c['id']==0)
tree=BVHTree.FromPolygons([Vector(x) for x in points-origin],g['gun_triangles'][stockids].tolist(),all_triangles=True)
palm=np.array(marks['left_palm_region']['world_cm'])
target=palm+np.array([0,0,.15])
loc,normal,index,gap=tree.find_nearest(Vector(target-origin))
assert loc is not None
loc=np.array(loc)+origin
gunlocal=tm.inverse_point(previous['after']['gun_world'],(loc-delta).tolist())
# It must be the forward stock region, not butt/neck/trigger or a new part.
assert 10<gunlocal[1]<35
result={**old,'status':'marked_regions_and_actual_foreend_measured','errors':[],
    'landmarks':{**marks,'foreend_lower_region':{'world_cm':(loc-delta).tolist(),
        'gun_local_cm':gunlocal,'triangle':int(stockids[index]),
        'selection':'actual stock underside nearest left palm after seating',
        'gap_after_seating_cm':float(gap)}},
    'input_hashes':{p.relative_to(ROOT).as_posix():sha(p) for p in (oldpath,geompath,Path(__file__))},
    'guards_before':guards(),'guards_after':guards(),'inputs_unchanged':True}
write(out/'result.json',result)
print(result['landmarks']['foreend_lower_region'])
