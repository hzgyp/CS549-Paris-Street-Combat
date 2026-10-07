"""Read-only reproduction of retained failed thumb pose for human marking, not a fit retry."""
import sys,traceback
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector,Matrix,Quaternion
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'GermanNPCGripV1'))
from common import ROOT,STORE,read,write,row,sha,guards
sys.path.insert(0,str(ROOT/'Tools/Integration/WeaponTriggerAlignmentV2'))
from blender_contact_common import mat,transform
BASE=STORE/'Evidence/GermanNPCRightThumbV6';OUT=BASE/'failure_views_v1'
assert not OUT.exists();OUT.mkdir(parents=True)
PREV=STORE/'Evidence/GermanNPCOrderedGripV4/offline_v6/result.json';DATA=PREV.parent/'geometry.npz'
FAILED=BASE/'vertical_lift_v2/result.json'
r={'errors':[],'guard_before':guards(),'inputs':[row(p) for p in (PREV,DATA,FAILED,Path(__file__))],
   'diagnostic_failed_pose_only':True,'source_modified':False,'formal_selected':False,'images':[]}
write(OUT/'result.json',r)
try:
    old=read(PREV);failed=read(FAILED);assert failed['status']=='failed_preserved' and failed['errors']
    assert failed['chosen']['stock_faces']==97
    d=np.load(DATA);names=old['bone_names'];parents=old['parents'];rest=d['rest_native_cm'];w=d['weights'];ref=d['reference_matrices'];tri=d['skin_triangles']
    before={n:mat(t) for n,t in old['after_bones'].items()};after={n:m.copy() for n,m in before.items()}
    for n in ('thumb_01_r','thumb_02_r','thumb_03_r'):
        p=parents[n];local=np.linalg.inv(before[p])@before[n]
        x,y,z,q=failed['chosen']['local_rotations'][n]
        local[:3,:3]=np.array(Quaternion((q,x,y,z)).to_matrix())*np.linalg.norm(local[:3,:3],axis=0)
        after[n]=after[p]@local
    origin=before['hand_r'][:3,3]
    def posed(bones):
        result=np.zeros_like(rest)
        for j,n in enumerate(names):result+=w[:,j,None]*transform(rest,bones[n]@np.linalg.inv(ref[j]))
        return result/w.sum(1)[:,None]
    p0,p1=posed(before),posed(after)
    mask=w[:,[names.index(n) for n in ('thumb_01_r','thumb_02_r','thumb_03_r')]].sum(1)>0
    assert np.linalg.norm(p1[~mask]-p0[~mask],axis=1).max()<.0001
    gp=transform(d['gun_local_cm'],mat(old['after_gun_world']));gt=d['gun_triangles']
    bpy.ops.wm.read_factory_settings(use_empty=True)
    def material(name,color):
        m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);return m
    mats=[material('Full original mesh gray',(.29,.34,.38)),material('Other hand skin',(.58,.47,.35)),material('Only adapted thumb orange',(.92,.34,.10)),material('Protected index blue',(.12,.44,.85))]
    def mesh(name,points,faces,flip=False):
        m=bpy.data.meshes.new(name);m.from_pydata(((points-origin)*.01).tolist(),[],(faces[:,::-1] if flip else faces).tolist());m.update()
        o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o);return o
    gun=mesh('Exact unchanged rifle',gp,gt);gun.data.materials.append(material('Original rifle diagnostic gray',(.22,.22,.22)))
    body=mesh('Full source skin diagnostic',p0,tri,True)
    for m in mats:body.data.materials.append(m)
    handidx=[j for j,n in enumerate(names) if n.endswith(('_r','_l')) and n.startswith(('hand_','thumb_','index_','middle_','ring_','pinky_'))]
    handmask=w[:,handidx].sum(1)>.5
    idx=w[:,[names.index(n) for n in ('index_01_r','index_02_r','index_03_r')]].sum(1)>.5
    for i,poly in enumerate(body.data.polygons):
        ids=tri[i]
        poly.material_index=2 if np.all(mask[ids]) else 3 if np.all(idx[ids]) else 1 if np.all(handmask[ids]) else 0
    scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1200;scene.render.resolution_y=850;scene.render.resolution_percentage=100
    scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True
    scene.display.shading.show_cavity=True;scene.display.shading.background_type='WORLD';scene.world.color=(.055,.07,.085)
    scene.view_settings.view_transform='Standard';scene.render.image_settings.file_format='PNG'
    cd=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',cd);bpy.context.collection.objects.link(cam);cd.type='ORTHO';scene.camera=cam
    thumb=(before['thumb_01_r'][:3,3]+before['thumb_03_r'][:3,3])/2
    handcenter=(origin+before['hand_l'][:3,3])/2
    for stage,points in (('before',p0),('after_failed',p1)):
        for v,position in zip(body.data.vertices,(points-origin)*.01):v.co=position
        body.data.update()
        for name,offset,width,target in [('reverse',(0,.4,.12),.25,thumb),('top',(0,0,.5),.3,thumb),('right',(0,-.4,.12),.25,thumb),('context',(0,-2,.25),1.25,handcenter)]:
            center=Vector((target-origin)*.01);cam.location=center+Vector(offset);cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=width
            dest=OUT/(stage+'_'+name+'.png');scene.render.filepath=str(dest);bpy.ops.render.render(write_still=True);r['images'].append(row(dest));write(OUT/'result.json',r)
    r['guards_after']=guards();r['inputs_unchanged']=all(sha(ROOT/e['path'])==e['sha256'] for e in r['inputs']);r['status']='failed_pose_diagnostic_views_only_not_candidate_acceptance'
except Exception:r['errors'].append(traceback.format_exc());r['status']='diagnostic_render_failed'
write(OUT/'result.json',r);print(r['status'],r['errors'])
