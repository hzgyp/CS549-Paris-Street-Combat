"""Inspect existing three-finger wrap against fixed accepted index/gun; reference-led."""
import sys,json,hashlib,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'WeaponTriggerAlignmentV2'))
from blender_contact_common import *
OUT=STORE/'Evidence/WeaponClosedGripV6/probe_v1';assert not OUT.exists();OUT.mkdir(parents=True)
INDEX=STORE/'Evidence/WeaponTriggerAlignmentV2/index_pose_v1/result.json'
inputs=[FBX,POSES,AUDIT,CALIB,TOPOLOGY,INDEX,Path(__file__),Path(__file__).resolve().parents[1]/'WeaponTriggerAlignmentV2/blender_contact_common.py']
hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
for p in inputs[-2:]:(OUT/p.name).write_bytes(p.read_bytes())
r={'scope':__doc__,'errors':[],'poses':[],'native_authored':False}
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
def rot(m):return m[:3,:3]/np.linalg.norm(m[:3,:3],axis=0)
try:
    d=load();accepted=json.loads(INDEX.read_text());gun=np.array(accepted['gun_hand_relative_matrix']);parents=d['model']['parents'];index=('index_01_r','index_02_r','index_03_r');fingers=('middle','ring','pinky');joints=[f'{f}_0{i}_r' for f in fingers for i in (1,2,3)]
    r['index_affected_vertices']=[i for i,w in enumerate(d['weights']) if d['digits']['index'][i] and any(w.get(n,0)>1e-6 for n in joints)]
    _,b=posed(d,'0.0');base=dict(b)
    for n in index:
        local=np.linalg.inv(b[parents[n]])@b[n];target=np.array(accepted['reused_pose']['local_transforms'][n]);local[:3,:3]=rot(target)*np.linalg.norm(local[:3,:3],axis=0);base[n]=base[parents[n]]@local
    gp,gt=d['gp'],d['gt'];tri=d['tri'];parts={c['id']:set(c['triangle_ids']) for c in d['topo']['components']};clips=json.loads(POSES.read_text())['clips'];gn,ga=normals(gp,gt);gc=gp[gt].mean(1);stock=np.array(list(parts[0]));stock=stock[(gc[stock,1]>-18)&(gc[stock,1]<4)]
    r['wrist_stock_faces']=[{'id':int(i),'p':gc[i].tolist(),'normal':gn[i].tolist()} for i in stock]
    for key,phase in [('owner_reload','0.0'),('owner_reload','2.2'),('owner_idle','0.0')]:
        s={n:mat(t) for n,t in clips[key]['samples'][phase]['bones_component'].items()};new=dict(base);locals={}
        for n in joints:
            local=np.linalg.inv(b[parents[n]])@b[n];target=np.linalg.inv(s[parents[n]])@s[n];local[:3,:3]=rot(target)*np.linalg.norm(local[:3,:3],axis=0);locals[n]=local.tolist();new[n]=new[parents[n]]@local
        p=skin(d['p'],d['weights'],{n:new[n]@d['invref'][n] for n in d['invref'] if n in new});local=transform(p,np.linalg.inv(new['hand_r']@gun));row={'clip_key':key,'phase_s':float(phase),'local_transforms':locals,'fingers':{}}
        for f in fingers:
            fm=d['digits'][f];ft=tri[np.all(fm[tri],axis=1)];distal=np.array([w.get(f+'_03_r',0)>.5 for w in d['weights']]);center=local[distal].mean(0);q,n,face,gap=project(gp,gt[stock],stock,center);pairs=intersection_pairs(local,ft,gp,gt)
            row['fingers'][f]={'joint_positions_cm':{j:transform(np.array([new[j][:3,3]]),np.linalg.inv(new['hand_r']@gun))[0].tolist() for j in joints if j.startswith(f+'_')},'distal_center_cm':center.tolist(),'stock_point_cm':q.tolist(),'stock_normal':n.tolist(),'distance_center_stock_cm':gap,'crossing_triangles':len({i for i,j in pairs})}
        r['poses'].append(row);write()
    r['status']='existing_wrap_poses_inspected_data'
except Exception:r['status']='stopped';r['errors'].append(traceback.format_exc())
finally:r['inputs_unchanged']=all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in hashes.items());r['input_hashes']=hashes;write();print(json.dumps({k:r[k] for k in ('status','errors','inputs_unchanged')}))
