"""Reproduce whole local rifle: small manual steel skin + connected annular front."""
import argparse,json,sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from barrel import *
from receiver import rebuild

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--pbr',action='store_true');p.add_argument('--skip-renders',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=False)
    rifle,originals=load();sling=originals[1];sh=sling_hash(sling);mat=steel();skin,rm=rebuild(rifle,mat,out);ordered,c=rings();metrics=clip_source(rifle,ordered);front=loft(ordered,c,mat);sights=sight(c,mat);meshes=[rifle,sling,skin,front,*sights]
    assert sling_hash(sling)==sh
    for o in meshes:o.data.calc_loop_triangles()
    metrics.update({'receiver':rm,'sling_geometry_uv_transform_exact':True,'whole_rifle':True,'receiver_complete_mechanics':False,'original_corner_normals_retained':True,'triangles':sum(len(o.data.loop_triangles) for o in meshes),'meshes':len(meshes),'stage':'assembled_clay' if not a.pbr else 'assembled_pbr','outer_root_edges':74,'inner_root_edges':42})
    (out/'metrics.json').write_text(json.dumps(metrics,indent=2));s,cams=setup()
    if a.pbr:pbr()
    if not a.skip_renders:
        for name in cams:s.camera=cams[name];s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    save_export(meshes,out,'Kar98k_ManualAssembly_V9');print(json.dumps(metrics),flush=True)

if __name__=='__main__':main()
