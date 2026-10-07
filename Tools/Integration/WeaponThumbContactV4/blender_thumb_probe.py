"""Inspect existing thumb poses with accepted gun/index frozen; no authored motion."""
import sys,json,hashlib,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'WeaponTriggerAlignmentV2'))
from blender_contact_common import *
BASE=STORE/'Evidence/WeaponThumbContactV4'
OUT=BASE/'probe_v1';assert not OUT.exists();OUT.mkdir(parents=True)
INDEX=STORE/'Evidence/WeaponTriggerAlignmentV2/index_pose_v1/result.json'
inputs=[FBX,POSES,AUDIT,CALIB,TOPOLOGY,INDEX,Path(__file__),Path(__file__).resolve().parents[1]/'WeaponTriggerAlignmentV2/blender_contact_common.py']
hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
for p in inputs[-2:]:(OUT/p.name).write_bytes(p.read_bytes())
r={'scope':__doc__,'errors':[],'poses':[],'native_authored':False}
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
try:
    d=load();accepted=json.loads(INDEX.read_text());candidate=np.array(accepted['gun_hand_relative_matrix']);parents=d['model']['parents']
    index=('index_01_r','index_02_r','index_03_r');thumb=('thumb_01_r','thumb_02_r','thumb_03_r')
    r['thumb_index_weight_overlap_vertices']=[i for i,w in enumerate(d['weights']) if d['digits']['index'][i] and any(w.get(n,0)>1e-6 for n in thumb)]
    indexlocal={n:np.array(accepted['reused_pose']['local_transforms'][n]) for n in index}
    _,b=posed(d,'0.0');base=dict(b)
    for n in index:base[n]=base[parents[n]]@indexlocal[n]
    gp,gt=d['gp'],d['gt'];parts={c['id']:np.array(c['triangle_ids']) for c in d['topo']['components']}
    gn,ga=normals(gp,gt);gc=gp[gt].mean(1)
    stockids=parts[0];upper=stockids[(gn[stockids,2]>.5)&(gc[stockids,1]<4)&(gc[stockids,1]>-18)]
    r['upper_stock_triangles']=[{'id':int(i),'center':gc[i].tolist(),'normal':gn[i].tolist()} for i in upper]
    r['accepted_gun_hand_relative_matrix']=candidate.tolist()
    tmask=np.array([sum(w.get(n,0) for n in thumb)>.5 for w in d['weights']]);thumbtri=d['tri'][np.all(tmask[d['tri']],axis=1)]
    distal=np.array([w.get('thumb_03_r',0)>.6 for w in d['weights']])
    r['distal_vertices']=np.where(distal)[0].tolist()
    poseinputs=json.loads(POSES.read_text())['clips'];poses=[]
    for clipkey in ('owner_reload','owner_idle'):
        for phase,s in poseinputs[clipkey]['samples'].items():poses.append((clipkey,phase,{n:mat(t) for n,t in s['bones_component'].items()}))
    for clip,phase,source in poses:
        new=dict(base);locals={}
        for n in thumb:
            t=np.linalg.inv(source[parents[n]])@source[n];current=np.linalg.inv(b[parents[n]])@b[n]
            current[:3,:3]=t[:3,:3]/np.linalg.norm(t[:3,:3],axis=0)*np.linalg.norm(current[:3,:3],axis=0)
            new[n]=new[parents[n]]@current;locals[n]=current.tolist()
        p=skin(d['p'],d['weights'],{n:new[n]@d['invref'][n] for n in d['invref'] if n in new});local=transform(p,np.linalg.inv(new['hand_r']@candidate))
        center=local[distal].mean(0);surface,normal,face,distance=project(gp,gt[upper],upper,center)
        pairs=intersection_pairs(local,thumbtri,gp,gt)
        r['poses'].append({'clip_key':clip,'source':poseinputs[clip]['asset'],'phase_s':float(phase),'local_transforms':locals,
          'thumb_joint_positions_gun_cm':{n:transform(np.array([new[n][:3,3]]),np.linalg.inv(new['hand_r']@candidate))[0].tolist() for n in thumb},
          'distal_center_gun_cm':center.tolist(),'upper_stock_nearest_triangle':face,'upper_stock_point_cm':surface.tolist(),'distance_center_to_upper_stock_cm':distance,
          'thumb_all_crossing_triangles':len({i for i,j in pairs}), 'thumb_stock_crossing_triangles':len({i for i,j in pairs if j in parts[0]})});write()
    # Baseline posed geometry/weights for an actual-pad chain fit, not synthetic mesh.
    points=skin(d['p'],d['weights'],{n:base[n]@d['invref'][n] for n in d['invref'] if n in base});local=transform(points,np.linalg.inv(base['hand_r']@candidate))
    r['baseline_thumb_vertices_gun_cm']=[{'id':int(i),'p':local[i].tolist(),'weights':d['weights'][i]} for i in np.where(tmask)[0]]
    r['baseline_thumb_triangles']=thumbtri.tolist();r['baseline_bones_component']={n:t.tolist() for n,t in base.items()}
    r['status']='existing_pose_inspection_collected'
except Exception:r['status']='stopped';r['errors'].append(traceback.format_exc())
finally:r['inputs_unchanged']=all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in hashes.items());r['input_hashes']=hashes;write();print(json.dumps({k:r[k] for k in ('status','errors','inputs_unchanged')}))
