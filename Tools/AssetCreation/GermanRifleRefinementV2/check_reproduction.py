"""Read-only GLB payload comparison; do not infer reproducibility from counts."""
import hashlib, json, struct
from pathlib import Path
root=Path(__file__).resolve().parents[3]
store=root/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-refine-v2'
def load(path):
    raw=path.read_bytes();magic,version,length=struct.unpack_from('<4sII',raw)
    assert magic==b'glTF' and version==2 and length==len(raw)
    n=struct.unpack_from('<I',raw,12)[0];data=json.loads(raw[20:20+n]);start=20+n;size=struct.unpack_from('<I',raw,start)[0]
    return raw,data,raw[start+8:start+8+size]
paths=[store/'blender/interface_finish_v3/Kar98k_RefinedMaster_V2.glb',store/'exports/reproduced_v3/Kar98k_RefinedMaster_V2.glb']
A,B=map(load,paths);different=[]
for i,(va,vb) in enumerate(zip(A[1]['bufferViews'],B[1]['bufferViews'])):
    aa=A[2][va.get('byteOffset',0):va.get('byteOffset',0)+va['byteLength']];bb=B[2][vb.get('byteOffset',0):vb.get('byteOffset',0)+vb['byteLength']]
    if aa!=bb:
        access=[{'index':j,'type':r['type'],'component':r['componentType'],'count':r['count']} for j,r in enumerate(A[1]['accessors']) if r.get('bufferView')==i]
        images=[r.get('name',str(j)) for j,r in enumerate(A[1].get('images',[])) if r.get('bufferView')==i]
        different.append({'view':i,'aBytes':len(aa),'bBytes':len(bb),'accessors':access,'images':images})
report={'paths':[p.relative_to(root).as_posix() for p in paths],'sha256':[hashlib.sha256(r[0]).hexdigest() for r in (A,B)],
        'exactBytesEqual':A[0]==B[0],'jsonEqual':A[1]==B[1],'bufferViewCountEqual':len(A[1]['bufferViews'])==len(B[1]['bufferViews']),
        'differentBufferViews':different,'sameAuthoredMetrics':json.loads((paths[0].parent/'refinement.json').read_text())==json.loads((paths[1].parent/'refinement.json').read_text())}
out=store/'evidence/reproduction_comparison.json'
if out.exists():raise RuntimeError('Preserve existing comparison')
out.write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
