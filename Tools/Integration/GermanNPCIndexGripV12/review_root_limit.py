"""Read-only cause evidence for the retained complete-grasp translation limit."""
import sys,json,struct,traceback
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'GermanNPCGripV1'))
from common import ROOT,STORE,GLB,read,write,row,sha,guards,tm
sys.path.insert(0,str(ROOT/'Tools/Integration/WeaponTriggerAlignmentV2'))
from blender_contact_common import mat,transform,intersection_pairs
sys.path.insert(0,str(ROOT/'Tools/Integration/GermanNPCOrderedGripV4'))
from arm_fit import arm_targets,encode
BASE=STORE/'Evidence/GermanNPCIndexGripV12';OUT=BASE/'root_limit_views_v1'
assert not OUT.exists();OUT.mkdir(parents=True)
FIT=BASE/'complete_existing_grasp_v2/result.json'
PREV=STORE/'Evidence/GermanNPCLowerGripV11/source_frame_v4/result.json'
DATA=STORE/'Evidence/GermanNPCOrderedGripV4/offline_v6/geometry.npz'
CACHE=STORE/'Evidence/ReloadIndexContactV6/contact_exchange_v1/result.json'
paths=(FIT,PREV,DATA,CACHE,GLB,Path(__file__))
r={'status':'starting','errors':[],'guards_before':guards(),'inputs':[row(p) for p in paths],
   'formal_selected':False,'source_modified':False,'native_tested':False,'contact_accepted':False,'images':[],
   'failure_visualization_only':True}
write(OUT/'result.json',r)
try:
    fit=read(FIT);old=read(PREV);assert fit['status']=='failed_preserved' and fit['gun_translation_cm']>4
    for entry in fit['inputs']:assert sha(ROOT/entry['path'])==entry['sha256']
    d=np.load(DATA);names=old['bone_names'];parents=old['parents'];rest=d['rest_native_cm'];w=d['weights'];refs=d['reference_matrices'];tri=d['skin_triangles'];gp=d['gun_local_cm'];gt=d['gun_triangles']
    before={n:mat(v) for n,v in old['after_bones'].items()};after={n:m.copy() for n,m in before.items()}
    cache=read(CACHE);sample=next(s for t,s in cache['clips']['owner_reload']['samples'].items() if float(t)==2.2)
    src={n:mat(v) for n,v in sample['bones_component'].items()}
    for n in ('index_01_r','index_02_r','index_03_r'):
        p=parents[n];loc=np.linalg.inv(before[p])@before[n];donor=np.linalg.inv(src[p])@src[n]
        loc[:3,:3]=donor[:3,:3]/np.linalg.norm(donor[:3,:3],axis=0)*np.linalg.norm(loc[:3,:3],axis=0)
        after[n]=after[p]@loc
    g0=old['after_gun_world'];g1=dict(g0);g1['t']=(np.array(g0['t'])+fit['gun_translation_world_cm']).tolist()
    change=mat(g1)@np.linalg.inv(mat(g0));after,arm=arm_targets(after,{'l':change@after['hand_l']},parents)
    def skin(b):
        p=np.zeros_like(rest)
        for j,n in enumerate(names):p+=w[:,j,None]*transform(rest,b[n]@np.linalg.inv(refs[j]))
        return p/w.sum(1)[:,None]
    p0,p1=skin(before),skin(after);g0p,g1p=transform(gp,mat(g0)),transform(gp,mat(g1))
    blob=GLB.read_bytes();gltf=json.loads(blob[20:20+struct.unpack_from('<I',blob,12)[0]]);at=0;groups={'wood':set(),'guard':set(),'blade':set()}
    for node in gltf['nodes']:
        if 'mesh' not in node:continue
        for prim in gltf['meshes'][node['mesh']]['primitives']:
            count=gltf['accessors'][prim['indices']]['count']//3;ids=set(range(at,at+count))
            if node['name'].startswith('Wood_'):groups['wood']|=ids
            if node['name'].startswith('Guard_'):groups['guard']|=ids
            if node['name']=='Trigger_Donor':groups['blade']|=ids
            at+=count
    r['contacts']={}
    for stage,p,g in (('before',p0,g0p),('after',p1,g1p)):
        woodtree=BVHTree.FromPolygons([Vector(v) for v in g],gt[sorted(groups['wood'])].tolist(),all_triangles=True)
        blade=BVHTree.FromPolygons([Vector(v) for v in g],gt[sorted(groups['blade'])].tolist(),all_triangles=True)
        c={}
        for digit in ('thumb','index','middle','ring','pinky'):
            mask=w[:,[names.index(digit+'_'+i+'_r') for i in ('01','02','03')]].sum(1)>0
            fs=np.flatnonzero(np.any(mask[tri],axis=1));pairs=intersection_pairs(p,tri[fs],g,gt)
            c[digit]={group:len({int(fs[a]) for a,b in pairs if b in ids}) for group,ids in groups.items()}
            if digit in old['fixed_pad_face_ids']:
                c[digit]['mean_pad_wood_gap_cm']=float(np.mean([woodtree.find_nearest(Vector(v))[3] for v in p[tri[old['fixed_pad_face_ids'][digit]]].mean(1)]))
        c['index']['pad_blade_gap_cm']=float(np.mean([blade.find_nearest(Vector(v))[3] for v in p[tri[fit['actual_pad_face_ids']]].mean(1)]))
        r['contacts'][stage]=c
    r.update(original_length_arm_checks=arm,bone_names=names,parents=parents,
      before_bones=old['after_bones'],after_bones={n:encode(v) for n,v in after.items()},
      before_gun_world=g0,after_gun_world=g1,mesh_world=old['mesh_world'])
    np.savez_compressed(OUT/'diagnostic_geometry.npz',skin=p1,before_skin=p0,skin_triangles=tri,gun_before_cm=g0p,gun_after_cm=g1p,gun_triangles=gt)
    origin=before['hand_r'][:3,3];bpy.ops.wm.read_factory_settings(use_empty=True)
    def material(name,color):
        m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);return m
    mats=[material('Full original body',(.29,.34,.38)),material('Original hands',(.58,.47,.35)),
      material('Accepted thumb',(.92,.34,.1)),material('Right index curl',(.12,.44,.85)),
      material('Accepted lower-three',(.62,.47,.25))]
    def mesh(name,points,faces,flip=False):
        md=bpy.data.meshes.new(name);md.from_pydata(((points-origin)*.01).tolist(),[],(faces[:,::-1] if flip else faces).tolist());md.update()
        o=bpy.data.objects.new(name,md);bpy.context.collection.objects.link(o);return o
    body=mesh('Full original skin',p0,tri,True);gun=mesh('Entire original rifle',g0p,gt)
    gun.data.materials.append(material('Rifle gray',(.22,.22,.22)))
    for m in mats:body.data.materials.append(m)
    def mask(prefixes):return w[:,[j for j,n in enumerate(names) if n.startswith(prefixes)]].sum(1)>.5
    thumb=mask(('thumb_01_r','thumb_02_r','thumb_03_r'));idx=mask(('index_01_r','index_02_r','index_03_r'))
    lower=mask(('middle_01_r','middle_02_r','middle_03_r','ring_01_r','ring_02_r','ring_03_r','pinky_01_r','pinky_02_r','pinky_03_r'))
    hands=mask(('hand_','thumb_','index_','middle_','ring_','pinky_'))
    for i,poly in enumerate(body.data.polygons):
        ids=tri[i];poly.material_index=2 if np.all(thumb[ids]) else 3 if np.all(idx[ids]) else 4 if np.all(lower[ids]) else 1 if np.all(hands[ids]) else 0
    scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1200;scene.render.resolution_y=850;scene.render.resolution_percentage=100
    scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
    scene.display.shading.background_type='WORLD';scene.world=bpy.data.worlds.new('DiagnosticWorld');scene.world.color=(.055,.07,.085)
    scene.view_settings.view_transform='Standard';scene.render.image_settings.file_format='PNG'
    cd=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',cd);bpy.context.collection.objects.link(cam);cd.type='ORTHO';scene.camera=cam
    center=(before['index_01_r'][:3,3]+before['index_03_r'][:3,3])/2
    both=(origin+before['hand_l'][:3,3])/2
    for stage,points,g in (('before',p0,g0p),('after',p1,g1p)):
        for o,p in ((body,points),(gun,g)):
            for v,pos in zip(o.data.vertices,(p-origin)*.01):v.co=pos
            o.data.update()
        for name,offset,width,target in [('right',(0,-.4,.12),.28,center),('reverse',(0,.4,.12),.28,center),
          ('top',(0,0,.5),.30,center),('under',(0,0,-.5),.30,center),
          ('support',(0,-.4,.1),.38,before['hand_l'][:3,3]),('context',(0,-2,.25),1.25,both)]:
            target=Vector((target-origin)*.01);cam.location=target+Vector(offset);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=width
            dest=OUT/(stage+'_'+name+'.png');scene.render.filepath=str(dest);bpy.ops.render.render(write_still=True);r['images'].append(row(dest));write(OUT/'result.json',r)
    r['status']='over_limit_existing_grasp_failure_reconstructed_not_selected'
except Exception:r['errors'].append(traceback.format_exc());r['status']='review_failed_preserved'
finally:
    r['guards_after']=guards();r['inputs_unchanged']=all(sha(ROOT/e['path'])==e['sha256'] for e in r['inputs']);write(OUT/'result.json',r)
    print(r['status'],r['errors']);print(json.dumps(r.get('contacts'),indent=2))
