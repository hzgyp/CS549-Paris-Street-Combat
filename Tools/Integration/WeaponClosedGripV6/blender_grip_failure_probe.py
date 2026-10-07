"""Read-only localization of the stopped grip; no second fit or source changes."""
import sys,json,hashlib,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'WeaponTriggerAlignmentV2'))
from blender_contact_common import *
FIT=STORE/'Evidence/WeaponClosedGripV6/fit_v1/result.json'
OUT=STORE/'Evidence/WeaponClosedGripV6/failure_probe_v1';assert not OUT.exists();OUT.mkdir(parents=True)
inputs=[FBX,POSES,AUDIT,CALIB,TOPOLOGY,FIT,Path(__file__)];hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
r={'scope':__doc__,'errors':[]}
try:
    d=load();fit=json.loads(FIT.read_text());parents=d['model']['parents'];_,b=posed(d,'0.0');gun=np.array(fit['gun_hand_relative_matrix']);new=dict(b)
    rotations={**fit['protected_index_local_rotations'],**fit['adapted_local_rotations']}
    for n,v in rotations.items():
        local=np.linalg.inv(b[parents[n]])@b[n];local[:3,:3]=np.array(v)*np.linalg.norm(local[:3,:3],axis=0);new[n]=new[parents[n]]@local
    p=transform(skin(d['p'],d['weights'],{n:new[n]@d['invref'][n] for n in d['invref']}),np.linalg.inv(new['hand_r']@gun));tri=d['tri'];gp,gt=d['gp'],d['gt'];parts={c['id']:set(c['triangle_ids']) for c in d['topo']['components']}
    r['shared_index_middle_root_vertices']=[{'vertex':i,'weights':w,'position_cm':p[i].tolist()} for i,w in enumerate(d['weights']) if d['digits']['index'][i] and w.get('middle_01_r',0)>1e-6]
    r['crossing_localization']={}
    for f in ('middle','ring'):
        ids=np.flatnonzero(np.all(d['digits'][f][tri],axis=1));ft=tri[ids];pairs=intersection_pairs(p,ft,gp,gt);crossids=sorted({i for i,j in pairs if j in parts[0]});record=[]
        for i in crossids:
            vertices=ft[i];weights={n:sum(d['weights'][int(v)].get(n,0) for v in vertices)/3 for n in (f+'_01_r',f+'_02_r',f+'_03_r')}
            record.append({'triangle':int(ids[i]),'center_cm':p[vertices].mean(0).tolist(),'average_weights':weights})
        r['crossing_localization'][f]=record
    r['status']='stopped_fit_localization_only'
except Exception:r['status']='stopped';r['errors'].append(traceback.format_exc())
finally:
    r['input_hashes']=hashes;r['inputs_unchanged']=all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in hashes.items());(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
