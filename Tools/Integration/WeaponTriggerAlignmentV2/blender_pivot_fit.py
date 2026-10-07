"""One actual-surface two-contact rigid solve: trigger pivot and supporting palm."""
import sys,json,hashlib,traceback,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from blender_contact_common import *
OUT=STORE/'Evidence/WeaponTriggerAlignmentV2'/os.environ.get('CS549_PIVOT_ID','pivot_fit_v2');assert not OUT.exists();OUT.mkdir(parents=True)
inputs=[FBX,POSES,AUDIT,CALIB,TOPOLOGY,V1,Path(__file__),Path(__file__).with_name('blender_contact_common.py')]
hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
for p in inputs[-2:]:(OUT/p.name).write_bytes(p.read_bytes())
r={'scope':__doc__,'errors':[],'phases':[],'views':[],'native_modified':False,'hand_modified':False,'finger_modified':False}
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
def inside(p,a,b,c):
    ab,ac,ap=b-a,c-a,p-a;aa=np.dot(ab,ab);bb=np.dot(ab,ac);cc=np.dot(ac,ac);dd=np.dot(ap,ab);ee=np.dot(ap,ac);det=aa*cc-bb*bb
    if abs(det)<1e-10:return False
    u=(cc*dd-bb*ee)/det;v=(aa*ee-bb*dd)/det;return u>=-1e-7 and v>=-1e-7 and u+v<=1+1e-7
def sphere_triangle(a,b,c,o,radius,target):
    n=np.cross(b-a,c-a);length=np.linalg.norm(n)
    if length<1e-10:return []
    n/=length;distance=np.dot(o-a,n)
    if abs(distance)>radius:return []
    center=o-distance*n;circle=np.sqrt(max(0,radius*radius-distance*distance));direction=target-center-n*np.dot(target-center,n)
    points=[]
    if np.linalg.norm(direction)>1e-10:
        q=center+circle*direction/np.linalg.norm(direction)
        if inside(q,a,b,c):points.append(q)
    for start,end in ((a,b),(b,c),(c,a)):
        edge=end-start;v=start-o;aa=np.dot(edge,edge);bb=2*np.dot(edge,v);cc=np.dot(v,v)-radius*radius;disc=bb*bb-4*aa*cc
        if aa<1e-10 or disc<0:continue
        for t in ((-bb+np.sqrt(disc))/(2*aa),(-bb-np.sqrt(disc))/(2*aa)):
            if 0<=t<=1:points.append(start+edge*t)
    return points
try:
    d=load();gp,gt=d['gp'],d['gt'];old=d['relative'];v1=json.loads(V1.read_text())
    pt,b=posed(d,'2.2');local=transform(pt,np.linalg.inv(b['hand_r']@old))
    # Reidentify actual front/pad surfaces after the single parity correction;
    # earlier V1 selected opposite surfaces from a raw mirrored cross product.
    ids=np.array(next(c for c in d['topo']['components'] if c['id']==5)['triangle_ids']);n,a=normals(gp,gt[ids]);centers=gp[gt[ids]].mean(1);choose=(n[:,1]>.35)&(centers[:,2]<-1)
    assert choose.any();ids=ids[choose];center=np.average(centers[choose],axis=0,weights=a[choose]);trigger,tn,trigger_id,_=project(gp,gt[ids],ids,center)
    distal=np.array([w.get('index_03_r',0)>.5 for w in d['weights']]);ids=np.flatnonzero(np.all(distal[d['tri']],axis=1));n,a=normals(local,d['tri'][ids]);choose=n[:,1]<-.35
    assert choose.any();ids=ids[choose];center=np.average(local[d['tri'][ids]].mean(1),axis=0,weights=a[choose]);pad,pn,pad_id,_=project(local,d['tri'][ids],ids,center)
    r['coordinate_reflection_determinant']=d['coordinate_determinant'];r['surface_normal_parity_corrected']=True
    # Nominal contact margin along actual blade normal, preserving source pose.
    base=old.copy();delta=pad-trigger-tn*.03;base[:3,3]+=old[:3,:3]@delta
    pt0,b0=posed(d,'0.0');startlocal=transform(pt0,np.linalg.inv(b0['hand_r']@old))
    palm_weight=np.array([w.get('hand_l',0)>.6 for w in d['weights']]);palm_ids=np.flatnonzero(np.all(palm_weight[d['tri']],axis=1))
    normal,area=normals(startlocal,d['tri'][palm_ids]);select=normal[:,2]>.35;assert select.any(),'No upper-facing support palm faces'
    palm_ids=palm_ids[select];centers=startlocal[d['tri'][palm_ids]].mean(1);center=np.average(centers,axis=0,weights=area[select])
    palm,n,palm_id,_=project(startlocal,d['tri'][palm_ids],palm_ids,center)
    # A physical bottom-stock contact sits .3mm above the actual palm surface.
    palm_hand=(old@np.r_[palm,1])[:3];support_target=palm_hand+old[:3,:3]@np.array([0,0,.03])
    desired=(np.linalg.inv(base)@np.r_[support_target,1])[:3]
    radius=float(np.linalg.norm(desired-trigger));stock=next(c for c in d['topo']['components'] if c['id']==0)
    stock_ids=np.array(stock['triangle_ids']);sn,sa=normals(gp,gt[stock_ids]);sc=gp[gt[stock_ids]].mean(1)
    stock_ids=stock_ids[(sn[:,2]<-.3)&(sc[:,1]>trigger[1]+5)]
    points=[]
    for idx in stock_ids:
        points.extend((float(np.linalg.norm(q-desired)),q,int(idx)) for q in sphere_triangle(*gp[gt[idx]],trigger,radius,desired))
    assert points,'Actual lower fore-end has no sphere contact solution'
    _,stock_point,stock_id=min(points,key=lambda x:x[0]);a=stock_point-trigger;bv=desired-trigger
    axis=np.cross(a,bv);angle=float(np.arctan2(np.linalg.norm(axis),np.dot(a,bv)));q=Quaternion(Vector(axis/np.linalg.norm(axis)),angle) if np.linalg.norm(axis)>1e-10 else Quaternion()
    rotation=np.array(q.to_matrix());candidate=base.copy();candidate[:3,:3]=base[:3,:3]@rotation
    pivot=(base@np.r_[trigger,1])[:3];candidate[:3,3]=pivot-candidate[:3,:3]@trigger
    support_error=np.linalg.norm((candidate@np.r_[stock_point,1])[:3]-support_target)
    r['landmarks']={'trigger_triangle_id':trigger_id,'trigger_gun_cm':trigger.tolist(),'trigger_normal':tn.tolist(),'pad_source_triangle_id':pad_id,'pad_original_gun_cm':pad.tolist(),'pad_normal':pn.tolist(),
      'support_palm_source_triangle_id':palm_id,'support_palm_original_gun_cm':palm.tolist(),'support_palm_normal':n.tolist(),'stock_contact_triangle_id':stock_id,'stock_contact_gun_cm':stock_point.tolist(),
      'method':'Actual projected surfaces; sphere/triangle intersection then one minimal-arc rotation, no transform sweep'}
    r['candidate']={'old_hand_relative_matrix':old.tolist(),'translation_only_reprojected_matrix':base.tolist(),'new_hand_relative_matrix':candidate.tolist(),'rotation_from_trigger_translation_deg':float(np.degrees(angle)),
      'support_contact_position_error_cm':float(support_error),'trigger_pivot_error_cm':float(np.linalg.norm((candidate@np.r_[trigger,1])[:3]-pivot)),'scale_unchanged':True}
    r['rotation_gate_passed']=bool(np.degrees(angle)<=15);write()
    assert r['rotation_gate_passed'],'Derived rotation exceeds15deg; stop this candidate, do not relax'
    scene=setup_scene();grey=material('Actual gun',(.14,.17,.20));metal=material('Trigger',(.15,.65,.7));tan=material('Right hand',(.62,.42,.27));orange=material('Right index',(1,.22,.04));blue=material('Left support',(.18,.45,.65))
    gun=mesh('Unchanged M1',gp,gt,[grey,metal]);triggerids=set(next(c for c in d['topo']['components'] if c['id']==5)['triangle_ids'])
    guardids=set(next(c for c in d['topo']['components'] if c['id']==4)['triangle_ids']);stockids=set(stock['triangle_ids'])
    for i in triggerids:gun.data.polygons[i].material_index=1
    rtri=d['tri'][np.all(d['masks']['r'][d['tri']],axis=1)];ltri=d['tri'][np.all(d['masks']['l'][d['tri']],axis=1)]
    idxtri=d['tri'][np.all(d['digits']['index'][d['tri']],axis=1)]
    visible=[]
    for phase in ('0.0','2.2','4.1'):
        pt,b=posed(d,phase);row={'phase_s':float(phase),'conditions':{}}
        transforms={'original':old,'translation_v1':np.array(v1['candidate']['new_hand_relative_matrix']),'pivot_v2':candidate}
        locals={k:transform(pt,np.linalg.inv(b['hand_r']@t)) for k,t in transforms.items()}
        center=np.mean(locals['pivot_v2'][d['digits']['index']],axis=0)*.01
        for condition,p in locals.items():
            pairs=intersection_pairs(p,idxtri,gp,gt)
            row['conditions'][condition]={'index_stock_crossing_triangles':len({i for i,j in pairs if j in stockids}),'index_guard_crossing_triangles':len({i for i,j in pairs if j in guardids}),
              'index_trigger_crossing_triangles':len({i for i,j in pairs if j in triggerids}),'index_all_crossing_triangles':len({i for i,j in pairs})}
            for o in visible:bpy.data.objects.remove(o,do_unlink=True)
            hand=mesh('Unmodified right hand',p,rtri,[tan,orange]);left=mesh('Unmodified left hand',p,ltri,[blue]);visible=[hand,left]
            for poly,f in zip(hand.data.polygons,rtri):poly.material_index=int(np.all(d['digits']['index'][f]))
            views=[('right',center,(.28,-.05,.10),.26),('left',center,(-.28,-.05,.10),.26),('top',center,(.02,-.04,.30),.26),('whole',[0,.22,0],(-1.2,.05,.4),1.2)]
            for view,target,offset,scale in views:
                camera(target,offset,scale);file=f'{phase}_{condition}_{view}.png';scene.render.filepath=str(OUT/file);bpy.ops.render.render(write_still=True);r['views'].append({'file':file,'phase_s':float(phase),'condition':condition,'view':view});write()
            if condition=='pivot_v2':
                left.hide_render=True;camera(center,(-.28,-.05,-.08),.24);file=f'{phase}_{condition}_right_contact_only.png';scene.render.filepath=str(OUT/file);bpy.ops.render.render(write_still=True);left.hide_render=False;r['views'].append({'file':file,'phase_s':float(phase),'condition':condition,'view':'right_contact_only'});write()
                hand.hide_render=True;left.hide_render=True;full=mesh('Whole unchanged arms',p,d['tri'],[tan]);visible.append(full)
                camera([0,.12,-.10],(-1.2,-.1,.45),1.2);file=f'{phase}_{condition}_full_arms.png';scene.render.filepath=str(OUT/file);bpy.ops.render.render(write_still=True);full.hide_render=True;hand.hide_render=False;left.hide_render=False;r['views'].append({'file':file,'phase_s':float(phase),'condition':condition,'view':'full_arms'});write()
        r['phases'].append(row);write()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'TriggerPivotCandidate.blend'));r['status']='one_rigid_surface_pivot_solve_collected_requires_inspection'
except Exception:r['status']='stopped';r['errors'].append(traceback.format_exc())
finally:
    r['inputs_unchanged']=all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in hashes.items());r['input_hashes']=hashes;write();print(json.dumps({k:r[k] for k in ('status','errors','inputs_unchanged')}))
