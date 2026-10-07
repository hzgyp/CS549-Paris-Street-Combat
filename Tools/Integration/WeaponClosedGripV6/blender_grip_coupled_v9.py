"""One coupled finite-volume finger/stock constrained solve; protected index/gun."""
import sys,json,hashlib,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'WeaponTriggerAlignmentV2'))
from blender_contact_common import *
V8=STORE/'Evidence/WeaponClosedGripV6/chain_seat_v8b/result.json';OUT=STORE/'Evidence/WeaponClosedGripV6/coupled_grip_v9b';assert not OUT.exists();OUT.mkdir(parents=True)
inputs=[FBX,POSES,AUDIT,CALIB,TOPOLOGY,V8,Path(__file__),Path(__file__).resolve().parents[1]/'WeaponTriggerAlignmentV2/blender_contact_common.py'];hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
for file in inputs[-2:]:(OUT/file.name).write_bytes(file.read_bytes())
r={'errors':[],'iterations':[],'phases':[],'views':[],'native_authored':False}
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
def rot(m):return m[:3,:3]/np.linalg.norm(m[:3,:3],axis=0)
def swing(v):
    a=np.linalg.norm(v);return np.eye(3) if a<1e-12 else np.array(Quaternion(Vector(v/a),a).to_matrix())
def vector(m):
    q=__import__('mathutils').Matrix(m.tolist()).to_quaternion();q.normalize();a,t=q.to_axis_angle();return np.array(a)*t
def apply(b,rotations,parents):
    out=dict(b)
    for n,v in rotations.items():
        local=np.linalg.inv(b[parents[n]])@b[n];local[:3,:3]=np.array(v)*np.linalg.norm(local[:3,:3],axis=0);out[n]=out[parents[n]]@local
    return out
def evaluated(d,b,gun):return transform(skin(d['p'],d['weights'],{n:b[n]@d['invref'][n] for n in d['invref']}),np.linalg.inv(b['hand_r']@gun))
def bary(q,a,b,c):
    u,v,w=b-a,c-a,q-a;uu=u@u;uv=u@v;vv=v@v;wu=w@u;wv=w@v;den=uu*vv-uv*uv
    if abs(den)<1e-12:return np.array([1.,0.,0.])
    s=(vv*wu-uv*wv)/den;t=(uu*wv-uv*wu)/den;return np.array([1-s-t,s,t])
def selfcount(p,a,b):
    return int(sum(np.min(np.linalg.norm(p[a[i]][:,None,:]-p[b[j]][None,:,:],axis=2))>=1e-5 for i,j in intersection_pairs(p,a,p,b)))
try:
    d=load();v8=json.loads(V8.read_text());parents=d['model']['parents'];gun=np.array(v8['gun_hand_relative_matrix']);index={n:np.array(v) for n,v in v8['protected_index_local_rotations'].items()};thumb={n:np.array(v) for n,v in v8['adapted_local_rotations'].items() if n.startswith('thumb_')};_,source=posed(d,'0.0');base=apply(source,{**index,**thumb},parents);joints=[f+'_0'+str(i)+'_r' for f in ('middle','ring','pinky') for i in ((2,3) if f=='middle' else (1,2,3))];assert not any(d['digits']['index'][i] and any(w.get(n,0)>1e-6 for n in joints) for i,w in enumerate(d['weights']))
    mature={n:rot(np.linalg.inv(source[parents[n]])@source[n]) for n in joints};limits=np.array([np.radians(20 if n.endswith('03_r') else 30) for n in joints]);x=np.concatenate([vector(mature[n].T@np.array(v8['adapted_local_rotations'][n])) for n in joints]);gp,gt,tri=d['gp'],d['gt'],d['tri'];parts={c['id']:set(c['triangle_ids']) for c in d['topo']['components']};stocktree=BVHTree.FromPolygons([Vector(p) for p in gp],gt[sorted(parts[0])].tolist(),all_triangles=True)
    ids=np.flatnonzero(d['digits']['middle']|d['digits']['ring']|d['digits']['pinky']);names=list(d['invref']);h=np.column_stack([d['p'][ids],np.ones(len(ids))]);weights=np.array([[d['weights'][i].get(n,0) for n in names] for i in ids]);weights/=weights.sum(1)[:,None]
    def bound(x):
        v=x.reshape(-1,3).copy()
        for i,limit in enumerate(limits):v[i]*=min(1.,limit/max(np.linalg.norm(v[i]),1e-12))
        return v.ravel()
    def points(x):
        changes={n:mature[n]@swing(v) for n,v in zip(joints,x.reshape(-1,3))};b=apply(base,changes,parents);matrices=np.array([np.linalg.inv(b['hand_r']@gun)@b[n]@d['invref'][n] for n in names]);return np.einsum('vn,nij,vj->vi',weights,matrices,h)[:,:3],changes
    ft={f:tri[np.all(d['digits'][f][tri],axis=1)] for f in ('middle','ring','pinky')};localtri={f:np.searchsorted(ids,t) for f,t in ft.items()};sampleidx={};samplew={};sampleinterior={}
    for f,t in localtri.items():
        rows=np.searchsorted(ids,np.flatnonzero(d['digits'][f]));sampleidx[f]=np.concatenate([np.repeat(rows[:,None],3,axis=1),t[:,[0,1,0]],t[:,[1,2,1]],t[:,[2,0,2]],t]);samplew[f]=np.concatenate([np.tile([1.,0.,0.],(len(rows),1)),np.tile([.5,.5,0.],(len(t)*3,1)),np.tile([1/3]*3,(len(t),1))]);vw=np.array([d['weights'][i].get(f+'_02_r',0)+d['weights'][i].get(f+'_03_r',0) for i in ids]);sampleinterior[f]=(vw[sampleidx[f]]*samplew[f]).sum(1)>.6
    def samples(p,f):return np.einsum('vi,vij->vj',samplew[f],p[sampleidx[f]])
    def tree(p,f):return BVHTree.FromPolygons([Vector(v) for v in p],localtri[f].tolist(),all_triangles=True)
    baseline,_=points(np.zeros(len(x)));baseline_self_valid={}
    for a,b in [('middle','ring'),('ring','middle'),('ring','pinky'),('pinky','ring')]:
        bt=tree(baseline,b);valid=[]
        for k,p in enumerate(samples(baseline,a)):
            q,n,face,gap=bt.find_nearest(Vector(p));signed=(p-np.array(q))@(-np.array(n));valid.append(bool(sampleinterior[a][k] and signed>.02 and gap<4))
        baseline_self_valid[(a,b)]=np.array(valid)
    r['validated_interior_sample_counts']={a+'_'+b:int(v.sum()) for (a,b),v in baseline_self_valid.items()};write()
    def inspect(x,derivatives=False):
        p,changes=points(x);eps=1e-4;dp=np.stack([(points(x+np.eye(len(x))[i]*eps)[0]-p)/eps for i in range(len(x))],axis=2) if derivatives else None;gaps=[];needs=[];jac=[];contacts=[];contactjac=[]
        for f in ('middle','ring','pinky'):
            sp=samples(p,f);ds=np.einsum('vi,vijk->vjk',samplew[f],dp[sampleidx[f]]) if derivatives else None;sg=[];sj=[]
            for k,point in enumerate(sp):
                q,n,face,gap=stocktree.find_nearest(Vector(point));normal=-np.array(n);signed=float((point-np.array(q))@normal);gaps.append(signed);needs.append(.035);sg.append(signed)
                if derivatives:row=normal@ds[k];jac.append(row);sj.append(row)
            sg=np.array(sg)
            for suffix in (2,3):
                rows=np.array([i for i,vid in enumerate(ids) if d['weights'][vid].get(f+'_0'+str(suffix)+'_r',0)>.6]);direct=samples(p,f)[:len(np.flatnonzero(d['digits'][f]))];frows=np.searchsorted(ids,np.flatnonzero(d['digits'][f]));lookup={int(row):i for i,row in enumerate(frows)};sr=np.array([lookup[int(row)] for row in rows]);sel=sr[np.argsort(abs(sg[sr]))[:max(5,len(sr)//6)]];contacts.append(float(sg[sel].mean()-.10))
                if derivatives:contactjac.append(np.array(sj)[sel].mean(0))
        for (a,b),valid in baseline_self_valid.items():
            bt=tree(p,b);sa=samples(p,a);dsa=np.einsum('vi,vijk->vjk',samplew[a],dp[sampleidx[a]]) if derivatives else None
            for k in np.flatnonzero(valid):
                point=sa[k];q,n,face,dist=bt.find_nearest(Vector(point));normal=-np.array(n);signed=float((point-np.array(q))@normal);gaps.append(signed);needs.append(.02)
                if derivatives:
                    t=localtri[b][face];coef=bary(np.array(q),*p[t]);dother=np.einsum('v,vij->ij',coef,dp[t]);jac.append(normal@(dsa[k]-dother))
        gaps=np.array(gaps);needs=np.array(needs);violation=np.maximum(needs-gaps,0);energy=float(violation@violation);maximum=float(violation.max());contact=np.array(contacts);score=(energy,maximum) if maximum>2e-4 else (0.,float(contact@contact)+.01*float(x@x))
        return p,changes,gaps,needs,violation,contact,score,np.array(jac) if derivatives else None,np.array(contactjac) if derivatives else None
    stalled=0
    for iteration in range(24):
        p,changes,gaps,needs,v,c,score,jg,jc=inspect(x,True);r['iterations'].append({'iteration':iteration,'violation_energy':float(v@v),'max_violation_cm':float(v.max()),'mean_contact_gaps_cm':(c+.10).tolist()});write();step=np.linalg.solve(jc.T@jc+np.eye(len(x))*.08,-jc.T@c-.008*x);active=np.where(gaps-needs<.2)[0];a=jg[active];need=needs[active]-gaps[active]
        for cycle in range(100):
            residual=need-a@step;order=np.argsort(residual)[::-1]
            if not len(order) or residual[order[0]]<1e-5:break
            for k in order[:32]:
                delta=float(need[k]-a[k]@step);length=float(a[k]@a[k])
                if delta>0 and length>1e-10:step+=a[k]*(delta/length)
        step*=min(1.,np.radians(4)/max(np.linalg.norm(step),1e-12));best=x;bestscore=score
        for alpha in (1.,.5,.25,.125):
            candidate=bound(x+step*alpha);newscore=inspect(candidate)[6]
            if newscore<bestscore:best=candidate;bestscore=newscore
        delta=np.linalg.norm(best-x);x=best;stalled=stalled+1 if delta<1e-5 else 0
        if stalled>=2:break
    p,changes,*_=inspect(x);adapt={**thumb,**changes};r['adapted_local_rotations']={n:v.tolist() for n,v in adapt.items()};r['protected_index_local_rotations']={n:v.tolist() for n,v in index.items()};r['gun_hand_relative_matrix']=gun.tolist();r['source_relative_rotation_deg']={n:float(np.degrees(np.linalg.norm(v))) for n,v in zip(joints,x.reshape(-1,3))};nochange=np.array([not any(w.get(n,0)>1e-6 for n in adapt) for w in d['weights']]);edges=np.unique(np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1),axis=0);evaluations={}
    for phase in d['poses']:
        _,b=posed(d,phase);bb=apply(b,index,parents);ab=apply(bb,adapt,parents);before=evaluated(d,bb,gun);after=evaluated(d,ab,gun);old=evaluated(d,apply(bb,{n:np.array(v) for n,v in v8['adapted_local_rotations'].items()},parents),gun);idx=float(np.max(np.linalg.norm(after[d['digits']['index']]-before[d['digits']['index']],axis=1)));body=float(np.max(np.linalg.norm(after[nochange]-before[nochange],axis=1)));bones=max(float(np.max(abs(ab[n]-bb[n]))) for n in b if n not in adapt);assert idx<1e-8 and body<1e-8 and bones==0
        row={'phase_s':float(phase),'accepted_index_skin_delta_cm':idx,'unaffected_skin_delta_cm':body,'other_bones_delta':bones,'digits':{},'self_contact':{}}
        for f in ('thumb','middle','ring','pinky','index'):
            pairs=intersection_pairs(after,tri[np.all(d['digits'][f][tri],axis=1)],gp,gt);row['digits'][f]={'all_gun_crossing_triangles':len({i for i,j in pairs}),'stock_crossing_triangles':len({i for i,j in pairs if j in parts[0]})}
        if phase in ('0.0','2.2','4.1'):
            for a,c in [('middle','ring'),('ring','pinky')]:row['self_contact'][a+'_'+c]={'before':selfcount(before,ft[a],ft[c]),'after':selfcount(after,ft[a],ft[c])}
        ol=np.linalg.norm(before[edges[:,1]]-before[edges[:,0]],axis=1);nl=np.linalg.norm(after[edges[:,1]]-after[edges[:,0]],axis=1);row['new_severe_edges']=int(np.sum((nl>3*np.maximum(ol,1e-8))&(nl-ol>2)));r['phases'].append(row);evaluations[phase]=(old,after);write()
    r['early_gate_passed']=all(x['new_severe_edges']==0 and all(x['digits'][f]['all_gun_crossing_triangles']==0 for f in ('thumb','middle','ring','pinky')) and all(y['after']<=y['before'] for y in x['self_contact'].values()) for x in r['phases']);write()
    scene=setup_scene();wood=material('Wood',(.20,.135,.078));metal=material('Metal',(.16,.19,.20));skinmat=material('Skin',(.61,.41,.27));rifle=mesh('Unchanged M1',gp,gt,[wood,metal])
    for poly in rifle.data.polygons:poly.material_index=0 if poly.index in parts[0] else 1
    rt=tri[np.all(d['masks']['r'][tri],axis=1)];lt=tri[np.all(d['masks']['l'][tri],axis=1)];visible=[]
    for phase in ('0.0','2.2','4.1'):
        for condition,p in zip(('unsafe_v8','coupled_v9'),evaluations[phase]):
            for o in visible:bpy.data.objects.remove(o,do_unlink=True)
            hand=mesh('Right '+condition,p,rt,[skinmat]);left=mesh('Left unchanged',p,lt,[skinmat]);visible=[hand,left]
            for view,offset in [('right',(.28,-.05,.08)),('left',(-.28,-.05,.08)),('top',(.02,-.04,.30)),('bottom',(.02,-.04,-.30)),('rear_oblique',(-.20,-.25,.2))]:
                camera([-.035,-.02,-.025],offset,.23);file=f'{phase}_{condition}_{view}.png';scene.render.filepath=str(OUT/file);bpy.ops.render.render(write_still=True);r['views'].append({'file':file,'phase_s':float(phase),'condition':condition,'view':view});write()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'ClosedGripCoupledV9.blend'));r['status']='pending_visual_review' if r['early_gate_passed'] else 'stopped_at_exact_gun_or_self_contact_gate'
except Exception:r['status']='stopped';r['errors'].append(traceback.format_exc())
finally:r['input_hashes']=hashes;r['inputs_unchanged']=all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in hashes.items());write();print(json.dumps({k:r[k] for k in ('status','errors','inputs_unchanged')}))
