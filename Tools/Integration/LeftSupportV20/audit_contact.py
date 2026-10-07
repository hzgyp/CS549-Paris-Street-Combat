"""Read-only accepted grip support-surface audit, no authored candidate."""
import hashlib,json,sys,traceback
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/WeaponTriggerPivotV12'))
from pivot_common import load,evaluate,guarded_files,STORE,normals
SOURCE=STORE/'Evidence/WeaponPinkyLengthV18/distal_v1'
OUT=STORE/'Evidence/LeftSupportV20/audit_v1'
assert not OUT.exists();OUT.mkdir(parents=True)
r={'errors':[],'candidate_authored':False,'scope':__doc__,'renders':[]}
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
try:
    r['guards_before']=guarded_files();assert not r['guards_before']['mismatches']
    blend=SOURCE/'RightPinkyDistalShorter.blend'
    r['source_sha256']=hashlib.sha256(blend.read_bytes()).hexdigest()
    assert r['source_sha256']=='7a1d0520b11e7d9c8d29377c46909cfa2b65fea39254789e28eff083de404219'
    d=load();weights=d['weights'];tri=d['tri'];palm=np.array([w.get('hand_l',0)>.8 for w in weights])
    bpy.ops.wm.open_mainfile(filepath=str(blend),load_ui=False,use_scripts=False)
    arms=bpy.data.objects['Frozen V16 continuous arms'];gun=bpy.data.objects['Frozen V16 M1']
    p=np.array([list(arms.matrix_world@v.co) for v in arms.data.vertices])*100
    gp=np.array([list(gun.matrix_world@v.co) for v in gun.data.vertices])*100
    gt=np.array([list(poly.vertices) for poly in gun.data.polygons],int)
    assert len(p)==len(weights) and len(gt)==len(d['gt'])
    stockids=np.array(next(c['triangle_ids'] for c in d['topo']['components'] if c['id']==0),int)
    tree=BVHTree.FromPolygons([Vector(v) for v in gp],gt[stockids].tolist(),all_triangles=True)
    # Diagnostic objects carry reflection-corrected winding, unlike immutable
    # native triangle arrays. Use their actual surface normals here.
    facing=np.cross(p[tri[:,1]]-p[tri[:,0]],p[tri[:,2]]-p[tri[:,0]])
    facing=-facing/np.maximum(np.linalg.norm(facing,axis=1)[:,None],1e-12)
    rows=[]
    for fid in np.flatnonzero(np.all(palm[tri],axis=1)):
        center=p[tri[fid]].mean(0)
        q,n,i,gap=tree.find_nearest(Vector(center))
        q,n=np.array(q),np.array(n)
        rows.append({'palm_triangle':int(fid),'stock_triangle':int(stockids[i]),
                     'palm_point_cm':center.tolist(),'stock_point_cm':q.tolist(),
                     'stock_normal':n.tolist(),'palm_normal':facing[fid].tolist(),
                     'gap_cm':float(gap),'signed_gap_cm':float((center-q)@n),
                     'opposition':float(facing[fid]@n)})
    rows.sort(key=lambda x:x['gap_cm'])
    r['pure_palm_surface_samples']=rows
    r['palm_vertices']=int(palm.sum())
    r['nearest_palm_samples']=rows[:12]
    center=np.mean(p[palm],axis=0)/100
    r['diagnostic_center_m']=center.tolist()
    # Existing frozen inspection objects only; full continuous mesh retained.
    right=bpy.data.objects['Fixed right raised_v16 original-textured']
    support=bpy.data.objects['Support raised_v16 original-textured']
    arms.hide_render=True;right.hide_render=False;support.hide_render=False
    scene=bpy.context.scene;scene.render.resolution_x=1000;scene.render.resolution_y=800
    scene.render.resolution_percentage=100
    for name,offset in [('left_side',(.5,0,.05)),('left_reverse',(-.5,0,.05)),('left_under',(0,0,-.5)),('left_top',(0,0,.5))]:
        cd=bpy.data.cameras.new(name);cd.type='ORTHO';cd.ortho_scale=.28;cd.clip_start=.001
        cam=bpy.data.objects.new(name,cd);scene.collection.objects.link(cam)
        cam.location=Vector(center)+Vector(offset)
        cam.rotation_euler=(Vector(center)-cam.location).to_track_quat('-Z','Y').to_euler()
        scene.camera=cam;scene.render.filepath=str(OUT/(name+'.png'))
        bpy.ops.render.render(write_still=True);r['renders'].append(name+'.png');write()
    arms.hide_render=False;right.hide_render=True;support.hide_render=True
    scene.camera=bpy.data.objects['whole_arms_context']
    scene.render.filepath=str(OUT/'whole_arms.png');bpy.ops.render.render(write_still=True)
    r['renders'].append('whole_arms.png')
    assert hashlib.sha256(blend.read_bytes()).hexdigest()==r['source_sha256']
    r['status']='read_only_contact_views_require_review'
except Exception:r['errors'].append(traceback.format_exc());r['status']='stopped'
finally:
    r['guards_after']=guarded_files();write()
    print(json.dumps({k:r.get(k) for k in ['status','errors','palm_vertices','nearest_palm_samples','guards_after']}),flush=True)
    if r['errors'] or r['guards_after']['mismatches']:raise SystemExit(1)
