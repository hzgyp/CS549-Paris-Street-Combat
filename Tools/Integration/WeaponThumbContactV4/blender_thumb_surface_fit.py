"""One full evaluated-thumb envelope root solve, not pad-point/angle-grid fitting."""
import sys,json,hashlib,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'WeaponTriggerAlignmentV2'))
from blender_contact_common import *
OUT=STORE/'Evidence/WeaponThumbContactV4/fit_v2';assert not OUT.exists();OUT.mkdir(parents=True)
INDEX=STORE/'Evidence/WeaponTriggerAlignmentV2/index_pose_v1/result.json'
PROBE=STORE/'Evidence/WeaponThumbContactV4/probe_v1/result.json'
V4=STORE/'Evidence/WeaponThumbContactV4/fit_v1/result.json'
inputs=[FBX,POSES,AUDIT,CALIB,TOPOLOGY,INDEX,PROBE,V4,Path(__file__),Path(__file__).resolve().parents[1]/'WeaponTriggerAlignmentV2/blender_contact_common.py']
hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
for p in inputs[-2:]:(OUT/p.name).write_bytes(p.read_bytes())
r={'scope':__doc__,'errors':[],'phases':[],'views':[],'native_authored':False,'source_clip_modified':False,'thumb_only':True,'envelope_solver_observations':[]}
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
def rot(m):return m[:3,:3]/np.linalg.norm(m[:3,:3],axis=0)
def apply(b,rotations,parents):
    new=dict(b)
    for n,rotation in rotations.items():
        local=np.linalg.inv(b[parents[n]])@b[n];local[:3,:3]=rotation*np.linalg.norm(local[:3,:3],axis=0);new[n]=new[parents[n]]@local
    return new
def evaluate(d,b,gun):return transform(skin(d['p'],d['weights'],{n:b[n]@d['invref'][n] for n in d['invref'] if n in b}),np.linalg.inv(b['hand_r']@gun))
try:
    d=load();accepted=json.loads(INDEX.read_text());probe=json.loads(PROBE.read_text());v4=json.loads(V4.read_text());assert not probe['thumb_index_weight_overlap_vertices']
    gun=np.array(accepted['gun_hand_relative_matrix']);parents=d['model']['parents'];index=('index_01_r','index_02_r','index_03_r');thumb=('thumb_01_r','thumb_02_r','thumb_03_r');indexrot={n:rot(np.array(accepted['reused_pose']['local_transforms'][n])) for n in index}
    idle=json.loads(POSES.read_text())['clips']['owner_idle'];ib={n:mat(t) for n,t in idle['samples']['0.0']['bones_component'].items()};mature_rot={n:rot(np.linalg.inv(ib[parents[n]])@ib[n]) for n in thumb}
    _,b0=posed(d,'0.0');base=apply(b0,indexrot,parents);mature=apply(base,mature_rot,parents);world=base['hand_r']@gun;invworld=np.linalg.inv(world)
    root=np.array(v4['landmarks']['root_cm']);a=np.array(v4['landmarks']['pad_before_cm'])-root;b=np.array(v4['landmarks']['offset_target_cm'])-root;axis=np.cross(a,b);axis/=np.linalg.norm(axis)
    gp,gt=d['gp'],d['gt'];tri=d['tri'];parts={c['id']:set(c['triangle_ids']) for c in d['topo']['components']};upper=np.array([x['id'] for x in probe['upper_stock_triangles']]);upper_tree=BVHTree.FromPolygons([Vector(q) for q in gp],gt[upper].tolist(),all_triangles=True)
    thumbmask=np.array([sum(w.get(n,0) for n in thumb)>.1 for w in d['weights']]);thumbids=np.where(thumbmask)[0];distalmask=np.array([w.get('thumb_03_r',0)>.6 for w in d['weights']]);distalids=np.where(distalmask)[0]
    def rootrotation(angle):
        swing=np.eye(4);swing[:3,:3]=np.array(Quaternion(Vector(axis),angle).to_matrix());swing[:3,3]=root-swing[:3,:3]@root
        newroot=world@swing@invworld@mature['thumb_01_r'];return rot(np.linalg.inv(base[parents['thumb_01_r']])@newroot)
    def clearance(angle):
        rots=dict(mature_rot);rots['thumb_01_r']=rootrotation(angle);points=evaluate(d,apply(base,rots,parents),gun);records=[]
        for i in thumbids:
            p=points[i]
            # Local envelope only near the actual rear stock. Far root/web points
            # cannot be classified as inside from an open upper-surface normal.
            if abs(p[0])>4 or not -18<p[1]<4:continue
            loc,n,idx,distance=upper_tree.find_nearest(Vector(p));normal=-np.array(n);signed=float((p-np.array(loc))@normal)
            if distance<3:records.append((signed,int(i),int(upper[idx]),float(distance)))
        assert records,'No thumb envelope points near inspected stock'
        minimum=min(records,key=lambda x:x[0]);r['envelope_solver_observations'].append({'angle_deg':float(np.degrees(angle)),'min_local_normal_clearance_cm':minimum[0],'vertex':minimum[1],'stock_triangle':minimum[2]})
        return minimum[0]-.05,rots,points,minimum
    low=np.radians(v4['root_swing_deg']);high=np.radians(40);fl,*_=clearance(low);fh,*_=clearance(high);write()
    assert fl<0 and fh>=0,'Whole-thumb envelope has no fixed-axis root before40deg; stop'
    # Geometric contact root; no render/pose grid or relaxed margins.
    for iteration in range(30):
        mid=(low+high)*.5;fm,*_=clearance(mid)
        if fm<0:low=mid
        else:high=mid
        if np.degrees(high-low)<1e-5:break
    final=high;residual,thumbrot,_,constraint=clearance(final);r['root_swing_deg']=float(np.degrees(final));r['active_contact_constraint']={'vertex':constraint[1],'stock_triangle':constraint[2],'local_normal_clearance_cm':constraint[0]};r['thumb_rotations']={n:x.tolist() for n,x in thumbrot.items()};r['gun_hand_relative_matrix']=gun.tolist();r['index_rotations']={n:x.tolist() for n,x in indexrot.items()};write()
    thumbtri=tri[np.all(thumbmask[tri],axis=1)];indextri=tri[np.all(d['digits']['index'][tri],axis=1)];no_thumb=np.array([not any(w.get(n,0)>1e-6 for n in thumb) for w in d['weights']]);edges=np.unique(np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1),axis=0)
    evaluated={}
    for phase in d['poses']:
        _,b=posed(d,phase);beforeb=apply(b,indexrot,parents);new=apply(beforeb,thumbrot,parents);before=evaluate(d,beforeb,gun);after=evaluate(d,new,gun)
        others=max(float(np.max(abs(new[n]-beforeb[n]))) for n in b if n not in thumb);idxdelta=float(np.max(np.linalg.norm(after[d['digits']['index']]-before[d['digits']['index']],axis=1)));bodydelta=float(np.max(np.linalg.norm(after[no_thumb]-before[no_thumb],axis=1)));assert others==0 and idxdelta<1e-8 and bodydelta<1e-8
        tpairs=intersection_pairs(after,thumbtri,gp,gt);ipairs=intersection_pairs(after,indextri,gp,gt)
        distances=[(upper_tree.find_nearest(Vector(after[i]))[3],int(i)) for i in distalids];gap,contact_id=min(distances)
        padid=v4['landmarks']['pad_triangle'];actual,_,_,_=project(after,tri[[padid]],np.array([padid]),after[tri[padid]].mean(0));_,_,_,centergap=project(gp,gt[upper],upper,actual)
        oldlen=np.linalg.norm(before[edges[:,1]]-before[edges[:,0]],axis=1);newlen=np.linalg.norm(after[edges[:,1]]-after[edges[:,0]],axis=1);severe=int(np.sum((newlen>3*np.maximum(oldlen,1e-8))&(newlen-oldlen>2)))
        r['phases'].append({'phase_s':float(phase),'non_thumb_bone_delta':others,'accepted_index_vertex_delta_cm':idxdelta,'non_thumb_influenced_skin_delta_cm':bodydelta,'thumb_all_crossing_triangles':len({i for i,j in tpairs}),'thumb_stock_crossing_triangles':len({i for i,j in tpairs if j in parts[0]}),'index_stock_crossing_triangles':len({i for i,j in ipairs if j in parts[0]}),'index_guard_crossing_triangles':len({i for i,j in ipairs if j in parts[4]}),'index_trigger_crossing_triangles':len({i for i,j in ipairs if j in parts[5]}),'closest_distal_vertex_to_upper_stock_cm':float(gap),'closest_distal_vertex':contact_id,'old_selected_pad_centre_gap_cm':centergap,'new_severe_edges':severe,'max_edge_extra_length_cm':float(np.max(newlen-oldlen))});evaluated[phase]=(before,after);write()
    r['early_contact_gate_passed']=all(x['thumb_all_crossing_triangles']==0 and x['new_severe_edges']==0 and x['closest_distal_vertex_to_upper_stock_cm']<.15 for x in r['phases']);write()
    scene=setup_scene();grey=material('Gun',(.14,.17,.20));metal=material('Trigger',(.15,.65,.7));tan=material('Right hand',(.62,.42,.27));orange=material('Protected index',(1,.22,.04));green=material('Thumb contact',(.15,.75,.27));blue=material('Left support',(.18,.45,.65));objgun=mesh('Frozen accepted M1 fit',gp,gt,[grey,metal])
    for i in parts[5]:objgun.data.polygons[i].material_index=1
    rt=tri[np.all(d['masks']['r'][tri],axis=1)];lt=tri[np.all(d['masks']['l'][tri],axis=1)];visible=[];camcenter=(root+np.array(v4['landmarks']['offset_target_cm']))*.005
    for phase in ('0.0','2.2','4.1'):
        for condition,points in zip(('accepted_index_before','thumb_surface_v5'),evaluated[phase]):
            for o in visible:bpy.data.objects.remove(o,do_unlink=True)
            hand=mesh('Right hand '+condition,points,rt,[tan,orange,green]);left=mesh('Left hand unchanged',points,lt,[blue]);visible=[hand,left]
            for poly,f in zip(hand.data.polygons,rt):poly.material_index=1 if np.all(d['digits']['index'][f]) else 2 if np.all(thumbmask[f]) else 0
            for view,target,offset,scale in [('right',camcenter,(.28,-.05,.10),.26),('left',camcenter,(-.28,-.05,.10),.26),('top',camcenter,(.02,-.04,.30),.26),('rear_three_quarter',camcenter,(-.20,-.25,.20),.28),('whole',[0,.22,0],(-1.2,.05,.4),1.2)]:
                camera(target,offset,scale);file=f'{phase}_{condition}_{view}.png';scene.render.filepath=str(OUT/file);bpy.ops.render.render(write_still=True);r['views'].append({'file':file,'phase_s':float(phase),'condition':condition,'view':view});write()
            if condition=='thumb_surface_v5':
                hand.hide_render=True;left.hide_render=True;full=mesh('Whole source arms',points,tri,[tan]);visible.append(full);camera([0,.12,-.10],(-1.2,-.1,.45),1.2);file=f'{phase}_{condition}_full_arms.png';scene.render.filepath=str(OUT/file);bpy.ops.render.render(write_still=True);full.hide_render=True;hand.hide_render=False;left.hide_render=False;r['views'].append({'file':file,'phase_s':float(phase),'condition':condition,'view':'full_arms'});write()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'ThumbSurfaceContact.blend'));r['status']='whole_surface_contact_collected_pending_visual_inspection' if r['early_contact_gate_passed'] else 'stopped_at_surface_contact_gate'
except Exception:r['status']='stopped';r['errors'].append(traceback.format_exc())
finally:r['inputs_unchanged']=all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in hashes.items());r['input_hashes']=hashes;write();print(json.dumps({k:r[k] for k in ('status','errors','inputs_unchanged')}))
