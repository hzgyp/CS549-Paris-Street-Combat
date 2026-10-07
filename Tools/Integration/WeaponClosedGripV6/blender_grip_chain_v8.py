"""One actual-surface whole-chain root seating; mature curl/index/gun unchanged."""
import sys,json,hashlib,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'WeaponTriggerAlignmentV2'))
from blender_contact_common import *
V7=STORE/'Evidence/WeaponClosedGripV6/envelope_fit_v7/result.json';OUT=STORE/'Evidence/WeaponClosedGripV6/chain_seat_v8b';assert not OUT.exists();OUT.mkdir(parents=True)
inputs=[FBX,POSES,AUDIT,CALIB,TOPOLOGY,V7,Path(__file__),Path(__file__).resolve().parents[1]/'WeaponTriggerAlignmentV2/blender_contact_common.py'];hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
for p in inputs[-2:]:(OUT/p.name).write_bytes(p.read_bytes())
r={'scope':__doc__,'errors':[],'seating':[],'phases':[],'views':[],'native_authored':False}
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
def rot(m):return m[:3,:3]/np.linalg.norm(m[:3,:3],axis=0)
def apply(b,rotations,parents):
    out=dict(b)
    for n,v in rotations.items():
        local=np.linalg.inv(b[parents[n]])@b[n];local[:3,:3]=v*np.linalg.norm(local[:3,:3],axis=0);out[n]=out[parents[n]]@local
    return out
def evaluate(d,b,gun):return transform(skin(d['p'],d['weights'],{n:b[n]@d['invref'][n] for n in d['invref']}),np.linalg.inv(b['hand_r']@gun))
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
try:
    d=load();v7=json.loads(V7.read_text());assert v7['early_gate_passed'];parents=d['model']['parents'];gun=np.array(v7['gun_hand_relative_matrix']);indexrot={n:np.array(v) for n,v in v7['protected_index_local_rotations'].items()};adapt={n:np.array(v) for n,v in v7['adapted_local_rotations'].items()};_,source=posed(d,'0.0');base=apply(source,{**indexrot,**adapt},parents);world=base['hand_r']@gun;invworld=np.linalg.inv(world);gp,gt,tri=d['gp'],d['gt'],d['tri'];parts={c['id']:set(c['triangle_ids']) for c in d['topo']['components']};stock=np.array(sorted(parts[0]));tree=BVHTree.FromPolygons([Vector(p) for p in gp],gt[stock].tolist(),all_triangles=True);gn,_=normals(gp,gt);gc=gp[gt].mean(1);under=stock[(gn[stock,2]<.2)&(gc[stock,1]>-18)&(gc[stock,1]<4)]
    for f in ('ring','pinky'):
        rootname=f+'_01_r';root=transform(np.array([base[rootname][:3,3]]),invworld)[0];ids=np.flatnonzero(d['digits'][f]);ft=tri[np.all(d['digits'][f][tri],axis=1)];t=np.searchsorted(ids,ft);allp=evaluate(d,base,gun);p=allp[ids];distalids=np.array([i for i in ids if d['weights'][i].get(f+'_03_r',0)>.6]);center=allp[distalids].mean(0);q,n,face,_=project(gp,gt[under],under,center);inward=-n;projection=(allp[distalids]-center)@inward;patch=distalids[projection>=np.quantile(projection,.75)];pad=allp[patch].mean(0);closest,_,_,_=project(gp,gt[under],under,pad);radius=float(np.linalg.norm(pad-root));solutions=[]
        for i in under:
            for point in sphere_triangle(*(gp[gt[i]]+gn[i]*.035),root,radius,closest):solutions.append((float(np.linalg.norm(point-pad)),point,int(i)))
        assert solutions,(f,'no reachable underside contact');_,target,face=min(solutions,key=lambda x:x[0]);a=pad-root;b=target-root;axis=np.cross(a,b);derived=float(np.arctan2(np.linalg.norm(axis),a@b));axis/=np.linalg.norm(axis);angle=min(derived,np.radians(10))
        original_root=rot(np.linalg.inv(source[parents[rootname]])@source[rootname]);rootbefore=base[rootname].copy()
        def rotation(theta):
            swing=np.eye(4);swing[:3,:3]=np.array(Quaternion(Vector(axis),theta).to_matrix());swing[:3,3]=root-swing[:3,:3]@root;newroot=world@swing@invworld@rootbefore;return rot(np.linalg.inv(base[parents[rootname]])@newroot)
        def calc(theta):
            rr=rotation(theta);changes=dict(adapt);changes[rootname]=rr;bones=apply(source,{**indexrot,**changes},parents);points=evaluate(d,bones,gun)[ids];samples=np.concatenate([points,(points[t[:,0]]+points[t[:,1]])*.5,(points[t[:,1]]+points[t[:,2]])*.5,(points[t[:,2]]+points[t[:,0]])*.5,points[t].mean(1)]);gaps=[]
            for point in samples:
                loc,n,i,dist=tree.find_nearest(Vector(point));gaps.append(float((point-np.array(loc))@(-np.array(n))))
            angle_from_source=float(np.degrees(np.arccos(np.clip((np.trace(original_root.T@rr)-1)*.5,-1,1))));return min(gaps),rr,angle_from_source
        g0,_,_=calc(0);g1,_,bound=calc(angle);assert g0>=.0348,'Initial V7 clearance mismatch';assert bound<=30+1e-5,(f,'source root bound exceeded',bound);observations=[{'angle_deg':0.,'minimum_envelope_cm':g0},{'angle_deg':float(np.degrees(angle)),'minimum_envelope_cm':g1}]
        if g1<.035:
            low,high=0.,angle
            for iteration in range(28):
                mid=(low+high)*.5;gap,_,_=calc(mid);observations.append({'angle_deg':float(np.degrees(mid)),'minimum_envelope_cm':gap})
                if gap<.035:high=mid
                else:low=mid
            final=low
        else:final=angle
        gap,rr,bound=calc(final);adapt[rootname]=rr;base=apply(source,{**indexrot,**adapt},parents);after=evaluate(d,base,gun);r['seating'].append({'finger':f,'pad_direction_source_cm':pad.tolist(),'reachable_direction_target_cm':target.tolist(),'stock_triangle':face,'derived_full_swing_deg':float(np.degrees(derived)),'applied_root_swing_deg':float(np.degrees(final)),'partial_direction_approach':bool(final<derived-1e-5),'source_root_deviation_deg':bound,'minimum_envelope_cm':gap,'pad_patch_mean_gap_cm':float(np.mean([tree.find_nearest(Vector(after[i]))[3] for i in patch])),'root_solve':observations});write()
    r['adapted_local_rotations']={n:v.tolist() for n,v in adapt.items()};r['protected_index_local_rotations']={n:v.tolist() for n,v in indexrot.items()};r['gun_hand_relative_matrix']=gun.tolist();nochange=np.array([not any(w.get(n,0)>1e-6 for n in adapt) for w in d['weights']]);edges=np.unique(np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1),axis=0);evaluated={}
    for phase in d['poses']:
        _,b=posed(d,phase);beforebones=apply(b,indexrot,parents);afterbones=apply(beforebones,adapt,parents);before=evaluate(d,beforebones,gun);after=evaluate(d,afterbones,gun);previous=evaluate(d,apply(beforebones,{n:np.array(v) for n,v in v7['adapted_local_rotations'].items()},parents),gun);idxdelta=float(np.max(np.linalg.norm(after[d['digits']['index']]-before[d['digits']['index']],axis=1)));bodydelta=float(np.max(np.linalg.norm(after[nochange]-before[nochange],axis=1)));otherdelta=max(float(np.max(abs(afterbones[n]-beforebones[n]))) for n in b if n not in adapt);assert idxdelta<1e-8 and bodydelta<1e-8 and otherdelta==0
        row={'phase_s':float(phase),'accepted_index_skin_delta_cm':idxdelta,'unaffected_skin_delta_cm':bodydelta,'other_bones_delta':otherdelta,'digits':{}}
        for f in ('thumb','middle','ring','pinky','index'):
            pairs=intersection_pairs(after,tri[np.all(d['digits'][f][tri],axis=1)],gp,gt);row['digits'][f]={'all_gun_crossing_triangles':len({i for i,j in pairs}),'stock_crossing_triangles':len({i for i,j in pairs if j in parts[0]})}
        oldlen=np.linalg.norm(before[edges[:,1]]-before[edges[:,0]],axis=1);newlen=np.linalg.norm(after[edges[:,1]]-after[edges[:,0]],axis=1);row['new_severe_edges']=int(np.sum((newlen>3*np.maximum(oldlen,1e-8))&(newlen-oldlen>2)));row['max_extra_edge_length_cm']=float(np.max(newlen-oldlen));r['phases'].append(row);evaluated[phase]=(previous,after);write()
    r['early_gate_passed']=all(x['new_severe_edges']==0 and all(x['digits'][f]['all_gun_crossing_triangles']==0 for f in ('thumb','middle','ring','pinky')) for x in r['phases']);write()
    scene=setup_scene();wood=material('Wood',(.20,.135,.078));metal=material('Metal',(.16,.19,.20));skinmat=material('Hand',(.61,.41,.27));orange=material('Protected index',(1,.24,.05));colors=[material(f,c) for f,c in [('thumb',(.2,.7,.3)),('middle',(.55,.62,.8)),('ring',(.65,.4,.7)),('pinky',(.25,.7,.7))]];rifle=mesh('Frozen accepted M1',gp,gt,[wood,metal])
    for poly in rifle.data.polygons:poly.material_index=0 if poly.index in parts[0] else 1
    rt=tri[np.all(d['masks']['r'][tri],axis=1)];lt=tri[np.all(d['masks']['l'][tri],axis=1)];visible=[]
    for phase in ('0.0','2.2','4.1'):
        for condition,p in zip(('v7_before_seating','v8_chain_seated'),evaluated[phase]):
            for o in visible:bpy.data.objects.remove(o,do_unlink=True)
            hand=mesh('Right hand '+condition,p,rt,[skinmat,orange]+colors);left=mesh('Unchanged left',p,lt,[skinmat]);visible=[hand,left]
            for poly,t in zip(hand.data.polygons,rt):
                poly.material_index=1 if np.all(d['digits']['index'][t]) else 0
                if not poly.material_index:
                    for i,f in enumerate(('thumb','middle','ring','pinky')):
                        if np.all(d['digits'][f][t]):poly.material_index=i+2;break
            for view,offset in [('right',(.28,-.05,.08)),('left',(-.28,-.05,.08)),('top',(.02,-.04,.30)),('bottom',(.02,-.04,-.30)),('rear_oblique',(-.20,-.25,.2))]:
                camera([-.035,-.02,-.025],offset,.23);file=f'{phase}_{condition}_{view}.png';scene.render.filepath=str(OUT/file);bpy.ops.render.render(write_still=True);r['views'].append({'file':file,'phase_s':float(phase),'condition':condition,'view':view});write()
            if condition=='v8_chain_seated':
                for poly in hand.data.polygons:poly.material_index=0
                camera([-.035,-.02,-.025],(-.20,-.25,.2),.23);file=f'{phase}_{condition}_plain_oblique.png';scene.render.filepath=str(OUT/file);bpy.ops.render.render(write_still=True);r['views'].append({'file':file,'phase_s':float(phase),'condition':condition,'view':'plain_oblique'});write()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'ClosedGripChainV8.blend'));r['status']='pending_visual_review' if r['early_gate_passed'] else 'stopped_at_exact_contact_gate'
except Exception:r['status']='stopped';r['errors'].append(traceback.format_exc())
finally:r['input_hashes']=hashes;r['inputs_unchanged']=all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in hashes.items());write();print(json.dumps({k:r[k] for k in ('status','errors','inputs_unchanged')}))
