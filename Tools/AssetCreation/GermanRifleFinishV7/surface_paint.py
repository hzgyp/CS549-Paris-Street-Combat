"""Explicit screen-space surface face selections with first-hit visibility."""
import argparse,json,sys
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import BASE,setup
# Hand traced after inspecting the named1600x900 clay images. Not XYZ masks.
STROKES={
 'right_detail':[
  [(480,270),(700,288),(814,311),(913,327),(919,303),(969,309),(978,332),(1203,365),(1243,370),(1254,340),(1307,348),(1315,380),(1336,383),(1340,357),(1430,362),(1472,395),(1600,421),(1600,456),(1463,436),(1317,419),(1201,409),(983,381),(814,376),(700,363),(620,353),(482,340)],
  [(583,346),(608,346),(620,355),(614,390),(607,410),(558,415),(566,387),(572,361)],
  [(555,534),(588,535),(626,535),(644,566),(632,618),(593,645),(544,639),(516,611),(517,569),(535,540)],
 ],
 'left_detail':[
  [(0,414),(162,383),(174,358),(250,342),(263,382),(280,379),(283,351),(349,340),(356,371),(596,330),(626,325),(631,309),(675,304),(682,322),(779,309),(792,319),(894,300),(898,294),(1030,279),(1090,272),(1114,296),(1100,328),(1100,339),(984,350),(800,366),(640,382),(354,413),(0,450)],
  [(1030,527),(1073,529),(1090,550),(1087,596),(1069,625),(1034,639),(1000,626),(985,600),(988,563),(1000,540)]
 ],
 'top_detail':[
  [(482,376),(500,366),(592,367),(603,384),(596,432),(580,440),(493,442),(482,426)],
  [(608,343),(633,335),(684,344),(695,364),(695,456),(684,471),(622,474),(609,455)],
  [(705,354),(798,361),(806,375),(801,454),(705,461)],
  [(814,346),(891,346),(935,354),(951,370),(951,460),(938,465),(814,464)],
  [(960,382),(993,377),(1176,388),(1239,390),(1248,375),(1302,372),(1316,389),(1312,433),(1335,443),(1338,407),(1414,405),(1428,439),(1427,461),(1353,470),(960,468)],
  [(513,270),(545,270),(548,324),(527,344),(515,325)],
  [(551,278),(568,283),(580,279),(584,261),(623,260),(631,278),(629,292),(601,295),(589,318),(558,318)],
  [(557,323),(579,324),(611,339),(598,362),(558,357)],
  [(578,480),(618,488),(616,554),(593,567),(558,556),(570,509)],
 ],
 'whole_right':[
  [(130,337),(145,335),(157,362),(133,491),(123,498),(118,482)],
  [(1139,362),(1162,365),(1160,413),(1141,415)],
  [(1340,386),(1440,392),(1446,386),(1457,388),(1460,402),(1478,400),(1483,424),(1380,427),(1367,414),(1342,418)],
 ],
 'whole_left':[
  [(1451,337),(1465,335),(1482,483),(1470,496),(1445,488)],
  [(122,401),(134,401),(140,390),(151,388),(157,400),(202,397),(201,384),(213,383),(217,397),(258,397),(259,415),(123,421)],
 ],
 'whole_top':[
  [(1259,407),(1385,410),(1410,416),(1478,412),(1478,437),(1390,438),(1259,438)],
  [(1162,407),(1172,406),(1170,441),(1161,442)],
 ],
 'whole_bottom':[
  [(120,412),(270,412),(270,443),(120,443)],
 ],
}
WOOD_EXCLUSIONS={
 'top_detail':[
  [(643,300),(860,300),(961,312),(1162,339),(1232,351),(1240,367),(972,373),(956,341),(815,334),(800,342),(705,342),(705,328),(643,328)],
  [(639,483),(790,481),(957,476),(1110,482),(1230,482),(1242,495),(1152,501),(957,508),(643,507)],
 ],
}

def inside(points,poly):
    x,y=points.T;result=np.zeros(len(points),bool)
    for p,q in zip(poly,poly[1:]+poly[:1]):
        px,py=p;qx,qy=q
        if abs(qy-py)<1e-12:continue
        result^=((py>y)!=(qy>y))&(x<(qx-px)*(y-py)/(qy-py)+px)
    return result

def select(rifle,cams):
    m=rifle.data;verts=np.array([tuple(v.co) for v in m.vertices]);ff=np.array([tuple(p.vertices) for p in m.polygons]);centers=verts[ff].mean(axis=1)
    # Separate sling is also an occluder, although never a painting target.
    allv=[v.co.copy() for v in m.vertices];allf=[tuple(p.vertices) for p in m.polygons]
    for o in bpy.context.scene.objects:
        if o.type!='MESH' or o==rifle:continue
        offset=len(allv);allv.extend(rifle.matrix_world.inverted()@o.matrix_world@v.co for v in o.data.vertices)
        allf.extend(tuple(offset+i for i in p.vertices) for p in o.data.polygons)
    tree=BVHTree.FromPolygons(allv,allf,all_triangles=True)
    selected=set();excluded=set();groups={};visibility=[]
    for name,polys,subtract in [(n,p,False) for n,p in STROKES.items()]+[(n,p,True) for n,p in WOOD_EXCLUSIONS.items()]:
        c=cams[name];rot=c.rotation_euler.to_matrix();R=np.array(rot);delta=centers-np.array(c.location)
        local=delta@R;scale=c.data.ortho_scale
        pixels=np.column_stack(((local[:,0]/scale+.5)*1600,(.5-local[:,1]/(scale*900/1600))*900))
        for k,poly in enumerate(polys):
            candidates=np.where(inside(pixels,poly))[0];hitfaces=[]
            direction=rot@Vector((0,0,-1))
            for fi in candidates:
                origin=Vector(centers[fi])-direction*2
                hit,n,first,dist=tree.ray_cast(origin,direction,2.0001)
                if first==fi:
                    (excluded if subtract else selected).add(int(fi));hitfaces.append(int(fi))
            groups[f'{"wood_" if subtract else ""}{name}_{k}']=hitfaces;visibility.append({'view':name,'subtractWood':subtract,'stroke':k,'screenPolygon':poly,'insideFaces':len(candidates),'visibleFirstHitFaces':len(hitfaces)})
    # Exact already-proved V6 ball faces, same mesh/UV/topology identity.
    ball=json.loads((BASE.parent/'20261003-joint-v6/boundary_v1b/surface_selection.json').read_text())['faces']
    selected.difference_update(excluded);selected.update(ball);groups['v6_proved_ball']=ball
    return {'faces':sorted(selected),'excludedWoodFaces':sorted(excluded),'groups':groups,'strokes':visibility,'coordinateEnvelope':False,'selectionMechanism':'manual visible-surface face centers / first ray hit including sling occlusion'}

p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=False)
bpy.ops.wm.open_mainfile(filepath=str(BASE/'normals_v1/Kar98k_Normals_V7.blend'),load_ui=False,use_scripts=False)
rifle=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.polygons))
s,cams=setup();r=select(rifle,cams)
grey=bpy.data.materials.new('UnselectedOriginalSurface');grey.diffuse_color=(.5,.52,.55,1)
cyan=bpy.data.materials.new('ExplicitVisibleSteelFaces');cyan.diffuse_color=(.02,.65,.85,1)
m=rifle.data;m.materials.clear();m.materials.append(grey);m.materials.append(cyan)
for fi in r['faces']:m.polygons[fi].material_index=1
s.display.shading.color_type='MATERIAL'
for n,c in cams.items():s.camera=c;s.render.filepath=str(out/('selection_'+n+'.png'));bpy.ops.render.render(write_still=True)
(out/'surface_faces.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'ManualSurfaceProof.blend'))
print(json.dumps({'selectedFaces':len(r['faces']),'strokes':r['strokes']}),flush=True)
