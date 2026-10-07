"""Read-only SP-R part/connected-component diagnosis; never saves delivery."""
import sys, json, collections, argparse
from pathlib import Path
import bpy
from mathutils import Vector

p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--out',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(Path(a.source).resolve()),load_ui=False,use_scripts=False)
objects=[o for o in bpy.data.collections['SP-R 208'].all_objects if o.type=='MESH']
report=[]
for o in objects:
    mesh=o.data; parent=list(range(len(mesh.vertices)))
    def find(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    # Position seams are logically joined for diagnosis ONLY, not source welding.
    same={}
    for v in mesh.vertices:
        key=tuple(round(c,5) for c in v.co)
        if key in same:parent[find(v.index)]=find(same[key])
        else:same[key]=v.index
    for e in mesh.edges:parent[find(e.vertices[0])]=find(e.vertices[1])
    parts=collections.defaultdict(list)
    for f in mesh.polygons:parts[find(f.vertices[0])].append(f.index)
    rows=[]
    for ids in sorted(parts.values(),key=len,reverse=True):
        vi={v for i in ids for v in mesh.polygons[i].vertices}
        pts=[o.matrix_world@mesh.vertices[i].co for i in vi]
        groups=collections.Counter()
        for i in vi:
            for g in mesh.vertices[i].groups:groups[o.vertex_groups[g.group].name]+=g.weight
        rows.append({'faces':len(ids),'face_ids':ids,'bounds':[[min(v[k] for v in pts) for k in range(3)],[max(v[k] for v in pts) for k in range(3)]],
                     'materials':dict(collections.Counter(mesh.materials[mesh.polygons[i].material_index].name for i in ids)),
                     'weights':dict(groups.most_common(5))})
    pts=[o.matrix_world@v.co for v in mesh.vertices]
    report.append({'name':o.name,'matrix_world':[list(r) for r in o.matrix_world], 'bounds':[[min(v[k] for v in pts) for k in range(3)],[max(v[k] for v in pts) for k in range(3)]],
                   'components':rows,'groups':[g.name for g in o.vertex_groups]})
    if o.name not in ['Mesh_0.070','Mesh_1.034','Mesh_2.025','Mesh_3.020','Mesh_4.017','Mesh_5.011','Mesh_0.073','Mesh_0.074']:continue
    scene=bpy.data.scenes.new('Diagnosis_'+o.name);scene.collection.objects.link(o);o.hide_render=False
    low=Vector([min(v[k] for v in pts) for k in range(3)]);high=Vector([max(v[k] for v in pts) for k in range(3)])
    center=(low+high)*.5;extent=max(high-low)
    cam=bpy.data.objects.new('DiagnosisCamera',bpy.data.cameras.new('DiagnosisCamera'));scene.collection.objects.link(cam);scene.camera=cam
    cam.data.type='ORTHO';cam.data.ortho_scale=extent*1.2;cam.location=center+Vector((0,-.5,1)).normalized()*extent*3
    cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_cavity=True
    scene.render.resolution_x=1000;scene.render.resolution_y=600;scene.render.resolution_percentage=100
    scene.render.filepath=str(out/(o.name+'.png'));bpy.ops.render.render(write_still=True,scene=scene.name)
    bpy.data.scenes.remove(scene)
(out/'components.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('SOURCE_DIAGNOSIS_COMPLETE',flush=True)
