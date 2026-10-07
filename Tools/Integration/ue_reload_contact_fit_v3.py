"""One transient native attachment, calibrated from the existing V3 grip rule."""
import builtins
import json
from pathlib import Path
import unreal

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/ReloadContactBindingV3/contact_fit_v1'
assert not OUT.exists()
OUT.mkdir(parents=True)
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
gun,handle,context=builtins.cs549_reload_preview_gun
parent=gun.get_attach_parent()
assert parent.get_skeletal_mesh_asset().get_name()=='SK_Mannequin'
assert '/Engine/Transient.' in parent.get_path_name()
assert abs(parent.get_position())<.001
assert hasattr(builtins,'cs549_reload_contact_v3_before')
def xyz(v):return [v.x,v.y,v.z]
def tr(t):return {'t':xyz(t.translation),'q':[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w],'s':xyz(t.scale3d)}
def hollow(side):
    fingers=('middle','ring','pinky','thumb') if side=='r' else ('index','middle','ring','pinky','thumb')
    points=[parent.get_socket_location(f+'_0'+str(i)+'_'+side) for f in fingers for i in (2,3)]
    return sum(points,unreal.Vector())/len(points)
right,left=hollow('r'),hollow('l')
look=unreal.MathLibrary.find_look_at_rotation(right,left)
rotation=unreal.Rotator(pitch=0,yaw=look.yaw-90,roll=-look.pitch)
orientation=unreal.Transform(rotation=rotation)
anchor=unreal.Vector(-.5,-8,0)
position=right-unreal.MathLibrary.transform_location(orientation,anchor)
candidate=unreal.Transform(location=position,rotation=rotation,scale=unreal.Vector(1,1,1))
hand=parent.get_socket_transform('hand_r',unreal.RelativeTransformSpace.RTS_WORLD)
relative=unreal.MathLibrary.make_relative_transform(candidate,hand)
r={'status':'transient_candidate_pending_visual_review','phase_s':parent.get_position(),
   'method':'existing V3 two-grasp holding rule calibrated once in source hand_r frame; native attachment thereafter',
   'right_hollow_world_cm':xyz(right),'left_hollow_world_cm':xyz(left),'gun_local_grip_cm':xyz(anchor),
   'before_socket':str(gun.get_attach_socket_name()),'before_relative':tr(gun.get_relative_transform()),
   'candidate_world':tr(candidate),'candidate_hand_r_relative':tr(relative),'native_saved':False,'python_frame_updater':False}
assert gun.attach_to_component(parent,'hand_r',unreal.AttachmentRule.KEEP_WORLD,
    unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
gun.set_relative_transform(relative,False,True)
gun.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
builtins.cs549_reload_contact_v3_relative=relative
(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
unreal.log('CS549_RELOAD_CONTACT_V3_NATIVE_ATTACHMENT_READY '+json.dumps(r))
