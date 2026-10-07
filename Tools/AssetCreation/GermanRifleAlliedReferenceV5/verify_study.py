"""Reopen packed study files and verify no geometry/UV/atlas changes, not asset acceptance."""
import json,hashlib,sys,argparse
from pathlib import Path
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-ally-reference-v5'
p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.output).resolve();assert not out.exists()
orig={};rows=[]
for variant in ('kar98k_original_pbr','kar98k_response_v1'):
    bpy.ops.wm.open_mainfile(filepath=str(BASE/'response_v1'/(variant+'.blend')),load_ui=False,use_scripts=False)
    parts=[]
    for o in [o for o in bpy.context.scene.objects if o.type=='MESH']:
        points=np.array([tuple(v.co) for v in o.data.vertices]);world=np.array([tuple(o.matrix_world@v.co) for v in o.data.vertices]);faces=np.array([tuple(f.vertices) for f in o.data.polygons]);uv=np.array([tuple(u.uv) for u in o.data.uv_layers.active.data])
        key=len(faces)
        if variant=='kar98k_original_pbr':orig[key]=(points,world,faces,uv)
        old=orig[key];same=[np.array_equal(x,y) for x,y in zip(old,(points,world,faces,uv))]
        parts.append({'name':o.name,'localPositionsExact':same[0],'worldPositionsExact':same[1],'faceIndicesExact':same[2],'cornerUvExact':same[3]})
    imgs=[{'name':i.name,'packed':bool(i.packed_file),'sha256':hashlib.sha256(bytes(i.packed_file.data)).hexdigest()} for i in bpy.data.images if i.packed_file]
    rows.append({'variant':variant,'parts':parts,'images':imgs})
expected={'60ee7c8e7ed65d2b45638faa3b7cc91fb32466901e416e284f4619939ace0316','2cefb7c2b529576e646c58f6ca3282b2f4eeb4581e0bdf3209b3e79844c73c6b'}
r={'scope':__doc__,'variants':rows,'geometryUvExactBetweenVariants':all(all(p[k] for k in ('localPositionsExact','worldPositionsExact','faceIndicesExact','cornerUvExact')) for row in rows for p in row['parts']),
   'ownSourceAtlasBytesExact':all({i['sha256'] for i in row['images']}==expected for row in rows),'usefulImprovementAccepted':False,'glbExported':False}
out.write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(r),flush=True)
assert r['geometryUvExactBetweenVariants'] and r['ownSourceAtlasBytesExact']
