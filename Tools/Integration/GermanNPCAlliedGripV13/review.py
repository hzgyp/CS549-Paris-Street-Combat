"""Fresh full-skin reconstruction and matched pose review; never a runtime mesh."""
import sys, json, struct, traceback
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'GermanNPCGripV1'))
from common import ROOT,STORE,GLB,read,write,row,sha,guards
sys.path.insert(0,str(ROOT/'Tools/Integration/WeaponTriggerAlignmentV2'))
from blender_contact_common import mat,transform
BASE=STORE/'Evidence/GermanNPCAlliedGripV13'
TEXTURED='--textured' in sys.argv; FINAL='--seated' in sys.argv;REFERENCE='--reference' in sys.argv
FIT=BASE/('seating_v3/result.json' if FINAL else 'transfer_fit_v2/result.json' if REFERENCE else 'transfer_fit_v1/result.json')
OUT=BASE/(('textured' if TEXTURED else 'gray')+('_v3' if FINAL else '_v2' if REFERENCE else '_v1')+('_viewer_repair' if '--viewer-repair' in sys.argv else ''))
GD=STORE/'Evidence/GermanNPCOrderedGripV4/offline_v6/geometry.npz'
LAB=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/character-ue582-v1/Evidence/Repair20261001/Exchange'
FBX=LAB/'SK_WWII_GermanSoldier_varA.fbx';MAT=LAB/'SK_WWII_GermanSoldier_varA.blend'
assert not OUT.exists();OUT.mkdir(parents=True)
r={'status':'starting','errors':[],'guards_before':guards(),'inputs':[row(p) for p in (FIT,GD,GLB,Path(__file__))],
   'formal_selected':False,'source_modified':False,'native_tested':False,'contact_accepted':False,'images':[],'textured':TEXTURED}
try:
    fit=read(FIT);assert not fit['errors']
    d=np.load(GD);saved=np.load(FIT.parent/'geometry.npz');names=fit['bone_names'];parents=fit['parents'];rest=d['rest_native_cm'];w=d['weights'];refs=d['reference_matrices'];tri=d['skin_triangles'];gt=d['gun_triangles']
    bones={s:{n:mat(v) for n,v in fit[s+'_bones'].items()} for s in ('before','after')}
    def skin(b):
        out=np.zeros_like(rest)
        for j,n in enumerate(names):out+=w[:,j,None]*transform(rest,b[n]@np.linalg.inv(refs[j]))
        return out/w.sum(1)[:,None]
    positions={s:skin(bones[s]) for s in bones};guns={s:transform(d['gun_local_cm'],mat(fit[s+'_gun_world'])) for s in bones}
    r['fresh_skin_error_cm']=float(np.linalg.norm(positions['after']-saved['skin'],axis=1).max())
    r['fresh_gun_error_cm']=float(np.linalg.norm(guns['after']-saved['gun_after_cm'],axis=1).max())
    assert max(r['fresh_skin_error_cm'],r['fresh_gun_error_cm'])<.01
    origin=bones['after']['hand_r'][:3,3];bpy.ops.wm.read_factory_settings(use_empty=True)
    def mesh(name,p,t,flip=False):
        m=bpy.data.meshes.new(name);m.from_pydata(((p-origin)*.01).tolist(),[],(t[:,::-1] if flip else t).tolist());m.update()
        o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o);return o
    def material(name,color):
        m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);return m
    body=mesh('Full German source topology - diagnostic ONLY',positions['after'],tri,True)
    gun=mesh('Actual German rifle original topology',guns['after'],gt)
    if TEXTURED:
        r['inputs'] +=[row(FBX),row(MAT)]
        bpy.ops.import_scene.fbx(filepath=str(FBX),automatic_bone_orientation=False,use_anim=False)
        imported=[o for o in bpy.context.scene.objects if o.type=='MESH' and o not in (body,gun)]
        assert len(imported)==1;src=imported[0];src.data.calc_loop_triangles();ts=list(src.data.loop_triangles)
        assert np.array_equal(np.array([list(t.vertices) for t in ts]),tri)
        assert len(src.data.vertices)==len(rest)
        with bpy.data.libraries.load(str(MAT),link=False) as (lib,loaded):loaded.materials=list(lib.materials)
        def material_key(name):return name.removesuffix('.001').removesuffix('_portable')
        portable={material_key(m.name):m for m in loaded.materials}
        for m in src.data.materials:
            key=material_key(m.name)
            assert key in portable,(m.name,list(portable));body.data.materials.append(portable[key])
        for poly,t in zip(body.data.polygons,ts):poly.material_index=t.material_index;poly.use_smooth=True
        for uv in src.data.uv_layers:
            layer=body.data.uv_layers.new(name=uv.name);coords=np.array([[list(uv.data[i].uv) for i in t.loops] for t in ts])[:,::-1].reshape(-1,2)
            for item,co in zip(layer.data,coords):item.uv=co
        for o in bpy.context.scene.objects:
            if o not in (body,gun):o.hide_render=True
        existing=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(GLB))
        imported=set(bpy.data.objects)-existing
        material_by_node={o.name:o.data.materials[:] for o in imported if o.type=='MESH'}
        blob=GLB.read_bytes();count=struct.unpack_from('<I',blob,12)[0];gltf=json.loads(blob[20:20+count]);binary=blob[28+count:]
        def acc(index):
            a=gltf['accessors'][index];v=gltf['bufferViews'][a['bufferView']];dim={'SCALAR':1,'VEC2':2}[a['type']]
            assert 'byteStride' not in v and 'sparse' not in a
            dtype={5126:'<f4',5123:'<u2',5125:'<u4',5121:'u1'}[a['componentType']]
            return np.frombuffer(binary,dtype=dtype,count=a['count']*dim,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(a['count'],dim)
        corners=[];slots=[];vbase=0;fbase=0
        for node in gltf['nodes']:
            if 'mesh' not in node:continue
            mats=material_by_node[node['name']]
            for j,prim in enumerate(gltf['meshes'][node['mesh']]['primitives']):
                indices=acc(prim['indices']).ravel().reshape(-1,3).astype(int);uv=acc(prim['attributes']['TEXCOORD_0']).copy();uv[:,1]=1-uv[:,1]
                assert np.array_equal(indices+vbase,gt[fbase:fbase+len(indices)])
                corners.extend(uv[indices]);slots.extend([len(gun.data.materials)]*len(indices));gun.data.materials.append(mats[j])
                vbase+=gltf['accessors'][prim['attributes']['POSITION']]['count'];fbase+=len(indices)
        assert fbase==len(gt) and vbase==len(d['gun_local_cm'])
        layer=gun.data.uv_layers.new(name='TEXCOORD_0')
        for item,co in zip(layer.data,np.array(corners).reshape(-1,2)):item.uv=co
        for poly,slot in zip(gun.data.polygons,slots):poly.material_index=slot;poly.use_smooth=True
        for o in imported:o.hide_render=True
        r['texture_images']=[]
        for img in bpy.data.images:
            if img.name in ('Render Result','Viewer Node'):continue
            # Source blend retains valid absolute external paths. Do not
            # manufacture new textures or remap on a guessed filename.
            if not img.packed_file:
                path=Path(bpy.path.abspath(img.filepath)).resolve();assert path.is_file(),str(path)
                img.filepath=str(path);img.reload();r['texture_images'].append(row(path))
            assert img.size[0]>0,img.name
        r['portable_pbr_not_native_ue_shader_parity']=True
    else:
        mats=[material('Original body',(.28,.33,.37)),material('Hand',(.63,.50,.36)),material('Thumb',(.9,.38,.1)),material('Transferred index',(.18,.48,.85))]
        for m in mats:body.data.materials.append(m)
        hand=w[:,[j for j,n in enumerate(names) if n.startswith(('hand_','thumb_','index_','middle_','ring_','pinky_'))]].sum(1)>.5
        thumb=w[:,[names.index('thumb_'+i+'_r') for i in ('01','02','03')]].sum(1)>.5
        index=w[:,[names.index('index_'+i+'_r') for i in ('01','02','03')]].sum(1)>.5
        for i,poly in enumerate(body.data.polygons):poly.material_index=2 if np.all(thumb[tri[i]]) else 3 if np.all(index[tri[i]]) else 1 if np.all(hand[tri[i]]) else 0
        gun.data.materials.append(material('Unchanged gun',(.20,.20,.20)))
    scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE' if TEXTURED else 'BLENDER_WORKBENCH';scene.render.resolution_x=1200;scene.render.resolution_y=850;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX' if TEXTURED else 'Standard'
    scene.world=bpy.data.worlds.new('ReviewWorld');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.075,.085,.10,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5
    scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.background_type='WORLD'
    center=(origin+bones['after']['hand_l'][:3,3])/2
    if TEXTURED:
        if hasattr(scene.eevee,'taa_render_samples'):scene.eevee.taa_render_samples=32
        for name,offset,power in [('Key',(0,-1,1.5),110),('Fill',(0,1,1),65),('Rim',(-1,0,.8),50)]:
            ld=bpy.data.lights.new(name,'AREA');ld.energy=power;ld.size=1.2;o=bpy.data.objects.new(name,ld);bpy.context.collection.objects.link(o)
            o.location=Vector((center-origin)*.01)+Vector(offset);o.rotation_euler=(Vector((center-origin)*.01)-o.location).to_track_quat('-Z','Y').to_euler()
    cd=bpy.data.cameras.new('MatchedCamera');cam=bpy.data.objects.new('MatchedCamera',cd);bpy.context.collection.objects.link(cam);scene.camera=cam;cd.type='ORTHO'
    idx=(bones['after']['index_02_r'][:3,3]+bones['after']['index_03_r'][:3,3])/2
    views=[('right',(0,-.5,.07),.34,origin),('reverse',(0,.5,.07),.34,origin),('top',(0,0,.6),.38,origin),
       ('trigger',(0,-.5,.05),.17,idx),('support',(0,-.5,.07),.38,bones['after']['hand_l'][:3,3]),('context',(0,-2,.28),1.30,center)]
    for stage in ('before','after'):
        for obj,pts in ((body,positions[stage]),(gun,guns[stage])):
            for vert,pos in zip(obj.data.vertices,(pts-origin)*.01):vert.co=pos
            obj.data.update()
        for name,offset,width,target in (views[:3] if stage=='before' else views):
            dest=OUT/(stage+'_'+name+'.png');v=Vector((target-origin)*.01);cam.location=v+Vector(offset);cam.rotation_euler=(v-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=width
            scene.render.filepath=str(dest);bpy.ops.render.render(write_still=True);r['images'].append(row(dest));write(OUT/'result.json',r)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'GermanGraspDiagnostic.blend'))
    r['status']='fresh_full_skin_original_geometry_views_require_review'
except Exception:r['status']='review_failed_preserved';r['errors'].append(traceback.format_exc())
finally:
    r['guards_after']=guards();r['inputs_unchanged']=all(sha(ROOT/e['path'])==e['sha256'] for e in r['inputs']);write(OUT/'result.json',r)
    print({k:r.get(k) for k in ('status','errors','fresh_skin_error_cm','fresh_gun_error_cm','textured')})
