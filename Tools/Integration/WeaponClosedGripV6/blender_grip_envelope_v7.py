"""Closed-stock envelope inequalities with sliding pad contact, not fixed targets."""
import sys,json,hashlib,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'WeaponTriggerAlignmentV2'))
from blender_contact_common import *
OUT=STORE/'Evidence/WeaponClosedGripV6/envelope_fit_v7';assert not OUT.exists();OUT.mkdir(parents=True)
V6=STORE/'Evidence/WeaponClosedGripV6/fit_v1/result.json';SURFACE=STORE/'Evidence/WeaponClosedGripV6/surface_probe_v7/result.json'
inputs=[FBX,POSES,AUDIT,CALIB,TOPOLOGY,V6,SURFACE,Path(__file__),Path(__file__).resolve().parents[1]/'WeaponTriggerAlignmentV2/blender_contact_common.py']
hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
for path in inputs[-2:]:(OUT/path.name).write_bytes(path.read_bytes())
r={'scope':__doc__,'errors':[],'fits':[],'phases':[],'views':[],'native_authored':False,'source_clip_modified':False,'contact_margin_cm':.035}
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
def rot(m):return m[:3,:3]/np.linalg.norm(m[:3,:3],axis=0)
def swing(v):
    a=np.linalg.norm(v);return np.eye(3) if a<1e-12 else np.array(Quaternion(Vector(v/a),a).to_matrix())
def vector(rotation):
    q=__import__('mathutils').Matrix(rotation.tolist()).to_quaternion();q.normalize();axis,angle=q.to_axis_angle();return np.array(axis)*angle
def apply(b,rotations,parents):
    out=dict(b)
    for n,rotation in rotations.items():
        local=np.linalg.inv(b[parents[n]])@b[n];local[:3,:3]=rotation*np.linalg.norm(local[:3,:3],axis=0);out[n]=out[parents[n]]@local
    return out
def evaluate(d,b,gun):return transform(skin(d['p'],d['weights'],{n:b[n]@d['invref'][n] for n in d['invref'] if n in b}),np.linalg.inv(b['hand_r']@gun))
try:
    assert json.loads(SURFACE.read_text())['status']=='closed_stock_surface_proved'
    d=load();v6=json.loads(V6.read_text());parents=d['model']['parents'];gun=np.array(v6['gun_hand_relative_matrix']);indexrot={n:np.array(v) for n,v in v6['protected_index_local_rotations'].items()};thumbrot={n:np.array(v) for n,v in v6['adapted_local_rotations'].items() if n.startswith('thumb_')}
    _,source=posed(d,'0.0');base=apply(source,{**indexrot,**thumbrot},parents);original=base.copy();adapt={};gp,gt,tri=d['gp'],d['gt'],d['tri'];parts={c['id']:set(c['triangle_ids']) for c in d['topo']['components']};stockids=np.array(sorted(parts[0]));tree=BVHTree.FromPolygons([Vector(p) for p in gp],gt[stockids].tolist(),all_triangles=True)
    def distances(points):
        gaps=[];normals=[];faces=[]
        for p in points:
            q,n,i,dist=tree.find_nearest(Vector(p));normal=-np.array(n);gaps.append(float((p-np.array(q))@normal));normals.append(normal);faces.append(int(stockids[i]))
        return np.array(gaps),np.array(normals),faces
    for f in ('middle','ring','pinky'):
        joints=[f+'_0'+str(i)+'_r' for i in ((2,3) if f=='middle' else (1,2,3))];assert not any(d['digits']['index'][i] and any(w.get(n,0)>1e-6 for n in joints) for i,w in enumerate(d['weights']))
        ids=np.flatnonzero(d['digits'][f]);ft=tri[np.all(d['digits'][f][tri],axis=1)];t=np.searchsorted(ids,ft)
        # Midpoints/centroids constrain skin edges and faces as well as vertices.
        def sampled(p):return np.concatenate([p,(p[t[:,0]]+p[t[:,1]])*.5,(p[t[:,1]]+p[t[:,2]])*.5,(p[t[:,2]]+p[t[:,0]])*.5,p[t].mean(1)])
        names=list(d['invref']);h=np.column_stack([d['p'][ids],np.ones(len(ids))]);wn=np.array([[d['weights'][i].get(n,0) for n in names] for i in ids]);wn/=wn.sum(1)[:,None]
        mature={n:rot(np.linalg.inv(source[parents[n]])@source[n]) for n in joints};limits=np.array([np.radians(20 if n.endswith('03_r') else 30) for n in joints])
        x=np.concatenate([vector(mature[n].T@np.array(v6['adapted_local_rotations'][n])) for n in joints])
        def bounded(x):
            v=x.reshape(-1,3).copy()
            for i,limit in enumerate(limits):v[i]*=min(1.,limit/max(np.linalg.norm(v[i]),1e-12))
            return v.ravel()
        def points(x):
            changes={n:mature[n]@swing(v) for n,v in zip(joints,x.reshape(-1,3))};bones=apply(base,changes,parents);matrices=np.array([np.linalg.inv(bones['hand_r']@gun)@bones[n]@d['invref'][n] for n in names]);p=np.einsum('vn,nij,vj->vi',wn,matrices,h)[:,:3];return p,changes
        x=bounded(x);p,_=points(x);g0,n0,_=distances(p);patches=[]
        for suffix in (2,3):
            rows=np.array([i for i,vid in enumerate(ids) if d['weights'][vid].get(f+'_0'+str(suffix)+'_r',0)>.6]);center=p[rows].mean(0);_,norm,_=distances(np.array([center]));inward=-norm[0];proj=(p[rows]-center)@inward;patches.append(rows[proj>=np.quantile(proj,.75)])
        def inspect(x):
            p,_=points(x);sp=sampled(p);g,n,faces=distances(sp);violation=np.maximum(.035-g,0.);vmax=float(violation.max());venergy=float(violation@violation);contact=[];selected=[]
            for rows in patches:
                order=rows[np.argsort(abs(g[rows]))[:max(5,len(rows)//3)]];contact.append(float(g[order].mean()-.10));selected.append(order)
            score=(venergy,vmax) if vmax>2e-4 else (0.,float(np.dot(contact,contact))+.02*float(x@x))
            return p,sp,g,n,faces,violation,np.array(contact),selected,score
        history=[];stalled=0
        for iteration in range(24):
            p,sp,g,n,faces,violation,contact,selected,score=inspect(x);history.append({'iteration':iteration,'max_envelope_violation_cm':float(violation.max()),'violation_energy':float(violation@violation),'patch_mean_gap_cm':(contact+.10).tolist()});eps=1e-4
            deriv=np.stack([(sampled(points(x+np.eye(len(x))[i]*eps)[0])-sp)/eps for i in range(len(x))],axis=2);jg=np.einsum('vi,vij->vj',n,deriv);jc=np.array([jg[rows].mean(0) for rows in selected]);step=np.linalg.solve(jc.T@jc+np.eye(len(x))*.08,-jc.T@contact-.015*x)
            active=np.where(g<.25)[0];a=jg[active];need=.035-g[active]
            # Project the small step onto actual current nonpenetration halfspaces.
            # A finite local QP projection, not an angle/pose/render grid.
            for cycle in range(80):
                residual=need-a@step;order=np.argsort(residual)[::-1];worst=float(residual[order[0]]) if len(order) else 0.
                if worst<1e-5:break
                for j in order[:min(24,len(order))]:
                    delta=float(need[j]-a[j]@step);length=float(a[j]@a[j])
                    if delta>0 and length>1e-10:step+=a[j]*(delta/length)
            step*=min(1.,np.radians(4)/max(np.linalg.norm(step),1e-12));best=x;bestscore=score
            for alpha in (1.,.5,.25,.125):
                candidate=bounded(x+alpha*step);candidate_score=inspect(candidate)[-1]
                if candidate_score<bestscore:best=candidate;bestscore=candidate_score
            delta=np.linalg.norm(best-x);x=best;stalled=stalled+1 if delta<1e-5 else 0
            if stalled>=2:break
        p,changes=points(x);adapt.update(changes);base=apply(base,changes,parents);final=inspect(x);r['fits'].append({'finger':f,'iteration_history':history,'final_max_envelope_violation_cm':float(final[5].max()),'patch_mean_gap_cm':(final[6]+.10).tolist(),'near_patch_vertices_within_2mm':[int(np.sum((final[2][rows]>=0)&(final[2][rows]<.2))) for rows in patches],'source_relative_rotation_deg':{n:float(np.degrees(np.linalg.norm(v))) for n,v in zip(joints,x.reshape(-1,3))},'local_rotations':{n:v.tolist() for n,v in changes.items()}});write()
    rotations={**thumbrot,**adapt};r['adapted_local_rotations']={n:v.tolist() for n,v in rotations.items()};r['protected_index_local_rotations']={n:v.tolist() for n,v in indexrot.items()};r['gun_hand_relative_matrix']=gun.tolist();nochange=np.array([not any(w.get(n,0)>1e-6 for n in rotations) for w in d['weights']]);edges=np.unique(np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1),axis=0);evaluated={}
    for phase in d['poses']:
        _,b=posed(d,phase);beforebones=apply(b,indexrot,parents);afterbones=apply(beforebones,rotations,parents);before=evaluate(d,beforebones,gun);after=evaluate(d,afterbones,gun);v6before=evaluate(d,apply(beforebones,{n:np.array(v) for n,v in v6['adapted_local_rotations'].items()},parents),gun)
        idxdelta=float(np.max(np.linalg.norm(after[d['digits']['index']]-before[d['digits']['index']],axis=1)));otherdelta=max(float(np.max(abs(afterbones[n]-beforebones[n]))) for n in b if n not in rotations);bodydelta=float(np.max(np.linalg.norm(after[nochange]-before[nochange],axis=1)));assert idxdelta<1e-8 and otherdelta==0 and bodydelta<1e-8
        row={'phase_s':float(phase),'accepted_index_skin_delta_cm':idxdelta,'other_bones_delta':otherdelta,'unaffected_skin_delta_cm':bodydelta,'digits':{}}
        for f in ('thumb','middle','ring','pinky','index'):
            ft=tri[np.all(d['digits'][f][tri],axis=1)];pairs=intersection_pairs(after,ft,gp,gt);row['digits'][f]={'all_gun_crossing_triangles':len({i for i,j in pairs}),'stock_crossing_triangles':len({i for i,j in pairs if j in parts[0]}),'guard_crossing_triangles':len({i for i,j in pairs if j in parts[4]}),'blade_crossing_triangles':len({i for i,j in pairs if j in parts[5]})}
        oldlen=np.linalg.norm(before[edges[:,1]]-before[edges[:,0]],axis=1);newlen=np.linalg.norm(after[edges[:,1]]-after[edges[:,0]],axis=1);row['new_severe_edges']=int(np.sum((newlen>3*np.maximum(oldlen,1e-8))&(newlen-oldlen>2)));row['max_extra_edge_length_cm']=float(np.max(newlen-oldlen));r['phases'].append(row);evaluated[phase]=(v6before,after);write()
    r['early_gate_passed']=all(x['new_severe_edges']==0 and all(x['digits'][f]['all_gun_crossing_triangles']==0 for f in ('thumb','middle','ring','pinky')) for x in r['phases']);write()
    scene=setup_scene();wood=material('Wood',(.20,.135,.078));metal=material('Metal',(.16,.19,.20));skinmat=material('Hand',(.61,.41,.27));orange=material('Approved index',(1,.24,.05));colors=[material(f,c) for f,c in [('thumb',(.2,.7,.3)),('middle',(.55,.62,.8)),('ring',(.65,.4,.7)),('pinky',(.25,.7,.7))]];rifle=mesh('Unchanged accepted M1 fit',gp,gt,[wood,metal])
    for poly in rifle.data.polygons:poly.material_index=0 if poly.index in parts[0] else 1
    rt=tri[np.all(d['masks']['r'][tri],axis=1)];lt=tri[np.all(d['masks']['l'][tri],axis=1)];visible=[]
    for phase in ('0.0','2.2','4.1'):
        for condition,p in zip(('stopped_v6','envelope_v7'),evaluated[phase]):
            for o in visible:bpy.data.objects.remove(o,do_unlink=True)
            hand=mesh('Right hand '+condition,p,rt,[skinmat,orange]+colors);left=mesh('Left support unchanged',p,lt,[skinmat]);visible=[hand,left]
            for poly,t in zip(hand.data.polygons,rt):
                poly.material_index=1 if np.all(d['digits']['index'][t]) else 0
                if not poly.material_index:
                    for i,f in enumerate(('thumb','middle','ring','pinky')):
                        if np.all(d['digits'][f][t]):poly.material_index=i+2;break
            for view,offset in [('right',(.28,-.05,.08)),('left',(-.28,-.05,.08)),('top',(.02,-.04,.30)),('bottom',(.02,-.04,-.30)),('rear_oblique',(-.20,-.25,.2))]:
                camera([-.035,-.02,-.025],offset,.23);file=f'{phase}_{condition}_{view}.png';scene.render.filepath=str(OUT/file);bpy.ops.render.render(write_still=True);r['views'].append({'file':file,'phase_s':float(phase),'condition':condition,'view':view});write()
            if condition=='envelope_v7':
                for poly in hand.data.polygons:poly.material_index=0
                camera([-.035,-.02,-.025],(-.20,-.25,.2),.23);file=f'{phase}_{condition}_plain_oblique.png';scene.render.filepath=str(OUT/file);bpy.ops.render.render(write_still=True);r['views'].append({'file':file,'phase_s':float(phase),'condition':condition,'view':'plain_oblique'});write()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'ClosedGripEnvelopeV7.blend'));r['status']='pending_visual_review' if r['early_gate_passed'] else 'stopped_at_exact_contact_gate'
except Exception:r['status']='stopped';r['errors'].append(traceback.format_exc())
finally:r['input_hashes']=hashes;r['inputs_unchanged']=all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in hashes.items());write();print(json.dumps({k:r[k] for k in ('status','errors','inputs_unchanged')}))
