"""Deterministic private SP-R exterior adaptation. No original delivery writes."""
import argparse, collections, hashlib, json, math, sys
from pathlib import Path
import bpy, numpy as np
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'Assets/LocalWorking/Intake/2026-10-03/01_MW2_Guns_Asset_Library/MW2_Guns_Asset_Library.blend'
BASE=ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-spr-v10'
ANCHOR=Vector((-240.20474243164062,-.2615,18.30))
BUTT=-.379; TIP=.7263040161132813
# x, half width, shoulder height, bottom, channel blend; metres, +X muzzle.
STATIONS=[(-.379,.024,-.025,-.145,0),(-.376,.025,-.023,-.146,0),(-.35,.026,-.020,-.137,0),
          (-.29,.0255,-.015,-.111,0),(-.22,.023,-.010,-.090,0),(-.16,.0195,-.008,-.076,0),
          (-.12,.017,-.009,-.068,0),(-.095,.0165,-.009,-.060,0),(-.068,.0175,-.006,-.051,0),
          (-.045,.020,-.003,-.045,0),(-.025,.0225,-.003,-.043,0),(-.009,.0235,-.002,-.044,0),
          (.0,.024,-.002,-.045,1),(.07,.024,-.002,-.046,1),(.20,.023,-.002,-.046,1),
          (.255,.022,-.001,-.044,1),(.34,.021,-.001,-.041,1),(.44,.020,-.001,-.038,1),
          (.54,.0175,-.001,-.033,1),(.578,.0155,-.002,-.030,1),(.586,.015,-.003,-.028,1)]

def interp(x):
    for i in range(len(STATIONS)-1):
        if x<=STATIONS[i+1][0]:
            a,b=np.array(STATIONS[i]),np.array(STATIONS[i+1]);t=(x-a[0])/(b[0]-a[0])
            p0=np.array(STATIONS[max(i-1,0)]);p3=np.array(STATIONS[min(i+2,len(STATIONS)-1)])
            # Hermite slopes divided by actual station distance avoid nonuniform overshoot.
            m0=(b-p0)/(b[0]-p0[0]);m1=(p3-a)/(p3[0]-a[0]);d=b[0]-a[0]
            v=(2*t**3-3*t*t+1)*a+(t**3-2*t*t+t)*d*m0+(-2*t**3+3*t*t)*b+(t**3-t*t)*d*m1
            v[0]=x;v[4]=min(1,max(0,(x+.009)/.009));return v
    return np.array(STATIONS[-1])

def barrel_factor(x):return 1-.35*max(0,min(1,(x-.254118)/(TIP-.254118)))
def radius(x):return .0147 if x<=.255 else .01443*barrel_factor(x)+.00035

def image_data(name,data,space='sRGB'):
    h,w=data.shape[:2];im=bpy.data.images.new(name,width=w,height=h,alpha=True)
    im.colorspace_settings.name=space;im.pixels.foreach_set(np.asarray(data,dtype=np.float32).ravel())
    im.filepath_raw=str(OUT/(name+'.png'));im.file_format='PNG';im.save();im.pack();return im

def principled(name,color,metal,rough,base=None,normal=None,orm=None):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1)
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
    if base:
        tx=m.node_tree.nodes.new('ShaderNodeTexImage');tx.image=base;m.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color'])
    if normal:
        tx=m.node_tree.nodes.new('ShaderNodeTexImage');tx.image=normal;nm=m.node_tree.nodes.new('ShaderNodeNormalMap')
        nm.inputs['Strength'].default_value=.45;m.node_tree.links.new(tx.outputs['Color'],nm.inputs['Color']);m.node_tree.links.new(nm.outputs['Normal'],bs.inputs['Normal'])
    if orm:
        tx=m.node_tree.nodes.new('ShaderNodeTexImage');tx.image=orm;sep=m.node_tree.nodes.new('ShaderNodeSeparateColor')
        m.node_tree.links.new(tx.outputs['Color'],sep.inputs['Color']);m.node_tree.links.new(sep.outputs['Green'],bs.inputs['Roughness']);m.node_tree.links.new(sep.outputs['Blue'],bs.inputs['Metallic'])
    return m

def wood_material():
    n=1024;u,v=np.meshgrid(np.arange(n)/n,np.arange(n)/n);rng=np.random.default_rng(10)
    warp=.15*np.sin(u*18)+.06*np.sin(u*43+v*6)
    grain=np.sin(v*2*math.pi*78+warp*10)+.4*np.sin(v*2*math.pi*203+warp*24)
    broad=.6*np.sin(v*2*math.pi*9+u*4)+.4*np.sin(v*2*math.pi*19-u*5)
    noise=rng.normal(0,.006,(n,n));c=np.ones((n,n,4),np.float32)
    # Dark oiled walnut rather than the too-light orange finish_v1 test.
    irregular=np.zeros_like(u)
    for _ in range(18):
        irregular+=np.sin(u*rng.uniform(3,25)+v*rng.uniform(40,230)+rng.uniform(0,7))/18
    c[:,:,:3]=np.array((.12,.043,.015))+grain[:,:,None]*np.array((.003,.0018,.0007))+broad[:,:,None]*np.array((.009,.004,.0015))+irregular[:,:,None]*np.array((.035,.012,.004))+noise[:,:,None]*.15
    base=image_data('V10_Walnut_BaseColor',np.clip(c,0,1))
    orm=np.ones_like(c);orm[:,:,1]=np.clip(.64+grain*.02+noise,0,1);orm[:,:,2]=0
    om=image_data('V10_Walnut_ORM',orm,'Non-Color')
    nm=np.ones_like(c);nm[:,:,0]=.5;nm[:,:,1]=.5+np.cos(v*2*math.pi*78+warp*10)*.022;nm[:,:,2]=1
    ni=image_data('V10_Walnut_Normal',nm,'Non-Color')
    return principled('V10_Oiled_Walnut',(.12,.043,.015),0,.64,base,ni,om)

def donor_material(mat):
    if mat.name in MAT_CACHE:return MAT_CACHE[mat.name]
    nodes=mat.node_tree.nodes;albedo=nodes.get('Image Texture').image;normal=nodes.get('Image Texture.002').image
    w,h=albedo.size;data=np.empty(w*h*4,np.float32);albedo.pixels.foreach_get(data);data=data.reshape(h,w,4)
    luminance=data[:,:,:3].mean(axis=2);baked=np.ones_like(data)
    baked[:,:,:3]=np.array((.19,.215,.235))*(.75+.45*luminance[:,:,None])
    base=image_data('V10_Steel_'+mat.name.replace('.','_'),baked)
    out=principled('V10_DonorSteel_'+str(len(MAT_CACHE)),(.19,.215,.235),1,.48,base,normal)
    MAT_CACHE[mat.name]=out;return out

def mesh_object(name,verts,faces,material,uvs=None,smooth=True):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
    obj=bpy.data.objects.new(name,me);SCENE.collection.objects.link(obj);me.materials.append(material)
    for f in me.polygons:f.use_smooth=smooth
    layer=me.uv_layers.new(name='UVMap')
    if uvs:
        for f,uv in zip(me.polygons,uvs):
            for li,p in zip(f.loop_indices,uv):layer.data[li].uv=p
    else:
        for f in me.polygons:
            for li in f.loop_indices:
                p=me.vertices[me.loops[li].vertex_index].co;layer.data[li].uv=((p.x-BUTT)/1.105,p.y*12+p.z*7)
    ASSET.append(obj);return obj

def extract(name,target,component=None,kind=None):
    src=bpy.data.objects[name];me=src.data
    row=next(x for x in DIAG if x['name']==name)
    ids=row['components'][component]['face_ids'] if component is not None else list(range(len(me.polygons)))
    uv=me.uv_layers.active;cn=me.corner_normals;verts=[];remap={};faces=[];uvs=[];normals=[]
    rotation=src.matrix_world.to_3x3().inverted().transposed()
    for i in ids:
        f=me.polygons[i];face=[];coords=[]
        for vi,li in zip(f.vertices,f.loop_indices):
            q=(src.matrix_world@me.vertices[vi].co-ANCHOR)*.01;n=(rotation@cn[li].vector).normalized()
            if kind=='barrel':
                factor=barrel_factor(q.x);df=-.35/(TIP-.254118) if .254118<q.x<TIP else 0
                n=Vector((n.x-df*q.y/factor*n.y-df*q.z/factor*n.z,n.y/factor,n.z/factor)).normalized()
                q.y*=factor;q.z*=factor
            if kind=='trigger':q.z+=.009
            if vi not in remap:remap[vi]=len(verts);verts.append(tuple(q))
            face.append(remap[vi]);coords.append(tuple(uv.data[li].uv));normals.append(tuple(n))
        faces.append(face);uvs.append(coords)
    obj=mesh_object(target,verts,faces,donor_material(me.materials[0]),uvs)
    obj.data.normals_split_custom_set(normals);obj.data.update()
    err=max(abs(obj.data.uv_layers.active.data[li].uv[k]-p[k]) for f,c in zip(obj.data.polygons,uvs) for li,p in zip(f.loop_indices,c) for k in range(2))
    assert err<1e-7
    RETAINED.append({'source':name,'component':component,'candidate':target,'faces':len(faces),'uv_max_error':err,'transform':kind or 'normalized rigid only'})
    return obj

def loft(name,rings,mat,caps=True):
    n=len(rings[0]);verts=[p for ring in rings for p in ring];faces=[];uvs=[]
    assert all(len(r)==n for r in rings)
    for i in range(len(rings)-1):
        for j in range(n):
            k=(j+1)%n;faces.append((i*n+j,i*n+k,(i+1)*n+k,(i+1)*n+j))
            # longitudinal texture grain on all station-built parts.
            uvs.append([((verts[t][0]-BUTT)/1.105,jj/n) for t,jj in zip(faces[-1],(j,j+1,j+1,j))])
    if caps:faces.extend([tuple(range(n-1,-1,-1)),tuple((len(rings)-1)*n+j for j in range(n))]);uvs.extend([[(.5+.5*math.cos(2*math.pi*j/n),.5+.5*math.sin(2*math.pi*j/n)) for j in range(n)][::-1],[(.5+.5*math.cos(2*math.pi*j/n),.5+.5*math.sin(2*math.pi*j/n)) for j in range(n)]])
    obj=mesh_object(name,verts,faces,mat,uvs)
    # Constructed rings may have clockwise winding; establish signed volume globally.
    import bmesh
    bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free();return obj

def stock_ring(x):
    x,w,top,bottom,g=interp(x);r=radius(x);ring=[]
    for t in np.linspace(0,math.pi,33):ring.append((x,w*math.cos(t),top+(bottom-top)*math.sin(t)))
    for t in np.linspace(0,1,49)[1:-1]:
        y=-w+2*w*t;roof=top+.006*math.sin(math.pi*t)
        channel=-math.sqrt(max(0,r*r-y*y)) if abs(y)<r else top
        ring.append((x,y,(1-g)*roof+g*channel))
    return ring

def handguard_ring(x):
    r=radius(x)+.0003;outer=r+.0047;ring=[]
    for t in np.linspace(0,math.pi,25):ring.append((x,outer*math.cos(t),outer*math.sin(t)-.0015))
    for t in np.linspace(math.pi,0,25):ring.append((x,r*math.cos(t),r*math.sin(t)-.0015))
    return ring

def band_ring(x,inflation):
    _,w,top,bottom,_=interp(x);ring=[]
    for t in np.linspace(0,math.pi,33):ring.append((x,(w+inflation)*math.cos(t),top+(bottom-top-inflation)*math.sin(t)))
    r=radius(x)+.005+inflation
    for t in np.linspace(math.pi,0,25):ring.append((x,r*math.cos(t),r*math.sin(t)-.0015))
    return ring

def band(name,x,width):
    # Metal shell follows outer stock + handguard, not an unrelated convex hull.
    r0=band_ring(x-width/2,.0001);r1=band_ring(x-width/2,.0013);r2=band_ring(x+width/2,.0013);r3=band_ring(x+width/2,.0001)
    rings=[r0,r1,r2,r3,r0];return loft(name,rings,STEEL,caps=False)

def box(name,loc,scale,mat,bevel=.0008):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);obj=bpy.context.object;obj.name=name
    obj.data.name=name
    # Operator links into active source scene: link only the authored scene.
    for c in list(obj.users_collection):c.objects.unlink(obj)
    SCENE.collection.objects.link(obj);obj.dimensions=scale
    bpy.context.view_layer.objects.active=obj;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    obj.data.materials.append(mat);obj.data.uv_layers.new(name='UVMap') if not obj.data.uv_layers else None
    be=obj.modifiers.new('Manufactured edge','BEVEL');be.width=bevel;be.segments=3
    for f in obj.data.polygons:f.use_smooth=True
    no=obj.modifiers.new('Face normal balance','WEIGHTED_NORMAL');no.keep_sharp=True
    ASSET.append(obj);return obj

def tube(name,points,mat,width=.006,thick=.003):
    rings=[]
    for i,p in enumerate(points):
        q=Vector(p);t=(Vector(points[min(len(points)-1,i+1)])-Vector(points[max(0,i-1)])).normalized();side=Vector((0,1,0));up=t.cross(side).normalized()
        rings.append([tuple(q+side*math.cos(a)*width+up*math.sin(a)*thick) for a in np.linspace(0,2*math.pi,12,endpoint=False)])
    return loft(name,rings,mat)

def profile_piece(name,xz,width,mat,bevel):
    n=len(xz);verts=[(x,y,z) for y in [-width/2,width/2] for x,z in xz]
    faces=[tuple(range(n-1,-1,-1)),tuple(n+i for i in range(n))]
    faces.extend((i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n))
    obj=mesh_object(name,verts,faces,mat,smooth=False)
    import bmesh
    bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
    mod=obj.modifiers.new('Small edge radius','BEVEL');mod.width=bevel;mod.segments=3
    return obj

def camera(name,center,dir,scale):
    obj=bpy.data.objects.new(name,bpy.data.cameras.new(name));SCENE.collection.objects.link(obj);obj.data.type='ORTHO';obj.data.ortho_scale=scale
    target=Vector(center)-PIVOT
    obj.location=target+Vector(dir).normalized()*3;obj.rotation_euler=(target-obj.location).to_track_quat('-Z','Y').to_euler();return obj

def evidence(prefix,engine):
    SCENE.render.engine=engine;SCENE.render.resolution_x=1400;SCENE.render.resolution_y=850;SCENE.render.resolution_percentage=100
    if engine=='CYCLES':SCENE.cycles.samples=32;SCENE.cycles.use_denoising=True
    else:SCENE.display.shading.color_type='SINGLE';SCENE.display.shading.single_color=(.55,.55,.55);SCENE.display.shading.show_cavity=True;SCENE.display.shading.light='STUDIO'
    for name,center,direction,scale in [('right',(.17,0,-.05),(0,-1,0),1.28),('left',(.17,0,-.05),(0,1,0),1.28),('quarter',(.17,0,-.04),(1,-2,1.1),1.25),('top',(.17,0,-.02),(0,0,1),1.28),('underside',(.17,0,-.04),(.2,-1,-1),1.28),('receiver',(.10,0,-.025),(-.15,-1,.65),.47)]:
        cam=camera('View_'+prefix+'_'+name,center,direction,scale);SCENE.camera=cam;SCENE.render.filepath=str(OUT/(prefix+'_'+name+'.png'));bpy.ops.render.render(write_still=True,scene=SCENE.name)

def main():
    global OUT,SCENE,ASSET,MAT_CACHE,DIAG,RETAINED,STEEL,PIVOT
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--mode',choices=['gray','finish'],default='gray');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    OUT=Path(a.out).resolve();assert not OUT.exists(),'Use a new output identity';OUT.mkdir(parents=True)
    DIAG=json.loads((BASE/'source_diagnosis_v1/components.json').read_text());ASSET=[];MAT_CACHE={};RETAINED=[]
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    SCENE=bpy.data.scenes.new('V10_Donor_Adapted_Rifle');SCENE.unit_settings.system='METRIC';SCENE.unit_settings.scale_length=1
    bpy.context.window.scene=SCENE
    steel_img=image_data('V10_NewSteel_BaseColor',np.broadcast_to(np.array((.17,.195,.215,1),np.float32),(64,64,4)).copy())
    STEEL=principled('V10_New_BluedSteel',(.17,.195,.215),1,.48,steel_img)
    WOOD=wood_material()
    extract('Mesh_1.034','Receiver_Donor_Lower',0)
    extract('Mesh_0.073','Bolt_Donor_HandleCaps')
    extract('Mesh_3.020','Bolt_Donor_TubeSafety')
    extract('Mesh_4.017','Trigger_Donor',1,'trigger')
    extract('Mesh_0.074','Barrel_Donor_Tapered',kind='barrel')
    extract('Mesh_1.035','Muzzle_Donor_Insert',kind='barrel')
    xs=sorted(set(float(x) for i in range(len(STATIONS)-1) for x in np.linspace(STATIONS[i][0],STATIONS[i+1][0],5))|{STATIONS[-1][0]})
    loft('Wood_ContinuousStock', [stock_ring(x) for x in xs],WOOD)
    loft('Wood_UpperHandguard',[handguard_ring(x) for x in np.linspace(.256,.578,23)],WOOD)
    band('Furniture_RearBand',.425,.020);band('Furniture_FrontBand',.56,.022)
    # Thin butt plate follows the actual butt contour.
    rings=[]
    for x in [BUTT-.002,BUTT-.0003]:
        ring=stock_ring(BUTT);rings.append([(x,y,z) for _,y,z in ring])
    loft('Furniture_ButtPlate',rings,STEEL)
    box('Furniture_FloorPlate',(.12,0,-.048),(.145,.026,.006),STEEL)
    box('Guard_Roof',(.032,0,-.043),(.093,.014,.006),STEEL)
    pts=[]
    for t in np.linspace(math.pi,2*math.pi,49):pts.append((.034+.041*math.cos(t),0,-.044+.039*math.sin(t)))
    tube('Guard_OpenBow',pts,STEEL)
    profile_piece('Sight_RearBed',[(.254,.015),(.322,.015),(.316,.025),(.268,.025)],.022,STEEL,.0015)
    box('Sight_TangentLeaf',(.313,0,.027),(.098,.016,.004),STEEL)
    for y in [-.006,.006]:box('Sight_RearNotchEar_'+str(y),(.267,y,.032),(.007,.005,.01),STEEL,.0005)
    for x in [.285,.314,.344]:box('Sight_LeafGroove_'+str(x),(x,0,.0294),(.0015,.009,.0005),STEEL,.00015)
    profile_piece('Sight_FrontBed',[(.687,-.001),(.716,-.001),(.711,.013),(.693,.013)],.017,STEEL,.0015)
    profile_piece('Sight_FrontBlade',[(.697,.012),(.705,.012),(.703,.031),(.699,.031)],.0026,STEEL,.0004)
    # Receiver barrel shoulder / bedding bands support the retained metal.
    box('Receiver_Underbed',(.13,0,-.026),(.24,.015,.006),STEEL)
    deps=bpy.context.evaluated_depsgraph_get()
    points=[o.matrix_world@Vector(c) for o in ASSET for c in o.evaluated_get(deps).bound_box]
    PIVOT=Vector([(min(q[k] for q in points)+max(q[k] for q in points))*.5 for k in range(3)])
    root=bpy.data.objects.new('RifleRoot_Centered',None);SCENE.collection.objects.link(root)
    for o in ASSET:o.location-=PIVOT;o.parent=root
    SCENE.world=bpy.data.worlds.new('V10_Studio');SCENE.world.use_nodes=True
    SCENE.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.12,.12,1);SCENE.world.node_tree.nodes['Background'].inputs[1].default_value=.7
    for i,(loc,energy,size) in enumerate([((.1,-1,1.5),170,1.4),((.2,1,1),110,1.2),((.4,-.5,-1),45,1)]):
        light=bpy.data.objects.new('StudioLight'+str(i),bpy.data.lights.new('StudioLight'+str(i),'AREA'));SCENE.collection.objects.link(light);light.location=loc
        light.location-=PIVOT
        light.rotation_euler=(Vector((.17,0,-.03))-PIVOT-light.location).to_track_quat('-Z','Y').to_euler();light.data.energy=energy;light.data.shape='DISK';light.data.size=size
    SCENE.view_settings.view_transform='AgX'
    evidence('gray','BLENDER_WORKBENCH')
    if a.mode=='finish':evidence('pbr','CYCLES')
    SCENE.render.engine='CYCLES';SCENE.cycles.samples=32
    SCENE.camera=bpy.data.objects.get('View_pbr_quarter') or bpy.data.objects.get('View_gray_quarter')
    bpy.ops.object.select_all(action='DESELECT')
    for obj in ASSET:obj.select_set(True)
    root.select_set(True)
    bpy.context.view_layer.objects.active=ASSET[0]
    glb=OUT/'GermanRifle_SPR_V10.glb'
    bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_yup=True,export_vertex_color='NONE',export_animations=False,export_apply=True)
    # Library write contains only this scene and dependencies, never the full source library.
    packed_path=OUT/'GermanRifle_SPR_V10.blend'
    bpy.data.libraries.write(str(packed_path),{SCENE},path_remap='RELATIVE',fake_user=False)
    deps=bpy.context.evaluated_depsgraph_get();tri=0
    for o in ASSET:
        me=o.evaluated_get(deps).to_mesh();me.calc_loop_triangles();tri+=len(me.loop_triangles);o.evaluated_get(deps).to_mesh_clear()
    assert tri<40000,tri
    report={'stage':a.mode,'blender':bpy.app.version_string,'meshes':len(ASSET),'triangles_evaluated':tri,'length_target_m':TIP-(BUTT-.002),'pivot_shift':list(PIVOT),
            'retained':RETAINED,'excluded':['modern synthetic stock','scope','rail component','cheek riser','external magazine','mag release','forward shroud'],
            'sha256_glb':hashlib.sha256(glb.read_bytes()).hexdigest(),'historical_approval':False,'runtime_approval':False,'user_visual_approval':False}
    (OUT/'build_report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
    # Reopen only the small dependency closure, then save as a normal interactive document.
    # Never save the 2.2GiB delivery currently loaded in memory.
    bpy.ops.wm.open_mainfile(filepath=str(packed_path),load_ui=False,use_scripts=False)
    bpy.context.window.scene=bpy.data.scenes['V10_Donor_Adapted_Rifle']
    bpy.context.scene.camera=bpy.data.objects.get('View_pbr_quarter') or bpy.data.objects.get('View_gray_quarter')
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(packed_path))

if __name__=='__main__':main()
