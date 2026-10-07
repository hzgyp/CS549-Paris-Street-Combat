"""Source-ordered exact triangle witnesses; no open-finger solid/sign inference."""
import sys,json,hashlib,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'WeaponTriggerAlignmentV2'))
from blender_contact_common import *
V8=STORE/'Evidence/WeaponClosedGripV6/chain_seat_v8b/result.json';OUT=STORE/'Evidence/WeaponClosedGripV6/triangle_witness_v10b';assert not OUT.exists();OUT.mkdir(parents=True)
inputs=[FBX,POSES,AUDIT,CALIB,TOPOLOGY,V8,Path(__file__),Path(__file__).resolve().parents[1]/'WeaponTriggerAlignmentV2/blender_contact_common.py'];hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
for file in inputs[-2:]:(OUT/file.name).write_bytes(file.read_bytes())
r={'errors':[],'iterations':[],'phases':[],'views':[],'native_authored':False}
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
def rot(m):return m[:3,:3]/np.linalg.norm(m[:3,:3],axis=0)
def swing(v):
    a=np.linalg.norm(v);return np.eye(3) if a<1e-12 else np.array(Quaternion(Vector(v/a),a).to_matrix())
def vector(m):
    q=__import__('mathutils').Matrix(m.tolist()).to_quaternion();q.normalize();a,t=q.to_axis_angle();return np.array(a)*t
def apply(b,rots,parents):
    out=dict(b)
    for n,v in rots.items():
        local=np.linalg.inv(b[parents[n]])@b[n];local[:3,:3]=np.array(v)*np.linalg.norm(local[:3,:3],axis=0);out[n]=out[parents[n]]@local
    return out
def evaluated(d,b,gun):return transform(skin(d['p'],d['weights'],{n:b[n]@d['invref'][n] for n in d['invref']}),np.linalg.inv(b['hand_r']@gun))
def crossing(p,a,b):return [(i,j) for i,j in intersection_pairs(p,a,p,b) if np.min(np.linalg.norm(p[a[i]][:,None,:]-p[b[j]][None,:,:],axis=2))>=1e-5]
def separator(a,b,current_a,current_b):
    ea=a[[1,2,0]]-a;eb=b[[1,2,0]]-b;na=np.cross(ea[0],ea[1]);nb=np.cross(eb[0],eb[1]);axes=[na,nb,a.mean(0)-b.mean(0),*np.eye(3)]
    axes += [np.cross(u,v) for u in ea for v in eb]+[np.cross(u,n) for u in [*ea,*eb] for n in (na,nb)];choices=[]
    for axis in axes:
        length=np.linalg.norm(axis)
        if length<1e-10:continue
        n=axis/length
        for sign in (1,-1):
            direction=n*sign;gap=float(np.min(a@direction)-np.max(b@direction))
            if gap>1e-5:choices.append((gap,direction,float(np.min(current_a@direction)-np.max(current_b@direction))))
    assert choices,'No source separating axis for actual nonadjacent pair';gap,direction,current_gap=max(choices,key=lambda x:x[2]);return gap,direction
try:
    d=load();v8=json.loads(V8.read_text());parents=d['model']['parents'];gun=np.array(v8['gun_hand_relative_matrix']);index={n:np.array(v) for n,v in v8['protected_index_local_rotations'].items()};thumb={n:np.array(v) for n,v in v8['adapted_local_rotations'].items() if n.startswith('thumb_')};_,source=posed(d,'0.0');base=apply(source,{**index,**thumb},parents);joints=[f+'_0'+str(i)+'_r' for f in ('middle','ring','pinky') for i in ((2,3) if f=='middle' else (1,2,3))];assert not any(d['digits']['index'][i] and any(w.get(n,0)>1e-6 for n in joints) for i,w in enumerate(d['weights']))
    mature={n:rot(np.linalg.inv(source[parents[n]])@source[n]) for n in joints};limits=np.array([np.radians(20 if n.endswith('03_r') else 30) for n in joints]);x=np.concatenate([vector(mature[n].T@np.array(v8['adapted_local_rotations'][n])) for n in joints]);gp,gt,tri=d['gp'],d['gt'],d['tri'];parts={c['id']:set(c['triangle_ids']) for c in d['topo']['components']};stocktree=BVHTree.FromPolygons([Vector(p) for p in gp],gt[sorted(parts[0])].tolist(),all_triangles=True)
    ids=np.flatnonzero(d['digits']['middle']|d['digits']['ring']|d['digits']['pinky']);names=list(d['invref']);h=np.column_stack([d['p'][ids],np.ones(len(ids))]);weights=np.array([[d['weights'][i].get(n,0) for n in names] for i in ids]);weights/=weights.sum(1)[:,None];ft={f:tri[np.all(d['digits'][f][tri],axis=1)] for f in ('middle','ring','pinky')};lt={f:np.searchsorted(ids,t) for f,t in ft.items()}
    def bound(x):
        v=x.reshape(-1,3).copy()
        for i,limit in enumerate(limits):v[i]*=min(1.,limit/max(np.linalg.norm(v[i]),1e-12))
        return v.ravel()
    def points(x):
        changes={n:mature[n]@swing(v) for n,v in zip(joints,x.reshape(-1,3))};b=apply(base,changes,parents);m=np.array([np.linalg.inv(b['hand_r']@gun)@b[n]@d['invref'][n] for n in names]);return np.einsum('vn,nij,vj->vi',weights,m,h)[:,:3],changes
    st=np.concatenate(list(lt.values()));sidx=np.concatenate([np.repeat(np.arange(len(ids))[:,None],3,axis=1),st[:,[0,1,0]],st[:,[1,2,1]],st[:,[2,0,2]],st]);sw=np.concatenate([np.tile([1.,0.,0.],(len(ids),1)),np.tile([.5,.5,0.],(len(st)*3,1)),np.tile([1/3]*3,(len(st),1))])
    def sample(p):return np.einsum('vi,vij->vj',sw,p[sidx])
    ref,_=points(np.zeros(len(x)));witness={}
    def collect(p):
        current={}
        for a,b in [('middle','ring'),('ring','pinky')]:
            pairs=crossing(p,lt[a],lt[b]);current[a+'_'+b]=len(pairs)
            for i,j in pairs:
                key=(a,b,int(i),int(j))
                if key not in witness:
                    gap,n=separator(ref[lt[a][i]],ref[lt[b][j]],p[lt[a][i]],p[lt[b][j]]);witness[key]=(lt[a][i],lt[b][j],n,gap)
        return current
    p,_=points(x);r['initial_actual_crossings']=collect(p);r['initial_witness_count']=len(witness);r['minimum_source_separator_gap_cm']=min(v[3] for v in witness.values());write()
    def inspect(x,derivatives=False):
        p,changes=points(x);sp=sample(p);eps=1e-4;dp=np.stack([(points(x+np.eye(len(x))[i]*eps)[0]-p)/eps for i in range(len(x))],axis=2) if derivatives else None;ds=np.einsum('vi,vijk->vjk',sw,dp[sidx]) if derivatives else None;g=[];target=[];jac=[];normal=[]
        for i,point in enumerate(sp):
            q,n,face,dist=stocktree.find_nearest(Vector(point));nn=-np.array(n);g.append(float((point-np.array(q))@nn));target.append(.035);normal.append(nn)
            if derivatives:jac.append(nn@ds[i])
        for a,b,n,sourcegap in witness.values():
            ia=int(a[np.argmin(p[a]@n)]);ib=int(b[np.argmax(p[b]@n)]);g.append(float((p[ia]-p[ib])@n));target.append(.02)
            if derivatives:jac.append(n@(dp[ia]-dp[ib]))
        g=np.array(g);target=np.array(target);v=np.maximum(target-g,0);contacts=[];cj=[]
        for f in ('middle','ring','pinky'):
            for suffix in (2,3):
                rows=np.array([i for i,vid in enumerate(ids) if d['weights'][vid].get(f+'_0'+str(suffix)+'_r',0)>.6]);sel=rows[np.argsort(abs(g[rows]))[:max(5,len(rows)//6)]];contacts.append(float(g[sel].mean()-.10))
                if derivatives:cj.append(np.array(jac)[sel].mean(0))
        c=np.array(contacts);maximum=float(v.max());score=(float(v@v),maximum) if maximum>2e-4 else (0.,float(c@c)+.01*float(x@x));return p,changes,g,target,v,c,score,np.array(jac) if derivatives else None,np.array(cj) if derivatives else None
    stalled=0
    for iteration in range(24):
        current=collect(points(x)[0]);p,changes,g,target,v,c,score,jg,jc=inspect(x,True);r['iterations'].append({'iteration':iteration,'actual_self_crossings':current,'witnesses':len(witness),'violation_energy':float(v@v),'max_violation_cm':float(v.max()),'contact_mean_gap_cm':(c+.10).tolist()});write();step=np.linalg.solve(jc.T@jc+np.eye(len(x))*.08,-jc.T@c-.008*x);active=np.where(g-target<.2)[0];a=jg[active];need=target[active]-g[active]
        for cycle in range(100):
            residual=need-a@step;order=np.argsort(residual)[::-1]
            if not len(order) or residual[order[0]]<1e-5:break
            for k in order[:32]:
                delta=float(need[k]-a[k]@step);length=float(a[k]@a[k])
                if delta>0 and length>1e-10:step+=a[k]*(delta/length)
        step*=min(1.,np.radians(4)/max(np.linalg.norm(step),1e-12));best=x;bestscore=score
        for alpha in (1.,.5,.25,.125):
            candidate=bound(x+alpha*step);sc=inspect(candidate)[6]
            if sc<bestscore:best=candidate;bestscore=sc
        delta=np.linalg.norm(best-x);x=best;stalled=stalled+1 if delta<1e-5 else 0
        if stalled>=2:break
    p,changes,*_=inspect(x);adapt={**thumb,**changes};r['adapted_local_rotations']={n:v.tolist() for n,v in adapt.items()};r['protected_index_local_rotations']={n:v.tolist() for n,v in index.items()};r['gun_hand_relative_matrix']=gun.tolist();r['source_relative_rotation_deg']={n:float(np.degrees(np.linalg.norm(v))) for n,v in zip(joints,x.reshape(-1,3))};r['final_actual_crossings']=collect(p);nochange=np.array([not any(w.get(n,0)>1e-6 for n in adapt) for w in d['weights']]);edges=np.unique(np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1),axis=0);evaluations={}
    for phase in d['poses']:
        _,b=posed(d,phase);bb=apply(b,index,parents);ab=apply(bb,adapt,parents);before=evaluated(d,bb,gun);after=evaluated(d,ab,gun);old=evaluated(d,apply(bb,{n:np.array(v) for n,v in v8['adapted_local_rotations'].items()},parents),gun);idx=float(np.max(np.linalg.norm(after[d['digits']['index']]-before[d['digits']['index']],axis=1)));body=float(np.max(np.linalg.norm(after[nochange]-before[nochange],axis=1)));bones=max(float(np.max(abs(ab[n]-bb[n]))) for n in b if n not in adapt);assert idx<1e-8 and body<1e-8 and bones==0;row={'phase_s':float(phase),'accepted_index_skin_delta_cm':idx,'unaffected_skin_delta_cm':body,'other_bones_delta':bones,'digits':{},'self_contact':{}}
        for f in ('thumb','middle','ring','pinky','index'):
            pairs=intersection_pairs(after,tri[np.all(d['digits'][f][tri],axis=1)],gp,gt);row['digits'][f]={'all_gun_crossing_triangles':len({i for i,j in pairs}),'stock_crossing_triangles':len({i for i,j in pairs if j in parts[0]})}
        for a,c in [('middle','ring'),('ring','pinky')]:row['self_contact'][a+'_'+c]={'before':len(crossing(before,ft[a],ft[c])),'after':len(crossing(after,ft[a],ft[c]))}
        ol=np.linalg.norm(before[edges[:,1]]-before[edges[:,0]],axis=1);nl=np.linalg.norm(after[edges[:,1]]-after[edges[:,0]],axis=1);row['new_severe_edges']=int(np.sum((nl>3*np.maximum(ol,1e-8))&(nl-ol>2)));r['phases'].append(row);evaluations[phase]=(old,after);write()
    r['early_gate_passed']=all(x['new_severe_edges']==0 and all(x['digits'][f]['all_gun_crossing_triangles']==0 for f in ('thumb','middle','ring','pinky')) and all(y['after']<=y['before'] for y in x['self_contact'].values()) for x in r['phases']);write()
    scene=setup_scene();wood=material('Wood',(.20,.135,.078));metal=material('Metal',(.16,.19,.20));skinmat=material('Skin',(.61,.41,.27));rifle=mesh('Unchanged M1',gp,gt,[wood,metal])
    for poly in rifle.data.polygons:poly.material_index=0 if poly.index in parts[0] else 1
    rt=tri[np.all(d['masks']['r'][tri],axis=1)];lt=tri[np.all(d['masks']['l'][tri],axis=1)];visible=[]
    for phase in ('0.0','2.2','4.1'):
        for condition,p in zip(('unsafe_v8','witness_v10'),evaluations[phase]):
            for o in visible:bpy.data.objects.remove(o,do_unlink=True)
            hand=mesh('Right '+condition,p,rt,[skinmat]);left=mesh('Left unchanged',p,lt,[skinmat]);visible=[hand,left]
            for view,offset in [('right',(.28,-.05,.08)),('left',(-.28,-.05,.08)),('top',(.02,-.04,.30)),('bottom',(.02,-.04,-.30)),('rear_oblique',(-.20,-.25,.2))]:
                camera([-.035,-.02,-.025],offset,.23);file=f'{phase}_{condition}_{view}.png';scene.render.filepath=str(OUT/file);bpy.ops.render.render(write_still=True);r['views'].append({'file':file,'phase_s':float(phase),'condition':condition,'view':view});write()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'ClosedGripWitnessV10.blend'));r['status']='pending_visual_review' if r['early_gate_passed'] else 'stopped_at_exact_gun_or_self_contact_gate'
except Exception:r['status']='stopped';r['errors'].append(traceback.format_exc())
finally:r['input_hashes']=hashes;r['inputs_unchanged']=all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in hashes.items());write();print(json.dumps({k:r[k] for k in ('status','errors','inputs_unchanged')}))
