"""Frozen V8b read-only skin/self-contact and whole-arms diagnostic review."""
import sys,json,hashlib,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'WeaponTriggerAlignmentV2'))
from blender_contact_common import *
POSE=STORE/'Evidence/WeaponClosedGripV6/chain_seat_v8b/result.json';OUT=STORE/'Evidence/WeaponClosedGripV6/final_review_v8';assert not OUT.exists();OUT.mkdir(parents=True)
inputs=[FBX,POSES,AUDIT,CALIB,TOPOLOGY,POSE,Path(__file__)];hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs};r={'errors':[],'phases':[],'views':[],'native_authored':False}
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
def apply(b,rotations,parents):
    out=dict(b)
    for n,v in rotations.items():
        local=np.linalg.inv(b[parents[n]])@b[n];local[:3,:3]=np.array(v)*np.linalg.norm(local[:3,:3],axis=0);out[n]=out[parents[n]]@local
    return out
def skinlocal(d,b,gun):return transform(skin(d['p'],d['weights'],{n:b[n]@d['invref'][n] for n in d['invref']}),np.linalg.inv(b['hand_r']@gun))
def nonadjacent(a,b,p):
    pairs=intersection_pairs(p,a,p,b);out=[]
    for i,j in pairs:
        # Exclude shared physical seam/edge positions, not merely vertex IDs.
        x=p[a[i]];y=p[b[j]]
        if np.min(np.linalg.norm(x[:,None,:]-y[None,:,:],axis=2))<1e-5:continue
        out.append((int(i),int(j)))
    return len(out)
try:
    d=load();pose=json.loads(POSE.read_text());parents=d['model']['parents'];gun=np.array(pose['gun_hand_relative_matrix']);index=pose['protected_index_local_rotations'];allrot={**index,**pose['adapted_local_rotations']};tri=d['tri'];parts={c['id']:set(c['triangle_ids']) for c in d['topo']['components']};pairnames=[('middle','ring'),('ring','pinky'),('index','middle'),('thumb','index')];evaluated={}
    for phase in ('0.0','2.2','4.1'):
        _,b=posed(d,phase);before=skinlocal(d,apply(b,index,parents),gun);after=skinlocal(d,apply(b,allrot,parents),gun);row={'phase_s':float(phase),'digit_pair_nonadjacent_surface_intersections':{}}
        for a,c in pairnames:
            ta=tri[np.all(d['digits'][a][tri],axis=1)];tc=tri[np.all(d['digits'][c][tri],axis=1)];row['digit_pair_nonadjacent_surface_intersections'][a+'_'+c]={'before':nonadjacent(ta,tc,before),'after':nonadjacent(ta,tc,after)}
        r['phases'].append(row);evaluated[phase]=after;write()
    scene=setup_scene();wood=material('Wood',(.20,.135,.078));metal=material('Metal',(.16,.19,.20));handmat=material('Skin',(.61,.41,.27));garment=material('Unchanged sleeves',(.21,.25,.12));rifle=mesh('Unchanged M1',d['gp'],d['gt'],[wood,metal])
    for poly in rifle.data.polygons:poly.material_index=0 if poly.index in parts[0] else 1
    obj=None
    for phase,p in evaluated.items():
        if obj:bpy.data.objects.remove(obj,do_unlink=True)
        obj=mesh('Whole unchanged source arms '+phase,p,tri,[garment,handmat])
        for poly,t in zip(obj.data.polygons,tri):poly.material_index=1 if np.all((d['masks']['r']|d['masks']['l'])[t]) else 0
        for view,target,offset in [('whole_oblique',[0,.12,-.1],(-1.2,-.1,.45)),('whole_reverse',[0,.12,-.1],(1.2,-.1,.45))]:
            camera(target,offset,1.2);file=phase+'_'+view+'.png';scene.render.filepath=str(OUT/file);bpy.ops.render.render(write_still=True);r['views'].append({'file':file,'phase_s':float(phase),'view':view});write()
    r['status']='collected_read_only_review'
except Exception:r['status']='stopped';r['errors'].append(traceback.format_exc())
finally:r['input_hashes']=hashes;r['inputs_unchanged']=all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in hashes.items());write();print(json.dumps(r))
