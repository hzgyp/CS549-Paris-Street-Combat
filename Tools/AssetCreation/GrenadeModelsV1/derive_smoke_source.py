"""Create the durable smoke authoring script from the accepted prop pipeline."""
from pathlib import Path
root=Path(__file__).resolve().parents[3]
src=(root/'Tools/AssetCreation/PressureMineV1/create_mine.py').read_text('utf-8')
start=src.index("if args.stage!='verify':")
end=src.index('\ndef light(',start)
block='''if args.stage!='verify':
    # 1943 external silhouette: gray round can, rolled ends, closed cap,
    # attached flat lever and ring. Exterior only, no internal construction.
    lathe('ClosedSmokeCan',[(0,-6.25),(2.9,-6.25),(3.12,-6.18),(3.175,-6.05),(3.175,5.98),(3.10,6.15),(2.97,6.25),(0,6.25)],paint)
    torus('BottomRolledSeam',3.12,.09,-6.12,steel)
    torus('UpperRolledSeam',3.12,.085,6.10,steel)
    lathe('ClosedTopCollar',[(0,6.25),(1.12,6.25),(1.12,6.85),(.96,7.05),(0,7.05)],steel,64)
    box('ClosedExternalCap',(0,0,7.30),(2.05,1.52,1.1),steel)
    # Continuous ribbon follows the top and one side; width is visible in 3D.
    profile=[(-1.0,7.95),(1.10,7.95),(1.8,7.65),(3.28,6.18),(3.36,5.8),(3.36,-4.45)]
    vertices=[]
    for x,z in profile:
        for y,dz in [(-.65,-.075),(.65,-.075),(.65,.075),(-.65,.075)]:vertices.append((x/100,y/100,(z+dz)/100))
    faces=[(3,2,1,0)]
    for i in range(len(profile)-1):
        for j in range(4):faces.append((i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j))
    k=(len(profile)-1)*4;faces.append((k,k+1,k+2,k+3))
    mesh=bpy.data.meshes.new('BentLever');mesh.from_pydata(vertices,[],faces);mesh.update();o=bpy.data.objects.new('ConnectedBentLever',mesh);bpy.context.collection.objects.link(o)
    b=o.modifiers.new('RoundedLeverEdges','BEVEL');b.width=.00055;b.segments=3;finish(o,steel)
    ring=torus('AttachedPullRing',1.32,.095,7.17,steel);ring.rotation_euler.x=math.pi/2;ring.location.y=-.009
    tube('RingAttachment',[(0,-.6,7.6),(0,-1.0,7.6),(0,-1.0,6.3)],.07,steel)
    for z in [-2.4,3.9]:lathe('YellowIdentificationBand',[(3.18,z-.26),(3.18,z+.26)],ivory)
    # Curved exterior lettering: no borrowed photo/modern lot number.
    for text,z,size in [('HC',1.1,1.42),('SMOKE',-4.25,.84)]:
        spacing=size*.68
        for i,char in enumerate(text):
            angle=(i-(len(text)-1)/2)*spacing/3.18
            bpy.ops.object.text_add(location=(math.sin(angle)*.03187,-math.cos(angle)*.03187,z/100))
            o=bpy.context.object;o.name='CurvedStencil_'+char;o.data.body=char;o.data.align_x='CENTER';o.data.size=size/100;o.data.extrude=0;o.rotation_euler=(math.pi/2,0,angle);o.data.materials.append(ivory);parts.append(o)
    for o in list(parts):
        bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts:o.select_set(True)
    bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();mine=bpy.context.object;mine.name='ANM8SmokeExterior'
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.uv.smart_project(angle_limit=1.15,island_margin=.016,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT')
else:
    bpy.ops.import_scene.gltf(filepath=str(BASE/('finish_'+args.identity)/'ANM8Smoke.glb'))
    meshes=[o for o in scene.objects if o.type=='MESH'];assert len(meshes)==1;mine=meshes[0]
'''
src=src[:start]+block+src[end:]
src=src.replace("Experiments/PressureMine/20261011-v1","Experiments/GrenadeModels/20261011/smoke")
src=src.replace('PressureMine','ANM8Smoke').replace('mine_','smoke_').replace('Mine_','Smoke_')
src=src.replace("(.060,.085,.028,1)","(.13,.145,.14,1)").replace("(.19,.23,.095,1)","(.26,.28,.27,1)")
src=src.replace("(.66,.62,.43)","(.65,.46,.07)")
src=src.replace("assert 3000<=triangles<=20000,triangles","assert 2000<=triangles<=15000,triangles")
src=src.replace("assert .27<dimensions[0]<.35 and .27<dimensions[1]<.30 and .06<dimensions[2]<.09,dimensions","assert .06<dimensions[0]<.08 and .06<dimensions[1]<.075 and .14<dimensions[2]<.17,dimensions")
src=src.replace("d.ortho_scale=.42","d.ortho_scale=.21").replace("((.015,0,.025))","((0,0,.01))")
src=src.replace("('top',(0,-.005,.63))","('top',(0,-.005,.43))").replace("('side',(0,-.58,.16))","('side',(0,-.58,.01))")
src=src.replace("location=(0,0,-.002)","location=(0,0,-.064)")
src=src.replace("inert exterior game prop, fictional personnel pressure trigger; no historical model certification","exterior-only AN-M8-inspired gray/yellow 1943 game prop, approximate art dimensions; no mechanism or exact lot certification")
out=root/'Tools/AssetCreation/GrenadeModelsV1/create_smoke.py';out.write_text(src,encoding='utf-8')
print(out)
