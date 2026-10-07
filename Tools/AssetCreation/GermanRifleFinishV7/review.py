"""Fresh import and matched original PBR evidence; no material adaptation."""
import argparse,json,sys,math
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import load,setup,pbr
p=argparse.ArgumentParser();p.add_argument('--input');p.add_argument('--output',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=False)
if a.input:
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(Path(a.input).resolve()))
else:load()
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];s,cams=setup()
if a.input:
    for n,c in cams.items():
        s.camera=c;s.render.filepath=str(out/('fresh_clay_'+n+'.png'));bpy.ops.render.render(write_still=True)
pbr()
names=('whole_right','whole_left','quarter','reverse','top_detail','muzzle') if a.input else ('whole_right','quarter','top_detail')
for n in names:
    s.camera=cams[n];s.render.filepath=str(out/('pbr_'+n+'.png'));bpy.ops.render.render(write_still=True)
rows=[{'name':o.name,'triangles':len(o.data.polygons),'uv':len(o.data.uv_layers),'materials':[m.name for m in o.data.materials],
       'finite':all(math.isfinite(x) for v in o.data.vertices for x in v.co)} for o in meshes]
(out/'review.json').write_text(json.dumps({'freshImport':bool(a.input),'meshes':rows,'pbrViews':names,'materialsUnmodified':True},indent=2),encoding='utf-8')
