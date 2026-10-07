"""Fresh saved-pose reconstruction and fixed full-source views; no fitting."""
import sys,traceback
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'GermanNPCGripV1'))
from common import ROOT,STORE,read,write,row,sha,guards
sys.path.insert(0,str(ROOT/'Tools/Integration/WeaponTriggerAlignmentV2'))
from blender_contact_common import mat,transform
BASE=STORE/'Evidence/GermanNPCIndexGripV12';OUT=BASE/'final_views_v1';FIT=BASE/'distal_existing_grasp_v4b/result.json'
DATA=STORE/'Evidence/GermanNPCOrderedGripV4/offline_v6/geometry.npz';GEOM=FIT.parent/'diagnostic_geometry.npz'
assert not OUT.exists();OUT.mkdir(parents=True)
r={'status':'starting','errors':[],'guards_before':guards(),'inputs':[row(p) for p in (FIT,DATA,GEOM,Path(__file__))],
   'formal_selected':False,'source_modified':False,'native_tested':False,'contact_accepted':False,'images':[]}
write(OUT/'result.json',r)
try:
    fit=read(FIT)
    for e in fit['inputs']:assert sha(ROOT/e['path'])==e['sha256']
    d=np.load(DATA);saved=np.load(GEOM);names=fit['bone_names'];parents=fit['parents'];w=d['weights'];rest=d['rest_native_cm'];refs=d['reference_matrices'];tri=d['skin_triangles'];gt=d['gun_triangles']
    pose={s:{n:mat(v) for n,v in fit[s+'_bones'].items()} for s in ('before','after')}
    def skin(b):
        p=np.zeros_like(rest)
        for j,n in enumerate(names):p+=w[:,j,None]*transform(rest,b[n]@np.linalg.inv(refs[j]))
        return p/w.sum(1)[:,None]
    p0,p1=skin(pose['before']),skin(pose['after']);g0,g1=[transform(d['gun_local_cm'],mat(fit[s+'_gun_world'])) for s in ('before','after')]
    r.update(fresh_skin_error_cm=float(np.linalg.norm(p1-saved['skin'],axis=1).max()),fresh_gun_error_cm=float(np.linalg.norm(g1-saved['gun_after_cm'],axis=1).max()),
      source_vertices=len(p1),source_triangles=len(tri),gun_vertices=len(g1),gun_triangles=len(gt),
      protected_bone_matrix_error=float(max(np.max(abs(pose['after'][n]-pose['before'][n])) for n in fit['protected_bones'])),
      local_index_transforms={n:{s:(np.linalg.inv(pose[s][parents[n]])@pose[s][n]).tolist() for s in ('before','after')} for n in ('index_01_r','index_02_r','index_03_r')},
      original_fit_status=fit['status'],original_fit_errors=fit['errors'])
    assert max(r['fresh_skin_error_cm'],r['fresh_gun_error_cm'])<.01 and r['protected_bone_matrix_error']<1e-8
    origin=pose['before']['hand_r'][:3,3];bpy.ops.wm.read_factory_settings(use_empty=True)
    def material(name,c):
        m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);return m
    mats=[material('Full original skin',(.29,.34,.38)),material('Original hands',(.58,.47,.35)),material('Accepted thumb',(.92,.34,.1)),material('Index source curl',(.12,.44,.85)),material('Accepted lower-three',(.62,.47,.25))]
    def mesh(name,p,t,flip=False):
        m=bpy.data.meshes.new(name);m.from_pydata(((p-origin)*.01).tolist(),[],(t[:,::-1] if flip else t).tolist());m.update();o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o);return o
    body=mesh('Whole source German body',p0,tri,True);gun=mesh('Entire actual German gun',g0,gt)
    gun.data.materials.append(material('Gray original rifle',(.22,.22,.22)))
    for m in mats:body.data.materials.append(m)
    def mask(prefix):return w[:,[j for j,n in enumerate(names) if n.startswith(prefix)]].sum(1)>.5
    thumb=mask(('thumb_01_r','thumb_02_r','thumb_03_r'));idx=mask(('index_01_r','index_02_r','index_03_r'));lower=mask(('middle_01_r','middle_02_r','middle_03_r','ring_01_r','ring_02_r','ring_03_r','pinky_01_r','pinky_02_r','pinky_03_r'));hands=mask(('hand_','thumb_','index_','middle_','ring_','pinky_'))
    for i,poly in enumerate(body.data.polygons):
        vs=tri[i];poly.material_index=2 if np.all(thumb[vs]) else 3 if np.all(idx[vs]) else 4 if np.all(lower[vs]) else 1 if np.all(hands[vs]) else 0
    scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1200;scene.render.resolution_y=850;scene.render.resolution_percentage=100
    scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.background_type='WORLD'
    scene.world=bpy.data.worlds.new('DiagnosticWorld');scene.world.color=(.055,.07,.085);scene.view_settings.view_transform='Standard';scene.render.image_settings.file_format='PNG'
    cd=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',cd);bpy.context.collection.objects.link(cam);cd.type='ORTHO';scene.camera=cam
    indexcenter=(pose['before']['index_02_r'][:3,3]+pose['before']['index_03_r'][:3,3])/2
    both=(origin+pose['before']['hand_l'][:3,3])/2
    for stage,p,g in (('before',p0,g0),('after',p1,g1)):
        for o,points in ((body,p),(gun,g)):
            for v,pos in zip(o.data.vertices,(points-origin)*.01):v.co=pos
            o.data.update()
        for name,offset,width,target in [('right',(0,-.4,.12),.26,indexcenter),('reverse',(0,.4,.12),.26,indexcenter),('top',(0,0,.5),.28,indexcenter),('under',(0,0,-.5),.28,indexcenter),('support',(0,-.4,.1),.38,pose['before']['hand_l'][:3,3]),('context',(0,-2,.25),1.25,both)]:
            center=Vector((target-origin)*.01);cam.location=center+Vector(offset);cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=width
            dest=OUT/(stage+'_'+name+'.png');scene.render.filepath=str(dest);bpy.ops.render.render(write_still=True);r['images'].append(row(dest));write(OUT/'result.json',r)
    r['status']='fresh_reconstructed_distal_existing_pose_views_not_native_acceptance'
except Exception:r['errors'].append(traceback.format_exc());r['status']='review_failed_preserved'
finally:
    r['guards_after']=guards();r['inputs_unchanged']=all(sha(ROOT/e['path'])==e['sha256'] for e in r['inputs']);write(OUT/'result.json',r)
    print(r['status'],r['errors']);print({k:r.get(k) for k in ('fresh_skin_error_cm','fresh_gun_error_cm','protected_bone_matrix_error')})
