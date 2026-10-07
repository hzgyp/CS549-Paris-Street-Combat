"""Actual proof masks on unchanged 3D surfaces; read-only scene inspection."""
import sys,argparse,json
from pathlib import Path
import bpy
import numpy as np
sys.path.insert(0,str(Path(__file__).parent))
import main as M

p=argparse.ArgumentParser();p.add_argument('--candidate',required=True);p.add_argument('--out',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);cand=Path(a.candidate).resolve();out=Path(a.out).resolve();assert not out.exists();out.mkdir(parents=True)
source=cand/(M.NAME+'.blend');guard=M.W.sha(source)
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
M.H.OUT=out;M.H.SCENE=bpy.context.scene;M.H.PIVOT=M.P.PIVOT
rows=[]
for mat in {s.material for o in bpy.context.scene.objects if o.type=='MESH' for s in o.material_slots if s.material}:
    nt=mat.node_tree;em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(.005,.005,.005,1)
    image_path=cand/(mat.name+'_WearMask.png')
    im=bpy.data.images.load(str(image_path),check_existing=False) if image_path.exists() else None
    if im:
        im.colorspace_settings.name='Non-Color'
        tx=nt.nodes.new('ShaderNodeTexImage');tx.image=im;nt.links.new(tx.outputs['Color'],em.inputs['Color'])
        data=M.W.pixels(im)[:,:,0];rows.append({'material':mat.name,'max':float(data.max()),'pixels_above_0_1':int((data>.1).sum())})
    nt.links.new(em.outputs[0],nt.nodes.get('Material Output').inputs['Surface'])
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=8;scene.cycles.use_denoising=True
assert len(rows)>=3,'Mask images were not loaded; black geometry is not a mask test'
scene.render.resolution_x=1000;scene.render.resolution_y=607
for args in [('butt',(-.372,0,-.130),(.05,-1,-.5),.065),('butt_reverse',(-.372,0,-.130),(.05,1,-.5),.065),
             ('barrel',(.650,0,.005),(.2,-1,.65),.23)]:M.render_view(*args,prefix='mask')
assert M.W.sha(source)==guard
(out/'mask_review.json').write_text(json.dumps({'source_sha':guard,'masks':rows,'source_unchanged':True},indent=2),encoding='utf-8')
