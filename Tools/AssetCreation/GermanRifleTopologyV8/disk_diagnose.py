"""Read-only diagnosis of failed intrinsic disk proof; no correction."""
import collections,json,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import BASE,load
from interface import graph
rifle,_=load();r=json.loads((BASE/'interface_v1/interface.json').read_text())
pos,ff,gp,gf,groups,vg,adj,ef=graph(rifle.data);tris=gf[r['faces']]
counts=collections.Counter(tuple(sorted((int(a),int(b)))) for f in tris for a,b in zip(f,np.roll(f,-1)))
expected={tuple(sorted((a,b))) for a,b in zip(r['loop_groups'],r['loop_groups'][1:]+r['loop_groups'][:1])}
actual={e for e,n in counts.items() if n==1}
extra=actual-expected;missing=expected-actual;non=[(e,n) for e,n in counts.items() if n>2]
d={'face_count':len(tris),'physical_vertices':len(set(tris.flatten())),'edges':len(counts),
   'euler':len(set(tris.flatten()))-len(counts)+len(tris),'expected_boundary_edges':len(expected),'actual_boundary_edges':len(actual),
   'extra_boundary':[{'edge':e,'xyz':gp[list(e)].tolist()} for e in sorted(extra)],'missing_boundary':[list(e) for e in sorted(missing)],
   'nonmanifold_edges':[{'edge':e,'count':n,'xyz':gp[list(e)].tolist(),
                        'source_vertices':[{ 'group':u,'members':groups[u],'xyz':pos[groups[u]].tolist()} for u in e],
                        'source_faces':[{'face':fi,'vertices':ff[fi].tolist(),'xyz':pos[ff[fi]].tolist()} for fi in ef[e] if fi in r['faces']]} for e,n in non],
   'degenerate_triangles':[r['faces'][i] for i,f in enumerate(tris) if len(set(f))<3]}
(BASE/'intrinsic_failure_diagnosis.json').write_text(json.dumps(d,indent=2))
print(json.dumps({k:v for k,v in d.items() if k not in ('extra_boundary','nonmanifold_edges')})+f' extra={len(extra)} nonmanifold={len(non)}',flush=True)
