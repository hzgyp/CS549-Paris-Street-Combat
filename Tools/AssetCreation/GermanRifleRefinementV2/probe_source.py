"""Read-only detail inspection of the immutable normalized base."""
import sys, json, argparse
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector

sys.stdout.reconfigure(encoding='utf-8')
p=argparse.ArgumentParser(); p.add_argument('--output',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
root=Path(__file__).resolve().parents[3]
old=root/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-v1'
out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=False)
bpy.ops.wm.open_mainfile(filepath=str(old/'evidence/incoming_v2/incoming_inspection.blend'),load_ui=False)
o=next(o for o in bpy.data.objects if o.type=='MESH')
v=np.array([list(o.matrix_world @ v.co) for v in o.data.vertices])
rows=[]
for x in np.arange(-.30,.56,.02):
    t=v[(v[:,0]>=x)&(v[:,0]<x+.02)&(abs(v[:,1])<.03)]
    if len(t):rows.append({'x':float(x),'count':len(t),'zQuantiles':np.quantile(t[:,2],[0,.1,.5,.9,1]).tolist(),'yQuantiles':np.quantile(t[:,1],[0,.1,.5,.9,1]).tolist()})
(out/'sections.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=1440;s.render.resolution_y=810
for name,eye,target,scale in [('receiver_side',(-.1,-2,.08),(-.1,0,.08),.46),('receiver_top',(-.1,0,2),(-.1,0,.08),.46),('receiver_quarter',(.1,-1,.7),(-.1,0,.075),.46),('muzzle_quarter',(.72,-1,.6),(.465,0,.02),.27)]:
    d=bpy.data.cameras.new(name);c=bpy.data.objects.new(name,d);s.collection.objects.link(c)
    c.location=eye;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=scale
    s.camera=c;s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
print(json.dumps(rows),flush=True)
