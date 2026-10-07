"""View retained failed goal only; never rerun fit or author a native candidate."""
import hashlib,json,sys
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/WeaponTriggerPivotV12'))
from pivot_common import load,evaluate,STORE
BASE=STORE/'Evidence/LeftSupportV20'
OUT=BASE/'stopped_goal_views_v1';assert not OUT.exists();OUT.mkdir()
goal=json.loads((BASE/'pivot_goal_v1/result.json').read_text())
assert goal['status']=='stopped_intact_target_contact_gate' and not goal['early_gate_passed']
source=STORE/'Evidence/WeaponPinkyLengthV18/distal_v1'
proof=json.loads((source/'result.json').read_text())
d=load();gun0=np.array(proof['baseline_gun_component_matrix'])
bones={n:np.array(v) for n,v in goal['candidate_component_bones'].items()}
after=evaluate(d,bones,gun0)
bpy.ops.wm.open_mainfile(filepath=str(source/'RightPinkyDistalShorter.blend'),load_ui=False,use_scripts=False)
arms=bpy.data.objects['Frozen V16 continuous arms'];right=bpy.data.objects['Fixed right raised_v16 original-textured'];left=bpy.data.objects['Support raised_v16 original-textured']
for obj in (arms,right,left):
    for v,p in zip(obj.data.vertices,after*.01):v.co=p
    obj.data.update()
center=Vector(json.loads((BASE/'audit_v1/result.json').read_text())['diagnostic_center_m'])
scene=bpy.context.scene;scene.render.resolution_x=1000;scene.render.resolution_y=800
arms.hide_render=True;right.hide_render=False;left.hide_render=False
views=[]
for name,offset in [('side',(.5,0,.05)),('reverse',(-.5,0,.05)),('top',(0,0,.5))]:
    cd=bpy.data.cameras.new(name);cd.type='ORTHO';cd.ortho_scale=.28;cd.clip_start=.001
    cam=bpy.data.objects.new(name,cd);scene.collection.objects.link(cam)
    cam.location=center+Vector(offset);cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.camera=cam;scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True);views.append(name+'.png')
(OUT/'result.json').write_text(json.dumps({'status':'failed_goal_diagnostic_views_only','renders':views,'native_authored':False,'source_unchanged':hashlib.sha256((source/'RightPinkyDistalShorter.blend').read_bytes()).hexdigest()==proof['blend_sha256']},indent=2)+'\n')
