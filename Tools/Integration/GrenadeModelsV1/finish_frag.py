import bpy,json,sys
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[3]
out=root/'Assets/LocalWorking/Experiments/GrenadeModels/20261011/frag_finish_v1';out.mkdir(exist_ok=False)
bpy.ops.wm.open_mainfile(filepath=str(root/'Assets/LocalWorking/Experiments/GrenadeModels/20261011/frag_inspection_v2/ExistingMkIIInspection.blend'))
o=next(o for o in bpy.context.scene.objects if o.type=='MESH');o.name='MkIIExistingExterior';scene=bpy.context.scene
for ob in list(scene.objects):
    if ob!=o:bpy.data.objects.remove(ob,do_unlink=True)
for key,file in [('D','frag_albedo.png'),('N','frag_normal.png'),('ORM','frag_orm.png')]:
    img=next(i for i in bpy.data.images if i.name.startswith('T_MKII_FRAG_'+key))
    img.scale(1024,1024);img.filepath_raw=str(out/file);img.file_format='PNG';img.save();img.pack()
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
bpy.ops.wm.save_as_mainfile(filepath=str(out/'MkIIExisting.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'MkIIExisting.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
mesh=o.data;mesh.calc_loop_triangles();mesh.calc_tangents(uvmap=mesh.uv_layers[0].name);verts=[]
for tri in mesh.loop_triangles:
    for lid in [tri.loops[0],tri.loops[2],tri.loops[1]]:
        loop=mesh.loops[lid];v=mesh.vertices[loop.vertex_index].co;n=mesh.corner_normals[lid].vector;t=loop.tangent;uv=mesh.uv_layers[0].data[lid].uv
        verts.append([v.x*100,-v.y*100,v.z*100,n.x,-n.y,n.z,t.x,-t.y,t.z,loop.bitangent_sign,uv.x,1-uv.y])
bounds=[o.matrix_world@Vector(v) for v in o.bound_box];dims=[max(v[i] for v in bounds)-min(v[i] for v in bounds) for i in range(3)]
(out/'frag_geometry.json').write_text(json.dumps(dict(schema=1,triangles=len(mesh.loop_triangles),vertices=verts,dimensions_m=dims),separators=(',',':')),encoding='utf-8')
(out/'REPORT.json').write_text(json.dumps(dict(source='equipment slot9 / original primitive9',triangles=len(mesh.loop_triangles),vertices=len(mesh.vertices),dimensions_m=dims,uv_layers=len(mesh.uv_layers),texture_size=1024,character_native_written=False),indent=2),encoding='utf-8')
print('FRAG_FINISHED',len(mesh.loop_triangles),dims,flush=True)
