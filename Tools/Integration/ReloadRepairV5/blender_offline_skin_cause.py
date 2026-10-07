"""Read existing exported V3 skin and recorded bone poses. No mesh/rig edits or UE reads."""
import bpy
import numpy as np
import hashlib, json, os, traceback
from pathlib import Path
from mathutils import Matrix, Quaternion, Vector

ROOT = Path(__file__).resolve().parents[3]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT = STORE / 'Evidence/ReloadRepairV5' / os.environ.get('CS549_RELOAD_SKIN_IDENTITY','offline_skin_v1')
assert not OUT.exists(), 'Preserve occupied evidence'
OUT.mkdir(parents=True)
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
FBX = STORE/'Evidence/ContinuousArmsV3/exchange_v1/SK_PC_ContinuousArmsV3.fbx'
AUDIT = STORE/'Evidence/ReloadSleeveAdaptationV2/bone_audit_v1/result.json'
r = {'errors': [], 'scope': __doc__, 'native_or_model_modified': False,
     'limitations': ['Exported skin plus recorded animation poses; not a new runtime LOD/leader skin query.',
                     'Numeric edge ratios diagnose stretch; they are not visual/contact acceptance.']}
before = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in (FBX, AUDIT)}

def matrix(row):
    if 't' in row: row={'translation':row['t'],'rotation':row['q'],'scale':row['s']}
    x,y,z,w = row['rotation']
    m = Quaternion((w,x,y,z)).to_matrix().to_4x4()
    for j in range(3):
        for i in range(3): m[i][j] *= row['scale'][j]
    m.translation = Vector(row['translation'])
    return np.array(m, dtype=np.float64)

try:
    assert before[str(FBX.relative_to(ROOT))] == '1eca576ef40357af58ecdc315b1006ed6a25140932555c04d72df2fa7c686bb9'
    audit=json.loads(AUDIT.read_text()); assert not audit['errors']
    model=audit['models']['owner']
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(FBX), automatic_bone_orientation=False, use_anim=False)
    rigs=[o for o in bpy.data.objects if o.type=='ARMATURE']; assert len(rigs)==1
    rig=rigs[0]
    names=[n for n in model['ref_component'] if n in rig.data.bones]
    src=np.array([list(rig.matrix_world @ rig.data.bones[n].head_local)+[1.] for n in names])
    dst=np.array([model['ref_component'][n]['translation'] for n in names])
    fit=np.linalg.lstsq(src,dst,rcond=None)[0]
    residual=np.linalg.norm(src@fit-dst,axis=1)
    r['rest_alignment']={'max_cm':float(residual.max()),'rms_cm':float(np.sqrt(np.mean(residual**2))),
                         'bones':len(names),'linear':fit.tolist(),
                         'worst_bone':names[int(residual.argmax())]}
    assert residual.max()<.01, 'FBX/native rest positions do not align'
    ref={n:matrix(t) for n,t in model['ref_component'].items()}
    inv={n:np.linalg.inv(t) for n,t in ref.items()}
    r['phases']=[]
    all_samples=[(label,phase,raw) for label in os.environ.get('CS549_RELOAD_SKIN_CLIPS','failed').split(',')
                 for phase,raw in audit['clips'][label]['samples'].items()]
    direct_path=STORE/'Evidence/ReloadSleeveAdaptationV2/skin_probe_v3/result.json'
    if os.environ.get('CS549_RELOAD_SKIN_DIRECT')=='1':
        direct=json.loads(direct_path.read_text())
        before[str(direct_path.relative_to(ROOT))]=hashlib.sha256(direct_path.read_bytes()).hexdigest()
        for label,row in direct['components'].items():
            all_samples.append(('actual_'+label,str(row['phase']),row['bones_component']))
    for label, phase, raw in all_samples:
        component={}
        def bone(n):
            if n not in component:
                local=matrix(raw.get(n,model['ref_local'][n])); parent=model['parents'][n]
                component[n]=bone(parent)@local if parent in ref else local
            return component[n]
        if label.startswith('actual_'):
            assert set(ref)<=set(raw),set(ref)-set(raw)
            deform={n:matrix(raw[n])@inv[n] for n in ref}
        else: deform={n:bone(n)@inv[n] for n in ref}
        for obj in [o for o in bpy.data.objects if o.type=='MESH']:
            positions=np.array([list(obj.matrix_world@v.co)+[1.] for v in obj.data.vertices])@fit
            homogeneous=np.column_stack([positions,np.ones(len(positions))])
            skinned=np.zeros((len(positions),3)); sums=np.zeros(len(positions))
            weights=[]
            for v in obj.data.vertices:
                named=[(obj.vertex_groups[g.group].name,float(g.weight)) for g in v.groups if g.weight>1e-6]
                assert named and all(n in deform for n,w in named), named
                for n,w in named: skinned[v.index]+=w*(deform[n]@homogeneous[v.index])[:3]; sums[v.index]+=w
                weights.append(named)
            assert np.max(abs(sums-1))<.001
            skinned/=sums[:,None]
            edges=np.array([list(e.vertices) for e in obj.data.edges]); assert len(edges)
            restlen=np.linalg.norm(positions[edges[:,0]]-positions[edges[:,1]],axis=1)
            posedlen=np.linalg.norm(skinned[edges[:,0]]-skinned[edges[:,1]],axis=1)
            valid=restlen>.05 # exclude near-duplicate tiny edges (cm)
            ratio=posedlen[valid]/restlen[valid]
            score=np.where(valid,posedlen-restlen,-np.inf)
            worst=np.argsort(score)[-12:][::-1]
            r['phases'].append({'clip':label,'phase':phase,'mesh':obj.name,'vertices':len(positions),
                'max_edge_stretch_cm':float((posedlen-restlen)[valid].max()),
                'p99_edge_ratio':float(np.percentile(ratio,99)), 'max_edge_ratio':float(ratio.max()),
                'edges_over_3x_and_2cm':int(np.sum((posedlen>3*restlen)&(posedlen-restlen>2)&valid)),
                'worst_edges':[{'edge':int(i),'vertices':edges[i].tolist(),
                    'rest_cm':float(restlen[i]),'posed_cm':float(posedlen[i]),
                    'rest_positions':positions[edges[i]].tolist(),'posed_positions':skinned[edges[i]].tolist(),
                    'weights':[weights[int(v)] for v in edges[i]]} for i in worst]})
    r['status']='offline_skin_simulation_collected_requires_runtime_corroboration'
except Exception:
    r['errors'].append(traceback.format_exc());r['status']='failed_early_cause_gate'
finally:
    r['input_hashes']=before
    r['inputs_unchanged']=all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in before.items())
    (OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:r[k] for k in ('status','errors','inputs_unchanged')}))
