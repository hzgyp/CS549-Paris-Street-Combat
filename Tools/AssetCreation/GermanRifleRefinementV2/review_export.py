"""Fresh exported-artifact gates and fixed-angle evidence, no game authoring."""
import argparse, hashlib, json, math, sys
from pathlib import Path
import bpy, bmesh
from mathutils import Vector

sys.stdout.reconfigure(encoding='utf-8')
p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',required=True);p.add_argument('--stage',choices=('structural','final'),default='structural')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=Path(a.input).resolve();out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=False)
spec=json.loads((source.parent/'refinement.json').read_text());sha=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(source))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];bpy.context.view_layer.update()
corners=[o.matrix_world @ Vector(v) for o in meshes for v in o.bound_box]
dimensions=[max(p[k] for p in corners)-min(p[k] for p in corners) for k in range(3)]
parts=[]
for o in meshes:
    m=o.data;m.calc_loop_triangles()
    diagnostic=m.copy();changed=diagnostic.validate(verbose=True,clean_customdata=False);bpy.data.meshes.remove(diagnostic)
    row={'name':o.name,'parent':o.parent.name if o.parent else None,'triangles':len(m.loop_triangles),'uv':[u.name for u in m.uv_layers],'wouldValidateChange':changed,
         'finite':all(math.isfinite(t) for v in m.vertices for t in v.co),'finiteUv':all(math.isfinite(t) for u in m.uv_layers for l in u.data for t in l.uv)}
    if o.name!='Kar98k_OriginalWoodGuardSling' and not o.name.startswith('Stock'):
        bm=bmesh.new();bm.from_mesh(m);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
        row.update({'weldedBoundaryEdges':sum(e.is_boundary for e in bm.edges),'weldedNonManifold':sum(not e.is_manifold for e in bm.edges),'signedVolume':bm.calc_volume(signed=True)});bm.free()
    parts.append(row)
expected={s['name']:s for s in spec['parts']};actual={s['name']:s for s in parts}
checks={'names':set(actual)==set(expected),'triangleParity':all(r['triangles']==expected[n]['triangles'] for n,r in actual.items()),
        'hierarchy':all(r['parent']==expected[n]['parent'] for n,r in actual.items()),'approxLength':abs(dimensions[0]-1.105)<.004,
        'underMasterCeiling':sum(r['triangles'] for r in parts)<=350000,'finite':all(r['finite'] and r['finiteUv'] for r in parts),'dataValid':not any(r['wouldValidateChange'] for r in parts),
        'uvPresent':all(r['uv'] for r in parts),'materialsPresent':all(o.data.materials for o in meshes),'packedTextures':all(im.packed_file for im in bpy.data.images),
        'sourceUvPreserved':spec['unchangedCornerUvMaxError']==0 and not spec['stockGlobalWeldOrDecimate'],
        'newMetalClosed':all(r.get('weldedNonManifold',0)==0 for r in parts),'newMetalOutward':all(r.get('signedVolume',1)>0 for r in parts)}
report={'inputSha256':sha,'input':str(source),'stage':a.stage,'checks':checks,'dimensions':dimensions,'triangles':sum(r['triangles'] for r in parts),'parts':parts,
        'images':[{'name':im.name,'size':list(im.size),'packed':bool(im.packed_file)} for im in bpy.data.images],
        'visualAcceptance':'Requires actual multiview review; numeric gates do not approve appearance',
        'stockTopologyLimit':'Inherited disconnected UV-index geometry/cut interfaces not certified watertight'}
(out/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'checks':checks,'triangles':report['triangles'],'dimensions':dimensions}),flush=True)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.render.resolution_x=1440;s.render.resolution_y=810;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.world=bpy.data.worlds.new('FixedInspectionWorld');s.world.use_nodes=True
s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.14,.16,.19,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6
s.view_settings.view_transform='AgX'
def cam(name,eye,target=(0,0,0),scale=1.30):
    d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=eye
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=scale;d.clip_start=.001;d.clip_end=100;return o
cams={n:cam(n,e) for n,e in [('right_side',(0,-3,0)),('left_side',(0,3,0)),('top',(0,0,3)),('bottom',(0,0,-3)),('three_quarter',(.75,-2,1.2)),('reverse_quarter',(-.75,2,1.2))]}
cams.update({n:cam(n,e,t,scale) for n,e,t,scale in [('receiver_side',(-.1,-2,.08),(-.1,0,.08),.46),('receiver_top',(-.1,0,2),(-.1,0,.08),.46),('receiver_quarter',(.1,-1,.7),(-.1,0,.075),.46),('muzzle_quarter',(.72,-1,.6),(.465,0,.02),.27)]})
s.render.engine='BLENDER_WORKBENCH';sh=s.display.shading;sh.light='STUDIO';sh.color_type='SINGLE';sh.single_color=(.62,.65,.69)
sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.show_specular_highlight=True;sh.background_type='WORLD';sh.show_object_outline=False
for name,c in cams.items():s.camera=c;s.render.filepath=str(out/('clay_'+name+'.png'));bpy.ops.render.render(write_still=True)
if a.stage=='final':
    s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True
    for name,position,energy,size in [('Key',(0,-1.2,2),120,2),('Fill',(0,1,1),65,1.5),('Rim',(-.3,.5,1.6),75,1)]:
        d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=position;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
    for name in ('right_side','left_side','top','three_quarter','reverse_quarter','receiver_quarter','receiver_top','muzzle_quarter'):
        s.camera=cams[name];s.render.filepath=str(out/('pbr_'+name+'.png'));bpy.ops.render.render(write_still=True)
    s.camera=cams['three_quarter'];bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'Kar98k_RefinedMaster_Review.blend'))
    # Separate part displacement is a diagnostic, not an operational bolt cycle.
    bolt=bpy.data.objects.get('Kar98k_VisibleBoltAssembly');old=bolt.location.copy()
    bolt.location.x-=.085;bpy.context.view_layer.update();s.render.engine='BLENDER_WORKBENCH';s.camera=cams['receiver_quarter']
    s.render.filepath=str(out/'diagnostic_bolt_displaced.png');bpy.ops.render.render(write_still=True);bolt.location=old;bpy.context.view_layer.update()
assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
print('REVIEW_COMPLETE',flush=True)
if not all(checks.values()):raise SystemExit(3)
