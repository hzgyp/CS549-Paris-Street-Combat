"""One render-only M1 workflow study, not an exported/runtime rifle replacement."""
import argparse,hashlib,json,sys,math
from pathlib import Path
import bpy,numpy as np
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-ally-reference-v5'
LAB=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/character-ue582-v1/Evidence/Repair20261001'
KAR=ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-parts-v3/incoming/kar98k-parts-v3-0-recovery.glb'
p=argparse.ArgumentParser();p.add_argument('--output',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=False)
assert hashlib.sha256(KAR.read_bytes()).hexdigest()=='78d3398820afc92314ce553afc4f1aa2528267281b644432177338bc052f4bf4'

def setup():
    s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
    s.render.resolution_x=1440;s.render.resolution_y=810;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
    s.world=bpy.data.worlds.new('ComparisonWorld');s.world.use_nodes=True
    s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.12,.14,.17,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
    s.view_settings.view_transform='AgX';cams={}
    for n,e,t,scale in [('whole_side',(0,-3,0),(0,0,0),1.3),('receiver_top',(-.1,0,2),(-.1,0,.08),.46),('receiver_quarter',(.1,-1,.7),(-.1,0,.075),.46)]:
        d=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,d);s.collection.objects.link(o);o.location=e
        o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=scale;d.clip_start=.001;cams[n]=o
    for n,pos,energy,size in [('Key',(0,-1.2,2),100,2),('Fill',(0,1,1),55,1.5),('Rim',(-.3,.5,1.6),65,1)]:
        d=bpy.data.lights.new(n,'AREA');d.energy=energy;d.shape='DISK';d.size=size;o=bpy.data.objects.new(n,d);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
    return s,cams

results=[]
for variant in ('allied_m1_portable','kar98k_original_pbr','kar98k_response_v1'):
    if variant=='allied_m1_portable':
        bpy.ops.wm.open_mainfile(filepath=str(LAB/'Exchange/SK_M1_Garand.blend'),load_ui=False,use_scripts=False)
        meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
        for o in list(bpy.context.scene.objects):
            if o not in meshes:bpy.data.objects.remove(o,do_unlink=True)
        for o in meshes:
            transform=Matrix.Rotation(math.pi/2,4,'Z')@o.matrix_world
            o.parent=None;o.matrix_world=transform
        pts=[o.matrix_world@v.co for o in meshes for v in o.data.vertices];low=Vector(tuple(min(p[i] for p in pts) for i in range(3)));high=Vector(tuple(max(p[i] for p in pts) for i in range(3)))
        center=(low+high)*.5
        for o in meshes:o.location-=center
    else:
        bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(KAR))
        meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
        norm=Matrix(json.loads((ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-v1/evidence/incoming_v2/inspection.json').read_text())['normalizationMatrix'])
        for o in meshes:o.matrix_world=norm@o.matrix_world
    s,cams=setup();rows=[]
    for o in meshes:
        o.data.calc_loop_triangles();rows.append({'name':o.name,'triangles':len(o.data.loop_triangles),'vertices':len(o.data.vertices),'uv':[u.name for u in o.data.uv_layers]})
    if variant=='kar98k_response_v1':
        for mat in set(m for o in meshes for m in o.data.materials if m):
            tree=mat.node_tree;bs=tree.nodes.get('Principled BSDF');link=bs.inputs['Base Color'].links[0]
            color=link.from_socket;tree.links.remove(link);separate=tree.nodes.new('ShaderNodeSeparateColor');tree.links.new(color,separate.inputs[0]);combine=tree.nodes.new('ShaderNodeCombineColor')
            for channel in ('Red','Green','Blue'):
                power=tree.nodes.new('ShaderNodeMath');power.operation='POWER';power.inputs[1].default_value=.9;tree.links.new(separate.outputs[channel],power.inputs[0]);tree.links.new(power.outputs[0],combine.inputs[channel])
            tree.links.new(combine.outputs[0],bs.inputs['Base Color'])
            mat.name='V5_ContinuousOwnAtlas_ColorPower09_RoughPower10'
        # RoughPower1.0 is identity; original metallic/roughness links unchanged.
    for name,c in cams.items():s.camera=c;s.render.filepath=str(out/(variant+'_'+name+'.png'));bpy.ops.render.render(write_still=True)
    s.camera=cams['receiver_quarter'];bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/(variant+'.blend')))
    results.append({'variant':variant,'meshes':rows,'triangles':sum(r['triangles'] for r in rows),
                    'renderOnly':True,'geometryModified':False,'coordinateLabelsUsed':False,
                    'images':[{'name':i.name,'packed':bool(i.packed_file),'sha256':hashlib.sha256(bytes(i.packed_file.data)).hexdigest() if i.packed_file else None} for i in bpy.data.images]})
(out/'comparison.json').write_text(json.dumps({'variants':results,'exactUeShaderParity':False,'glbExported':False,'visuallyAccepted':'Review required, not inferred'},indent=2),encoding='utf-8')
print(json.dumps({'variants':[(r['variant'],r['triangles']) for r in results],'glbExported':False}),flush=True)
