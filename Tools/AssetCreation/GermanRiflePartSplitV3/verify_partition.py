"""Full face/corner-UV multiset test, independent fresh import; no repair/export."""
import argparse,hashlib,json,struct,sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[3]
p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.output).resolve()
if out.exists():raise RuntimeError('Occupied evidence')
def signatures(path):
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(path))
    faces=[];images=[];count=0
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        m=o.data;m.calc_loop_triangles();uv=m.uv_layers.active
        if uv is None:raise RuntimeError('Missing UV')
        coords=[tuple(o.matrix_world@v.co) for v in m.vertices]
        for t in m.loop_triangles:
            corners=[coords[m.loops[i].vertex_index]+tuple(uv.data[i].uv) for i in t.loops]
            # Cyclic rotations equivalent; mirrored winding is deliberately different.
            corners=min(corners[i:]+corners[:i] for i in range(3))
            faces.append(struct.pack('<15f',*(x for c in corners for x in c)))
        count+=len(m.loop_triangles)
    for i in bpy.data.images:
        if i.packed_file:images.append(hashlib.sha256(bytes(i.packed_file.data)).hexdigest())
    return faces,sorted(images),count
original=ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-v1/incoming/kar98k-base-v1.glb'
x,xi,xc=signatures(original);y,yi,yc=signatures(Path(a.input).resolve())
hx=hashlib.sha256(b''.join(sorted(x))).hexdigest();hy=hashlib.sha256(b''.join(sorted(y))).hexdigest()
r={'originalTriangles':xc,'resultTriangles':yc,'allFacePositionsWindingAndCornerUvsExact':hx==hy,
   'originalFaceUvMultisetSha256':hx,'resultFaceUvMultisetSha256':hy,'packedImagesExact':xi==yi,
   'meaning':'All triangle positions, winding and UVs exact as unordered full multiset; does not certify semantic division, smoothing or PBR node equivalence.'}
out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(r))
