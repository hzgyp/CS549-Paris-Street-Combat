"""Read-only supplied M1 Blender/atlas comparison; no native asset modification."""
import bpy,numpy as np,json,hashlib,sys,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
LAB=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/character-ue582-v1/Evidence/Repair20261001'
p=argparse.ArgumentParser();p.add_argument('--output',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=False)
src=LAB/'Exchange/SK_M1_Garand.blend';bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];rows=[]
for o in meshes:
    o.data.calc_loop_triangles();pts=np.array([tuple(o.matrix_world@v.co) for v in o.data.vertices]);lo=pts.min(axis=0);hi=pts.max(axis=0)
    rows.append({'name':o.name,'vertices':len(o.data.vertices),'triangles':len(o.data.loop_triangles),'bounds_m':{'min':lo.tolist(),'max':hi.tolist(),'extent':(hi-lo).tolist()},
                 'materials':[s.material.name if s.material else None for s in o.material_slots],'uv':[u.name for u in o.data.uv_layers],
                 'bones':[b.name for mod in o.modifiers if mod.type=='ARMATURE' and mod.object for b in mod.object.data.bones]})
mats=[]
for mat in bpy.data.materials:
    if not mat.use_nodes:continue
    nodes=mat.node_tree.nodes
    mats.append({'name':mat.name,'custom':{k:mat[k] for k in mat.keys()},'nodes':[{'name':n.name,'type':n.type,'image':n.image.name if n.type=='TEX_IMAGE' and n.image else None} for n in nodes],
                 'links':[{'from':l.from_node.name+'.'+l.from_socket.name,'to':l.to_node.name+'.'+l.to_socket.name} for l in mat.node_tree.links]})
tex=[]
for suffix in ('D','N','ORM'):
    path=LAB/f'Textures/USParatrooper/Textures/M1_Garand/T_M1_Garand_{suffix}.png'
    im=bpy.data.images.load(str(path),check_existing=False);im.colorspace_settings.name='Non-Color'
    pix=np.array(im.pixels[:],dtype=np.float32).reshape(im.size[1],im.size[0],4)[:,:,:3]
    tex.append({'suffix':suffix,'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'size':list(im.size),
                'channel_percentiles':np.percentile(pix.reshape(-1,3),[5,50,95],axis=0).tolist(),
                'blue_low_lt_01_fraction':float((pix[:,:,2]<.1).mean()),'blue_high_gt_09_fraction':float((pix[:,:,2]>.9).mean())})
probe=json.loads((LAB/'ue_repair_probe.json').read_text());native=[m for m in probe['materials'] if m['path'].endswith('/MI_M1_Garand')]
cap=json.loads((ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/P3/weapon_capability_v1.json').read_text())
static=[m for m in cap['native_meshes'] if m['path'].endswith('/Sm_M1_Garand')]
r={'scope':__doc__,'blender':bpy.app.version_string,'sourceBlendSha256':sha(src),'sourceBlend':src.relative_to(ROOT).as_posix(),
   'skeletalAppearanceMeshes':rows,'materials':mats,'textures':tex,'nativeMaterialRecord':native,'currentStaticHistoricalRecord':static,
   'nativeHistoricalRecordIsNotNewRuntimeTest':True,'exactNativeShaderParityClaimed':False}
(out/'ally_parameters.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
print(json.dumps({'meshes':rows,'textures':tex,'native_material':native,'static_record':static}),flush=True)
