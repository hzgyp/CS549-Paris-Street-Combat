"""Surface-retaining refinement; no cuts, caps, hulls, global weld/decimation.

Photo-guided metal surface marking. Every source polygon/UV is retained.
Named source-vertex feature groups keep wood/interface points protected.
"""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy,numpy as np
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[3];OLD=ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-v1'
INPUT=ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-parts-v3/incoming/kar98k-parts-v3-0-recovery.glb'
EXPECTED='78d3398820afc92314ce553afc4f1aa2528267281b644432177338bc052f4bf4'
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--geometry',action='store_true');p.add_argument('--contours',action='store_true')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
if a.geometry:raise RuntimeError('GP004: both labels failed visual gate; geometry is disabled. New surface proof requires a new implementation.')
out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=False)
assert hashlib.sha256(INPUT.read_bytes()).hexdigest()==EXPECTED
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(INPUT))
norm=Matrix(json.loads((OLD/'evidence/incoming_v2/inspection.json').read_text())['normalizationMatrix'])
objects=[o for o in bpy.context.scene.objects if o.type=='MESH'];rifle=max(objects,key=lambda o:len(o.data.polygons));sling=min(objects,key=lambda o:len(o.data.polygons))
root=bpy.data.objects.new('Kar98k_SurfaceMaster_V4',None);bpy.context.scene.collection.objects.link(root)
for o in objects:
    w=norm@o.matrix_world;o.parent=root;o.matrix_world=w
    bpy.context.view_layer.objects.active=o;bpy.ops.object.select_all(action='DESELECT');o.select_set(True)
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
rifle.name='Kar98k_ContinuousStockAndHardware';sling.name='Kar98k_MuseumReplacementSling'
ax=Vector((1,.021,-.135)).normalized();ay=Vector((-ax.y,ax.x,0)).normalized();az=ax.cross(ay).normalized()
F=Matrix((ax,ay,az)).transposed().to_4x4();F.translation=(0,.010,.103);I=F.inverted()
m=rifle.data;pos=np.array([tuple(v.co) for v in m.vertices],dtype=float);local=np.array([tuple(I@v.co) for v in m.vertices])
faces=np.array([tuple(f.vertices) for f in m.polygons],dtype=int);centers=local[faces].mean(axis=1);world_centers=pos[faces].mean(axis=1)
x,y,z=centers.T;wx,wy,wz=world_centers.T
uv=m.uv_layers.active;original_uv=np.array([tuple(v.uv) for v in uv.data])
original_mat=rifle.data.materials[0];wood=original_mat.copy();wood.name='V4_WornMuseumWood'
bs=wood.node_tree.nodes.get('Principled BSDF')
for socket in ('Metallic','Roughness'):
    for l in list(bs.inputs[socket].links):wood.node_tree.links.remove(l)
bs.inputs['Metallic'].default_value=0;bs.inputs['Roughness'].default_value=.58
bs.inputs['Specular IOR Level'].default_value=.30
steel=bpy.data.materials.new('V4_BluedExteriorSteel');steel.use_nodes=True
sb=steel.node_tree.nodes.get('Principled BSDF');sb.inputs['Metallic'].default_value=.88;sb.inputs['Roughness'].default_value=.57 if a.contours else .43
vc=steel.node_tree.nodes.new('ShaderNodeVertexColor');vc.layer_name='V4_SteelVariation'
steel.node_tree.links.new(vc.outputs['Color'],sb.inputs['Base Color'])

# Mark observed upper metal and protrusions; do not remove any triangle.
receiver=(x>-.253)&(x<-.042)&(z>-.001)&(abs(y)<.024)
sight=(x>=-.042)&(x<.143)&(z>.006)&(abs(y)<.017)
handle=(x>-.20)&(x<-.112)&(y<-.030)&(z>-.078)
barrel=(x>.440)
frontband=(x>.404)&(x<.445)
buttplate=wx<-.537
guard=(wx>-.205)&(wx<-.06)&(wz<.011)
# Flat metal bands and small metal insert observed on the wood exterior.
midband=(x>.319)&(x<.332)
metal=receiver|sight|handle|barrel|frontband|buttplate|guard|midband
if a.contours:
    # Hand-traced exposed receiver shoulder, NOT a volumetric cut.
    # Varying half-width follows the bolt sleeve/rings and narrowed sight base.
    stations=np.array([-.281,-.251,-.215,-.199,-.172,-.151,-.127,-.103,-.082,-.045,.005,.068,.109,.143])
    widths=np.array([.010,.013,.019,.023,.025,.025,.022,.023,.025,.024,.017,.015,.017,.016])
    seams=np.array([-.020,-.023,-.025,-.025,-.025,-.025,-.024,-.023,-.022,-.020,-.019,-.018,-.019,-.018])
    receiver_outline=(x>stations[0])&(x<stations[-1])&(abs(y)<np.interp(x,stations,widths))&(z>np.interp(x,stations,seams))
    # The safety lever projects on the opposite side of the sleeve.
    safety=(x>-.252)&(x<-.183)&(y>.012)&(y<.052)&(z>-.021)
    # Trace exposed bent stem and ball; taper at the receiver/stock contact.
    stem_x=np.interp(y,[-.080,-.060,-.035,-.019],[-.152,-.160,-.171,-.185])
    stem=(y<-.020)&(y>-.090)&(abs(x-stem_x)<.021)&(z>-.091)
    metal=receiver_outline|safety|stem|barrel|frontband|buttplate|guard|midband
m.materials.clear();m.materials.append(wood);m.materials.append(steel)
for f,v in zip(m.polygons,metal):f.material_index=int(v)
wood_vertices=set(int(i) for i in faces[~metal].ravel())
# Source UV seams duplicate coordinates. Lock coincident wood points too, no weld.
wood_keys={tuple(np.round(pos[i],6)) for i in wood_vertices}
locked=np.array([tuple(np.round(q,6)) in wood_keys for q in pos],dtype=bool)
selected=~locked;changes=[]
if a.geometry:
    # Exterior smoothing from actual surface adjacency only, bounded0.7mm.
    # Geometric seam duplicates share one diagnostic group; original topology stays.
    groups={};vid=[]
    for i,q in enumerate(pos):
        key=tuple(np.round(q,6));groups.setdefault(key,[]).append(i);vid.append(key)
    neighbors={k:set() for k in groups}
    for e in m.edges:
        u,v=vid[e.vertices[0]],vid[e.vertices[1]]
        if u!=v:neighbors[u].add(v);neighbors[v].add(u)
    representative={k:pos[ii].mean(axis=0) for k,ii in groups.items()}
    # Only marked metal interiors; all wood/interface vertices remain exact.
    for k,indices in groups.items():
        if any(locked[i] for i in indices) or len(neighbors[k])<3:continue
        q=representative[k];l=I@Vector(q)
        # Keep source front features and guard; only receiver/sight/handle polish.
        if not (-.25<l.x<.143):continue
        mean=np.mean([representative[t] for t in sorted(neighbors[k])],axis=0)
        delta=(mean-q)*.55;length=np.linalg.norm(delta)
        if length>.0007:delta*=.0007/length
        if np.linalg.norm(delta)>1e-10:
            for i in indices:m.vertices[i].co=pos[i]+delta;changes.append(i)
    # Flatten only interior upper sight-leaf surface, blended at edges.
    for i in np.flatnonzero(selected):
        l=local[i]
        if -.005<l[0]<.105 and abs(l[1])<.0065 and .011<l[2]<.029:
            w=min(1,(l[0]+.005)/.012,(.105-l[0])/.012,(.0065-abs(l[1]))/.002)
            d=np.clip(.021-l[2],-.0015,.0015)*max(0,w)
            m.vertices[i].co+=az*float(d);changes.append(int(i))
m.update()
for f in m.polygons:f.use_smooth=True
# Preserve fine mapped diffuse variation in exported vertex colors for steel.
image=next(n.image for n in original_mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image and any(l.to_socket.name=='Base Color' for l in n.outputs['Color'].links))
pixels=np.array(image.pixels[:],dtype=np.float32).reshape(image.size[1],image.size[0],4)
q=original_uv;h,w=pixels.shape[:2];rgb=pixels[np.clip((q[:,1]*h).astype(int),0,h-1),np.clip((q[:,0]*w).astype(int),0,w-1),:3]
lum=rgb@np.array([.2126,.7152,.0722]);v=np.clip(.018+.040*lum,.020,.053)
rgba=np.column_stack((v*.92,v,v*1.06,np.ones(len(v)))).astype(np.float32)
attr=m.color_attributes.new(name='V4_SteelVariation',type='FLOAT_COLOR',domain='CORNER');attr.data.foreach_set('color',rgba.ravel())
sling_mat=sling.data.materials[0].copy();sling_mat.name='V4_MuseumCanvas';bs=sling_mat.node_tree.nodes.get('Principled BSDF')
for socket in ('Metallic','Roughness'):
    for l in list(bs.inputs[socket].links):sling_mat.node_tree.links.remove(l)
bs.inputs['Metallic'].default_value=0;bs.inputs['Roughness'].default_value=.78;sling.data.materials[0]=sling_mat

after=np.array([tuple(v.co) for v in m.vertices]);diff=np.linalg.norm(after-pos,axis=1)
assert not np.any(diff[locked]>0)
assert np.array_equal(np.array([tuple(v.uv) for v in uv.data]),original_uv)
rifle.vertex_groups.new(name='ProtectedWoodAndContact').add(np.flatnonzero(locked).tolist(),1,'REPLACE')
rifle.vertex_groups.new(name='MarkedExteriorSteel').add(np.flatnonzero(selected).tolist(),1,'REPLACE')
report={'stage':'surface interface proof' if not a.geometry else 'bounded interior steel polish',
 'sourceSha256':EXPECTED,'blender':bpy.app.version_string,'allSourceFacesRetained':True,'sourceFaces':len(m.polygons)+len(sling.data.polygons),
 'markedSteelFaces':int(metal.sum()),'woodFaces':int((~metal).sum()),'protectedWoodVertices':int(locked.sum()),
 'woodMaxMove':float(diff[locked].max()),'changedMetalVertices':int(np.count_nonzero(diff)), 'maxMetalMove':float(diff.max()),
 'sourceUvExact':True,'globalWeldDecimation':False,'cutsOrCaps':False,'completeOperatingBolt':False,
 'geometryMode':a.geometry,'sourceFrames':[list(r) for r in F],'materialBoundaryRequiresVisualReview':True,
 'labeling':'manual varying contour/seam' if a.contours else 'failed rectangular ribbons',
 'parts':[{'name':o.name,'triangles':len(o.data.polygons),'parent':o.parent.name} for o in objects]}
(out/'surface.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'Kar98k_SurfaceMaster_V4.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in [root]+objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out/'Kar98k_SurfaceMaster_V4.glb'),export_format='GLB',use_selection=True,
 export_apply=True,export_animations=False,export_extras=True,export_vertex_color='MATERIAL',export_all_vertex_colors=False)
print(json.dumps(report),flush=True)
