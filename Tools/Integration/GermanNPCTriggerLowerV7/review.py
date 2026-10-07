"""Fresh read-only reconstruction of retained 8-degree comparison; no fitting."""
import sys, traceback
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'GermanNPCGripV1'))
from common import ROOT,STORE,read,write,row,sha,guards
sys.path.insert(0,str(ROOT/'Tools/Integration/WeaponTriggerAlignmentV2'))
from blender_contact_common import mat,transform
BASE=STORE/'Evidence/GermanNPCTriggerLowerV7';OUT=BASE/'review_v1'
assert not OUT.exists();OUT.mkdir(parents=True)
FIT=BASE/'stock_down_v2/result.json'
DATA=STORE/'Evidence/GermanNPCOrderedGripV4/offline_v6/geometry.npz'
r={'status':'starting','errors':[],'guards_before':guards(),'inputs':[row(p) for p in (FIT,DATA,Path(__file__))],
   'formal_selected':False,'source_modified':False,'native_tested':False,'contact_accepted':False,'images':[]}
write(OUT/'result.json',r)
try:
    fit=read(FIT);assert fit['status']=='failed_preserved' and fit['rotation_deg']==8
    assert fit['protected_bone_matrix_error']<1e-8 and fit['new_severe_edges']==0
    d=np.load(DATA);names=fit['bone_names'];w=d['weights'];rest=d['rest_native_cm'];refs=d['reference_matrices'];tri=d['skin_triangles']
    poses={stage:{n:mat(v) for n,v in fit[stage+'_bones'].items()} for stage in ('before','after')}
    def skin(bones):
        p=np.zeros_like(rest)
        for j,n in enumerate(names):p+=w[:,j,None]*transform(rest,bones[n]@np.linalg.inv(refs[j]))
        return p/w.sum(1)[:,None]
    p0,p1=[skin(poses[s]) for s in ('before','after')];g0,g1=[transform(d['gun_local_cm'],mat(fit[s+'_gun_world'])) for s in ('before','after')]
    leftids=[j for j,n in enumerate(names) if n.startswith(('upperarm_','lowerarm_','hand_','thumb_','index_','middle_','ring_','pinky_')) and n.endswith('_l')]
    rightids=[j for j,n in enumerate(names) if n.startswith(('hand_','thumb_','index_','middle_','ring_','pinky_')) and n.endswith('_r')]
    lm=w[:,leftids].sum(1)>0;rm=w[:,rightids].sum(1)>0;shared=lm&rm;move=np.linalg.norm(p1-p0,axis=1)
    index=w[:,[names.index(n) for n in ('index_02_r','index_03_r')]].sum(1)>0
    right_protected_bones=[n for n in names if n.endswith('_r')]
    r.update(true_zero_left_influence_skin_cm=float(move[~lm].max()),
       actual_distal_index_skin_cm=float(move[index].max()),
       protected_right_world_matrix_error=float(max(np.max(abs(poses['after'][n]-poses['before'][n])) for n in right_protected_bones)),
       shared_hand_vertices=[{'vertex_id':int(i),'before_cm':p0[i].tolist(),'motion_cm':float(move[i]),
         'right_hand_weight':float(w[i,rightids].sum()),'left_arm_weight':float(w[i,leftids].sum()),
         'weights':{n:float(w[i,j]) for j,n in enumerate(names) if w[i,j]>0}} for i in np.flatnonzero(shared)])
    assert len(r['shared_hand_vertices'])==6
    assert r['true_zero_left_influence_skin_cm']<.01 and r['actual_distal_index_skin_cm']<.01
    assert r['protected_right_world_matrix_error']==0
    r['six_shared_vertices_are_not_fixed']=True
    np.savez_compressed(OUT/'diagnostic_geometry.npz',skin=p1,before_skin=p0,skin_triangles=tri,
       gun_before_cm=g0,gun_after_cm=g1,gun_triangles=d['gun_triangles'])
    # Gray/orange display only; exact full source topology and winding parity.
    origin=poses['before']['hand_r'][:3,3]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    def material(name,color):
        m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);return m
    mats=[material('Original body diagnostic',(.29,.34,.38)),material('Hands diagnostic',(.58,.47,.35)),
       material('Retained raised right thumb',(.92,.34,.10)),material('Fixed right index',(.12,.44,.85))]
    def mesh(name,points,faces,flip=False):
        md=bpy.data.meshes.new(name);md.from_pydata(((points-origin)*.01).tolist(),[],(faces[:,::-1] if flip else faces).tolist());md.update()
        o=bpy.data.objects.new(name,md);bpy.context.collection.objects.link(o);return o
    body=mesh('Full original skin diagnostic',p0,tri,True);gun=mesh('Original rifle',g0,d['gun_triangles'])
    gun.data.materials.append(material('Rifle diagnostic gray',(.22,.22,.22)))
    for m in mats:body.data.materials.append(m)
    thumb=w[:,[names.index(n) for n in ('thumb_01_r','thumb_02_r','thumb_03_r')]].sum(1)>0
    idx=w[:,[names.index(n) for n in ('index_01_r','index_02_r','index_03_r')]].sum(1)>.5
    handids=[j for j,n in enumerate(names) if n.startswith(('hand_','thumb_','index_','middle_','ring_','pinky_'))]
    hand=w[:,handids].sum(1)>.5
    for i,poly in enumerate(body.data.polygons):
        ids=tri[i];poly.material_index=2 if np.all(thumb[ids]) else 3 if np.all(idx[ids]) else 1 if np.all(hand[ids]) else 0
    scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1200;scene.render.resolution_y=850;scene.render.resolution_percentage=100
    scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
    scene.display.shading.background_type='WORLD';scene.world=bpy.data.worlds.new('DiagnosticWorld');scene.world.color=(.055,.07,.085)
    scene.view_settings.view_transform='Standard';scene.render.image_settings.file_format='PNG'
    cd=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',cd);bpy.context.collection.objects.link(cam);cd.type='ORTHO';scene.camera=cam
    thumbcenter=(poses['before']['thumb_01_r'][:3,3]+poses['before']['thumb_03_r'][:3,3])/2
    handcenter=(origin+poses['before']['hand_l'][:3,3])/2
    for stage,points,gp in (('before',p0,g0),('after',p1,g1)):
        for obj,newpoints in ((body,points),(gun,gp)):
            for v,pos in zip(obj.data.vertices,(newpoints-origin)*.01):v.co=pos
            obj.data.update()
        for name,offset,width,target in [('reverse',(0,.4,.12),.25,thumbcenter),('right',(0,-.4,.12),.25,thumbcenter),
           ('top',(0,0,.5),.3,thumbcenter),('support',(0,-.4,.1),.35,poses['before']['hand_l'][:3,3]),('context',(0,-2,.25),1.25,handcenter)]:
            center=Vector((target-origin)*.01);cam.location=center+Vector(offset);cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=width
            dest=OUT/(stage+'_'+name+'.png');scene.render.filepath=str(dest);bpy.ops.render.render(write_still=True);r['images'].append(row(dest));write(OUT/'result.json',r)
    r['status']='retained_directional_comparison_views_not_full_contact_acceptance'
except Exception:r['errors'].append(traceback.format_exc());r['status']='review_failed_preserved'
finally:
    r['guards_after']=guards();r['inputs_unchanged']=all(sha(ROOT/e['path'])==e['sha256'] for e in r['inputs']);write(OUT/'result.json',r)
    print(r['status'],r['errors']);print('Shared vertices:',r.get('shared_hand_vertices'))
