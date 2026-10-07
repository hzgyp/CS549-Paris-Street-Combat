"""Read-only source shader/face-color probe, not semantic or visual acceptance."""
import argparse,json,sys,hashlib
from pathlib import Path
import bpy,numpy as np
from mathutils import Matrix
ROOT=Path(__file__).resolve().parents[3];OLD=ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-v1'
INPUT=ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-parts-v3/incoming/kar98k-parts-v3-0-recovery.glb'
p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=False)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(INPUT))
norm=Matrix(json.loads((OLD/'evidence/incoming_v2/inspection.json').read_text())['normalizationMatrix'])
o=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.polygons))
mat=o.data.materials[0];nodes=[]
for n in mat.node_tree.nodes:
    nodes.append({'name':n.name,'type':n.bl_idname,'image':n.image.name if n.type=='TEX_IMAGE' and n.image else None})
links=[{'from':l.from_node.name+'.'+l.from_socket.name,'to':l.to_node.name+'.'+l.to_socket.name} for l in mat.node_tree.links]
images={i.name:np.array(i.pixels[:],dtype=np.float32).reshape(i.size[1],i.size[0],4) for i in bpy.data.images}
uv=o.data.uv_layers.active;positions=np.array([list(norm@o.matrix_world@v.co) for v in o.data.vertices])
centers=np.array([positions[list(f.vertices)].mean(axis=0) for f in o.data.polygons])
uvcenter=np.array([np.mean([list(uv.data[j].uv) for j in f.loop_indices],axis=0) for f in o.data.polygons])
colors={}
for name,img in images.items():
    h,w=img.shape[:2];colors[name]=img[np.clip((uvcenter[:,1]*h).astype(int),0,h-1),np.clip((uvcenter[:,0]*w).astype(int),0,w-1),:3]
zones={
 'stock':(centers[:,0]<-.3)&(centers[:,0]>-.49),
 'receiver_top':(centers[:,0]>-.24)&(centers[:,0]<-.10)&(centers[:,2]>.125),
 'receiver_side_wood':(centers[:,0]>-.23)&(centers[:,0]<-.05)&(centers[:,2]<.065)&(abs(centers[:,1])>.025),
 'front_barrel':(centers[:,0]>.49),
 'handguard':(centers[:,0]>.1)&(centers[:,0]<.3)&(abs(centers[:,1])>.02),
 'handle':(centers[:,0]>-.2)&(centers[:,0]<-.11)&(centers[:,1]<-.045),
}
r={'inputSha256':hashlib.sha256(INPUT.read_bytes()).hexdigest(),'nodes':nodes,'links':links,'zones':{}}
for zone,mask in zones.items():
    r['zones'][zone]={'faces':int(mask.sum()),'xyzRanges':[centers[mask].min(axis=0).tolist(),centers[mask].max(axis=0).tolist()],
        'images':{name:{'rgbQuantiles':np.quantile(c[mask],[.1,.5,.9],axis=0).tolist()} for name,c in colors.items()}}
(out/'materials.json').write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(r))
