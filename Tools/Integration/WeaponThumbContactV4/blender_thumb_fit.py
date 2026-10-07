"""Existing Rifle_Idle thumb grip, one actual upper-stock root swing; accepted index frozen."""
import sys,json,hashlib,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'WeaponTriggerAlignmentV2'))
from blender_contact_common import *
OUT=STORE/'Evidence/WeaponThumbContactV4/fit_v1';assert not OUT.exists();OUT.mkdir(parents=True)
INDEX=STORE/'Evidence/WeaponTriggerAlignmentV2/index_pose_v1/result.json'
PROBE=STORE/'Evidence/WeaponThumbContactV4/probe_v1/result.json'
inputs=[FBX,POSES,AUDIT,CALIB,TOPOLOGY,INDEX,PROBE,Path(__file__),Path(__file__).resolve().parents[1]/'WeaponTriggerAlignmentV2/blender_contact_common.py']
hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
for p in inputs[-2:]:(OUT/p.name).write_bytes(p.read_bytes())
r={'scope':__doc__,'errors':[],'phases':[],'views':[],'native_authored':False,'source_clip_modified':False,'thumb_local_rotations_only':True}
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
def inside(p,a,b,c):
    ab,ac,ap=b-a,c-a,p-a;aa=ab@ab;bb=ab@ac;cc=ac@ac;dd=ap@ab;ee=ap@ac;det=aa*cc-bb*bb
    if abs(det)<1e-10:return False
    u=(cc*dd-bb*ee)/det;v=(aa*ee-bb*dd)/det;return u>=-1e-7 and v>=-1e-7 and u+v<=1+1e-7
def sphere_triangle(a,b,c,o,radius,target):
    n=np.cross(b-a,c-a);length=np.linalg.norm(n)
    if length<1e-10:return []
    n/=length;distance=(o-a)@n
    if abs(distance)>radius:return []
    center=o-distance*n;circle=np.sqrt(max(0,radius*radius-distance*distance));direction=target-center-n*((target-center)@n);points=[]
    if np.linalg.norm(direction)>1e-10:
        q=center+circle*direction/np.linalg.norm(direction)
        if inside(q,a,b,c):points.append(q)
    for start,end in ((a,b),(b,c),(c,a)):
        edge=end-start;v=start-o;aa=edge@edge;bb=2*(edge@v);cc=v@v-radius*radius;disc=bb*bb-4*aa*cc
        if aa<1e-10 or disc<0:continue
        for t in ((-bb+np.sqrt(disc))/(2*aa),(-bb-np.sqrt(disc))/(2*aa)):
            if 0<=t<=1:points.append(start+edge*t)
    return points
def rotationpart(m):return m[:3,:3]/np.linalg.norm(m[:3,:3],axis=0)
def apply_local_rotations(b,rotations,parents):
    out=dict(b)
    for n,rotation in rotations.items():
        old=np.linalg.inv(b[parents[n]])@b[n];new=old.copy();new[:3,:3]=rotation*np.linalg.norm(old[:3,:3],axis=0)
        assert np.max(abs(old[:3,3]-new[:3,3]))==0
        out[n]=out[parents[n]]@new
    return out
def evaluate(d,b,gun):
    p=skin(d['p'],d['weights'],{n:b[n]@d['invref'][n] for n in d['invref'] if n in b})
    return transform(p,np.linalg.inv(b['hand_r']@gun))
try:
    d=load();accepted=json.loads(INDEX.read_text());probe=json.loads(PROBE.read_text());assert not probe['errors'] and probe['inputs_unchanged']
    assert not probe['thumb_index_weight_overlap_vertices'],'Thumb skin affects accepted index; stop'
    gun=np.array(accepted['gun_hand_relative_matrix']);parents=d['model']['parents'];index=('index_01_r','index_02_r','index_03_r');thumb=('thumb_01_r','thumb_02_r','thumb_03_r')
    indexrot={n:rotationpart(np.array(accepted['reused_pose']['local_transforms'][n])) for n in index}
    idle=json.loads(POSES.read_text())['clips']['owner_idle'];ib={n:mat(t) for n,t in idle['samples']['0.0']['bones_component'].items()}
    throt={n:rotationpart(np.linalg.inv(ib[parents[n]])@ib[n]) for n in thumb}
    _,b0=posed(d,'0.0');base=apply_local_rotations(b0,indexrot,parents);mature=apply_local_rotations(base,throt,parents)
    p=evaluate(d,mature,gun);tri=d['tri'];gp,gt=d['gp'],d['gt'];parts={c['id']:set(c['triangle_ids']) for c in d['topo']['components']}
    distal=np.array([w.get('thumb_03_r',0)>.6 for w in d['weights']]);ids=np.flatnonzero(np.all(distal[tri],axis=1));normal,area=normals(p,tri[ids]);sel=normal[:,2]<-.3;assert sel.any()
    ids=ids[sel];center=np.average(p[tri[ids]].mean(1),axis=0,weights=area[sel]);pad,pn,pad_id,_=project(p,tri[ids],ids,center)
    upper=np.array([x['id'] for x in probe['upper_stock_triangles']]);gn,_=normals(gp,gt)
    root=transform(np.array([mature['thumb_01_r'][:3,3]]),np.linalg.inv(base['hand_r']@gun))[0];radius=float(np.linalg.norm(pad-root))
    closest,_,_,_=project(gp,gt[upper],upper,pad);solutions=[]
    for i in upper:
        offset=gn[i]*.05
        for q in sphere_triangle(*(gp[gt[i]]+offset),root,radius,closest):solutions.append((float(np.linalg.norm(q-pad)),q,int(i)))
    assert solutions,'No actual upper-stock target reachable by this fixed thumb-root arc'
    _,target,face=min(solutions,key=lambda x:x[0]);v=pad-root;w=target-root;axis=np.cross(v,w);angle=float(np.arctan2(np.linalg.norm(axis),v@w));q=Quaternion(Vector(axis/np.linalg.norm(axis)),angle) if np.linalg.norm(axis)>1e-10 else Quaternion()
    swing=np.eye(4);swing[:3,:3]=np.array(q.to_matrix());swing[:3,3]=root-swing[:3,:3]@root
    world=base['hand_r']@gun;newroot=world@swing@np.linalg.inv(world)@mature['thumb_01_r'];rootlocal=np.linalg.inv(base[parents['thumb_01_r']])@newroot
    throt['thumb_01_r']=rotationpart(rootlocal)
    r['source_thumb_pose']={'asset':idle['asset'],'phase_s':0.0};r['landmarks']={'pad_triangle':pad_id,'pad_before_cm':pad.tolist(),'pad_normal':pn.tolist(),'stock_triangle':face,'stock_point_cm':(target-gn[face]*.05).tolist(),'offset_target_cm':target.tolist(),'root_cm':root.tolist()}
    r['root_swing_deg']=float(np.degrees(angle));r['rotation_gate_passed']=bool(np.degrees(angle)<=40);r['gun_hand_relative_matrix']=gun.tolist();r['index_rotations']= {n:rot.tolist() for n,rot in indexrot.items()};r['thumb_rotations']={n:rot.tolist() for n,rot in throt.items()};write()
    assert r['rotation_gate_passed'],'Derived root swing exceeds40deg: stop, no relaxed gate'
    indextri=tri[np.all(d['digits']['index'][tri],axis=1)];thumbmask=np.array([sum(w.get(n,0) for n in thumb)>.1 for w in d['weights']]);thumbtri=tri[np.all(thumbmask[tri],axis=1)]
    no_thumb=np.array([not any(w.get(n,0)>1e-6 for n in thumb) for w in d['weights']]);edges=np.unique(np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1),axis=0)
    evaluated={}
    for phase in d['poses']:
        _,b=posed(d,phase);beforebones=apply_local_rotations(b,indexrot,parents);new=apply_local_rotations(beforebones,throt,parents)
        before=evaluate(d,beforebones,gun);after=evaluate(d,new,gun);others=max(float(np.max(abs(new[n]-beforebones[n]))) for n in b if n not in thumb)
        idxchange=float(np.max(np.linalg.norm(after[d['digits']['index']]-before[d['digits']['index']],axis=1)));bodychange=float(np.max(np.linalg.norm(after[no_thumb]-before[no_thumb],axis=1)))
        assert others==0 and idxchange<1e-8 and bodychange<1e-8,'Accepted index/other bones/skin changed'
        tpairs=intersection_pairs(after,thumbtri,gp,gt);ipairs=intersection_pairs(after,indextri,gp,gt)
        # True pad surface from the preserved selected source triangle, not bone endpoint.
        actual,_,_,_=project(after,tri[[pad_id]],np.array([pad_id]),after[tri[pad_id]].mean(0));point,n,tid,dist=project(gp,gt[upper],upper,actual)
        oldlen=np.linalg.norm(before[edges[:,1]]-before[edges[:,0]],axis=1);newlen=np.linalg.norm(after[edges[:,1]]-after[edges[:,0]],axis=1);severe=int(np.sum((newlen>3*np.maximum(oldlen,1e-8))&(newlen-oldlen>2)))
        row={'phase_s':float(phase),'non_thumb_bone_delta':others,'accepted_index_vertex_delta_cm':idxchange,'non_thumb_influenced_skin_delta_cm':bodychange,
          'thumb_all_crossing_triangles':len({i for i,j in tpairs}),'thumb_stock_crossing_triangles':len({i for i,j in tpairs if j in parts[0]}),
          'index_stock_crossing_triangles':len({i for i,j in ipairs if j in parts[0]}),'index_guard_crossing_triangles':len({i for i,j in ipairs if j in parts[4]}),'index_trigger_crossing_triangles':len({i for i,j in ipairs if j in parts[5]}),
          'pad_to_upper_stock_cm':dist,'pad_gun_cm':actual.tolist(),'stock_nearest_triangle':tid,'new_severe_edges':severe,'max_edge_extra_length_cm':float(np.max(newlen-oldlen))}
        r['phases'].append(row);evaluated[phase]=(before,after);write()
    r['early_contact_gate_passed']=all(x['thumb_all_crossing_triangles']==0 and x['new_severe_edges']==0 and x['pad_to_upper_stock_cm']<.15 for x in r['phases']);write()
    # Render failed evidence too; no further parameter iterations or native save.
    scene=setup_scene();grey=material('Gun',(.14,.17,.20));metal=material('Trigger',(.15,.65,.7));tan=material('Right hand',(.62,.42,.27));orange=material('Protected index',(1,.22,.04));green=material('Thumb contact',(.15,.75,.27));blue=material('Left support',(.18,.45,.65))
    objgun=mesh('Frozen accepted M1 fit',gp,gt,[grey,metal])
    for i in parts[5]:objgun.data.polygons[i].material_index=1
    rt=tri[np.all(d['masks']['r'][tri],axis=1)];lt=tri[np.all(d['masks']['l'][tri],axis=1)];visible=[]
    camcenter=(target+root)*.005
    for phase in ('0.0','2.2','4.1'):
        for condition,points in zip(('accepted_index_before','thumb_contact_v4'),evaluated[phase]):
            for o in visible:bpy.data.objects.remove(o,do_unlink=True)
            hand=mesh('Right hand '+condition,points,rt,[tan,orange,green]);left=mesh('Left hand unchanged',points,lt,[blue]);visible=[hand,left]
            for poly,f in zip(hand.data.polygons,rt):poly.material_index=1 if np.all(d['digits']['index'][f]) else 2 if np.all(thumbmask[f]) else 0
            for view,targetpoint,offset,scale in [('right',camcenter,(.28,-.05,.10),.26),('left',camcenter,(-.28,-.05,.10),.26),('top',camcenter,(.02,-.04,.30),.26),('rear_three_quarter',camcenter,(-.20,-.25,.20),.28),('whole',[0,.22,0],(-1.2,.05,.4),1.2)]:
                camera(targetpoint,offset,scale);file=f'{phase}_{condition}_{view}.png';scene.render.filepath=str(OUT/file);bpy.ops.render.render(write_still=True);r['views'].append({'file':file,'phase_s':float(phase),'condition':condition,'view':view});write()
            if condition=='thumb_contact_v4':
                hand.hide_render=True;left.hide_render=True;full=mesh('Whole source arms',points,tri,[tan]);visible.append(full)
                camera([0,.12,-.10],(-1.2,-.1,.45),1.2);file=f'{phase}_{condition}_full_arms.png';scene.render.filepath=str(OUT/file);bpy.ops.render.render(write_still=True);full.hide_render=True;hand.hide_render=False;left.hide_render=False;r['views'].append({'file':file,'phase_s':float(phase),'condition':condition,'view':'full_arms'});write()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'ThumbStockContact.blend'));r['status']='bounded_thumb_comparison_collected_pending_visual_inspection' if r['early_contact_gate_passed'] else 'stopped_at_thumb_contact_gate_evidence_preserved'
except Exception:r['status']='stopped';r['errors'].append(traceback.format_exc())
finally:r['inputs_unchanged']=all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in hashes.items());r['input_hashes']=hashes;write();print(json.dumps({k:r[k] for k in ('status','errors','inputs_unchanged')}))
