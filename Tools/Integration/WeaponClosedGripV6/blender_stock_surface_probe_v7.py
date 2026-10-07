"""Read-only whole-stock closure, outward-normal and stopped-envelope inspection."""
import sys,json,hashlib,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'WeaponTriggerAlignmentV2'))
from blender_contact_common import *
FIT=STORE/'Evidence/WeaponClosedGripV6/fit_v1/result.json';OUT=STORE/'Evidence/WeaponClosedGripV6/surface_probe_v7';assert not OUT.exists();OUT.mkdir(parents=True)
inputs=[FBX,POSES,AUDIT,CALIB,TOPOLOGY,FIT,Path(__file__)];hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs};r={'errors':[]}
try:
    d=load();fit=json.loads(FIT.read_text());parts={c['id']:set(c['triangle_ids']) for c in d['topo']['components']};gp=d['gp'];st=d['gt'][sorted(parts[0])];edges=np.sort(np.concatenate([st[:,[0,1]],st[:,[1,2]],st[:,[2,0]]]),axis=1);unique,counts=np.unique(edges,axis=0,return_counts=True)
    # Stock positions may have duplicated UV/normal seam vertices. Weld exact
    # diagnostic positions only for closure counts, never change source mesh.
    _,reverse=np.unique(np.round(gp,6),axis=0,return_inverse=True);wt=reverse[st];we=np.sort(np.concatenate([wt[:,[0,1]],wt[:,[1,2]],wt[:,[2,0]]]),axis=1);_,wc=np.unique(we,axis=0,return_counts=True)
    r['stock_topology']={'triangles':len(st),'raw_boundary_edges':int(np.sum(counts==1)),'raw_nonmanifold_edges':int(np.sum(counts>2)),'position_weld_boundary_edges':int(np.sum(wc==1)),'position_weld_nonmanifold_edges':int(np.sum(wc>2))}
    normal,_=normals(gp,st);volume=-float(np.einsum('ij,ij->i',gp[st[:,0]],np.cross(gp[st[:,1]],gp[st[:,2]])).sum()/6);r['outward_signed_volume_cm3']=volume
    r['coordinate_determinant']=d['coordinate_determinant'];r['status']='closed_stock_surface_proved' if not np.sum(wc!=2) and volume>0 else 'surface_closure_uncertain_stop'
except Exception:r['status']='stopped';r['errors'].append(traceback.format_exc())
finally:r['input_hashes']=hashes;r['inputs_unchanged']=all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in hashes.items());(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
