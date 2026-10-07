"""One bounded existing-D059 closed-grip adaptation; immutable accepted index/gun."""
import sys,json,hashlib,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'WeaponTriggerAlignmentV2'))
from blender_contact_common import *
OUT=STORE/'Evidence/WeaponClosedGripV6/fit_v1';assert not OUT.exists();OUT.mkdir(parents=True)
INDEX=STORE/'Evidence/WeaponTriggerAlignmentV2/index_pose_v1/result.json'
PROBE=STORE/'Evidence/WeaponClosedGripV6/probe_v1/result.json'
THUMB=STORE/'Evidence/WeaponThumbContactV4/fit_v2/result.json'
inputs=[FBX,POSES,AUDIT,CALIB,TOPOLOGY,INDEX,PROBE,THUMB,Path(__file__),Path(__file__).resolve().parents[1]/'WeaponTriggerAlignmentV2/blender_contact_common.py']
hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
for p in inputs[-2:]:(OUT/p.name).write_bytes(p.read_bytes())
r={'scope':__doc__,'errors':[],'fits':[],'phases':[],'views':[],'native_authored':False,'source_clip_modified':False}
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
def rot(m):return m[:3,:3]/np.linalg.norm(m[:3,:3],axis=0)
def apply(b,rotations,parents):
    out=dict(b)
    for n,rotation in rotations.items():
        local=np.linalg.inv(b[parents[n]])@b[n];local[:3,:3]=rotation*np.linalg.norm(local[:3,:3],axis=0);out[n]=out[parents[n]]@local
    return out
def swing(v):
    a=np.linalg.norm(v)
    return np.eye(3) if a<1e-12 else np.array(Quaternion(Vector(v/a),a).to_matrix())
def evaluate(d,b,gun):return transform(skin(d['p'],d['weights'],{n:b[n]@d['invref'][n] for n in d['invref'] if n in b}),np.linalg.inv(b['hand_r']@gun))
try:
    d=load();accepted=json.loads(INDEX.read_text());thumb=json.loads(THUMB.read_text());parents=d['model']['parents'];gun=np.array(accepted['gun_hand_relative_matrix'])
    index=('index_01_r','index_02_r','index_03_r');indexrot={n:rot(np.array(accepted['reused_pose']['local_transforms'][n])) for n in index}
    thumbrot={n:np.array(x) for n,x in thumb['thumb_rotations'].items()};_,b=posed(d,'0.0');base=apply(b,indexrot,parents);base=apply(base,thumbrot,parents)
    gp,gt,tri=d['gp'],d['gt'],d['tri'];parts={c['id']:set(c['triangle_ids']) for c in d['topo']['components']};stock=np.array([x['id'] for x in json.loads(PROBE.read_text())['wrist_stock_faces']]);tree=BVHTree.FromPolygons([Vector(q) for q in gp],gt[stock].tolist(),all_triangles=True)
    def nearest(p):
        loc,n,idx,dist=tree.find_nearest(Vector(p));return np.array(loc),-np.array(n),float(dist),int(stock[idx])
    current=evaluate(d,base,gun);adapt={};all_joints=[]
    for f in ('middle','ring','pinky'):
        joints=[f+'_0'+str(i)+'_r' for i in ((2,3) if f=='middle' else (1,2,3))];all_joints+=joints
        overlap=[i for i,w in enumerate(d['weights']) if d['digits']['index'][i] and any(w.get(n,0)>1e-6 for n in joints)];assert not overlap,(f,'moves accepted index',overlap)
        # Broad interior pad patches, selected once on the existing mature grip.
        patches=[];targets=[];records=[]
        for suffix in (2,3):
            ids=np.array([i for i,w in enumerate(d['weights']) if w.get(f+'_0'+str(suffix)+'_r',0)>.6]);assert len(ids)>15
            center=current[ids].mean(0);q,n,dist,face=nearest(center);toward=-n
            projection=(current[ids]-center)@toward;sel=ids[projection>=np.quantile(projection,.75)]
            patch=current[sel].mean(0);surface,normal,_,face=nearest(patch)
            target=surface+normal*.08;patches.append(sel);targets.append(target);records.append({'phalange':suffix,'vertices':sel.tolist(),'before_center_cm':patch.tolist(),'target_cm':target.tolist(),'stock_triangle':face})
        ids=np.where(d['digits'][f])[0];names=list(d['invref']);h=np.column_stack([d['p'][ids],np.ones(len(ids))]);wn=np.array([[w.get(n,0) for n in names] for w in [d['weights'][i] for i in ids]]);wn/=wn.sum(1)[:,None]
        def fast(bones):
            m=np.array([np.linalg.inv(bones['hand_r']@gun)@bones[n]@d['invref'][n] for n in names]);return np.einsum('vn,nij,vj->vi',wn,m,h)[:,:3]
        patch_rows=[np.searchsorted(ids,x) for x in patches];initial=fast(base);limits=np.array([np.radians(20 if n.endswith('03_r') else 30) for n in joints]);initialrots={n:rot(np.linalg.inv(base[parents[n]])@base[n]) for n in joints}
        # Restrict clearance to existing near-grip skin, not open-surface global
        # solid classification. Actual triangle crossing is checked separately.
        proximity=np.array([nearest(p)[2]<3 for p in initial]);clearance_rows=np.where(proximity)[0]
        def calc(x,report=False):
            changes={n:initialrots[n]@swing(v) for n,v in zip(joints,x.reshape(-1,3))};bones=apply(base,changes,parents);p=fast(bones);res=[]
            for rows,target in zip(patch_rows,targets):res.extend((p[rows].mean(0)-target)*1.5)
            for i in clearance_rows:
                q,n,dist,_=nearest(p[i]);signed=(p[i]-q)@n;res.append(2*min(0.,signed-.035))
            # Minimal local correction regularizer preserves the mature curl.
            res.extend(x*.16)
            return (np.array(res),changes,p)
        x=np.zeros(len(joints)*3);history=[]
        for iteration in range(18):
            residual,_,_=calc(x);loss=float(residual@residual);history.append(loss);eps=1e-4;jac=np.column_stack([(calc(x+np.eye(len(x))[i]*eps)[0]-residual)/eps for i in range(len(x))]);step=np.linalg.solve(jac.T@jac+np.eye(len(x))*.02,-jac.T@residual)
            length=np.linalg.norm(step);step*=min(1.,np.radians(6)/max(length,1e-12));best=x;bestloss=loss
            for alpha in (1.,.5,.25,.125):
                candidate=(x+alpha*step).reshape(-1,3)
                for j,limit in enumerate(limits):candidate[j]*=min(1.,limit/max(np.linalg.norm(candidate[j]),1e-12))
                candidate=candidate.ravel();rr=calc(candidate)[0];ll=float(rr@rr)
                if ll<bestloss:best=candidate;bestloss=ll
            if np.linalg.norm(best-x)<1e-5:break
            x=best
        residual,changes,p=calc(x);adapt.update(changes);base=apply(base,changes,parents);current=evaluate(d,base,gun)
        r['fits'].append({'finger':f,'preserved_middle_root':f=='middle','patches':records,'rotation_changes_deg':{n:float(np.degrees(np.linalg.norm(v))) for n,v in zip(joints,x.reshape(-1,3))},'loss_history':history,'patch_residual_cm':[float(np.linalg.norm(p[rows].mean(0)-target)) for rows,target in zip(patch_rows,targets)]});write()
    rotations={**thumbrot,**adapt};r['adapted_local_rotations']={n:v.tolist() for n,v in rotations.items()};r['protected_index_local_rotations']={n:v.tolist() for n,v in indexrot.items()};r['gun_hand_relative_matrix']=gun.tolist();changed=tuple(rotations)
    edges=np.unique(np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1),axis=0);nochange=np.array([not any(w.get(n,0)>1e-6 for n in changed) for w in d['weights']]);indextri=tri[np.all(d['digits']['index'][tri],axis=1)];evaluated={}
    for phase in d['poses']:
        _,source=posed(d,phase);beforebones=apply(source,indexrot,parents);afterbones=apply(beforebones,rotations,parents);before=evaluate(d,beforebones,gun);after=evaluate(d,afterbones,gun)
        idxdelta=float(np.max(np.linalg.norm(after[d['digits']['index']]-before[d['digits']['index']],axis=1)));bodydelta=float(np.max(np.linalg.norm(after[nochange]-before[nochange],axis=1)));bonesdelta=max(float(np.max(abs(afterbones[n]-beforebones[n]))) for n in source if n not in changed);assert idxdelta<1e-8 and bodydelta<1e-8 and bonesdelta==0
        row={'phase_s':float(phase),'accepted_index_skin_delta_cm':idxdelta,'non_adapted_skin_delta_cm':bodydelta,'other_bones_delta':bonesdelta,'digits':{}}
        for f in ('thumb','middle','ring','pinky'):
            ft=tri[np.all(d['digits'][f][tri],axis=1)];pairs=intersection_pairs(after,ft,gp,gt);row['digits'][f]={'all_gun_crossing_triangles':len({i for i,j in pairs}),'stock_crossing_triangles':len({i for i,j in pairs if j in parts[0]})}
        ip=intersection_pairs(after,indextri,gp,gt);row['index_crossing_triangles']={str(part):len({i for i,j in ip if j in parts[part]}) for part in (0,4,5)}
        oldlen=np.linalg.norm(before[edges[:,1]]-before[edges[:,0]],axis=1);newlen=np.linalg.norm(after[edges[:,1]]-after[edges[:,0]],axis=1);row['new_severe_edges']=int(np.sum((newlen>3*np.maximum(oldlen,1e-8))&(newlen-oldlen>2)));row['max_extra_edge_length_cm']=float(np.max(newlen-oldlen));r['phases'].append(row);evaluated[phase]=(before,after);write()
    r['early_gate_passed']=all(x['new_severe_edges']==0 and all(y['all_gun_crossing_triangles']==0 for y in x['digits'].values()) for x in r['phases']);write()
    scene=setup_scene();gunmat=material('Stock',(.18,.13,.08));metal=material('Metal',(.16,.19,.20));skinmat=material('Hand',(.61,.41,.27));orange=material('Protected approved index',(1,.24,.05));colors=[material(f,co) for f,co in [('thumb',(.2,.7,.3)),('middle',(.55,.62,.8)),('ring',(.65,.4,.7)),('pinky',(.25,.7,.7))]]
    rifle=mesh('Frozen M1 fit',gp,gt,[gunmat,metal]);
    for poly in rifle.data.polygons:poly.material_index=0 if poly.index in parts[0] else 1
    rt=tri[np.all(d['masks']['r'][tri],axis=1)];lt=tri[np.all(d['masks']['l'][tri],axis=1)];visible=[]
    for phase in ('0.0','2.2','4.1'):
        for condition,p in zip(('accepted_index_before','closed_grip_v6'),evaluated[phase]):
            for o in visible:bpy.data.objects.remove(o,do_unlink=True)
            hand=mesh('Right hand '+condition,p,rt,[skinmat,orange]+colors);left=mesh('Unchanged left support',p,lt,[skinmat]);visible=[hand,left]
            for poly,t in zip(hand.data.polygons,rt):
                poly.material_index=1 if np.all(d['digits']['index'][t]) else 0
                if not poly.material_index:
                    for i,f in enumerate(('thumb','middle','ring','pinky')):
                        if np.all(d['digits'][f][t]):poly.material_index=i+2;break
            for view,offset in [('right',(.28,-.05,.08)),('left',(-.28,-.05,.08)),('top',(.02,-.04,.30)),('bottom',(.02,-.04,-.30)),('rear_oblique',(-.2,-.25,.2))]:
                camera([-.035,-.02,-.025],offset,.23);file=f'{phase}_{condition}_{view}.png';scene.render.filepath=str(OUT/file);bpy.ops.render.render(write_still=True);r['views'].append({'file':file,'phase_s':float(phase),'condition':condition,'view':view});write()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'ClosedGripDiagnostic.blend'));r['status']='pending_multiview_human_review' if r['early_gate_passed'] else 'stopped_at_actual_contact_gate'
except Exception:r['status']='stopped';r['errors'].append(traceback.format_exc())
finally:r['inputs_unchanged']=all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in hashes.items());r['input_hashes']=hashes;write();print(json.dumps({k:r[k] for k in ('status','errors','inputs_unchanged')}))
