"""Safe socket/contact observations only; no mesh-skin bulk queries or asset save."""
import builtins
import json
from pathlib import Path
import unreal

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/ReloadContactBindingV3/contact_probe_v1'
assert not OUT.exists()
OUT.mkdir(parents=True)
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
gun, handle, context=builtins.cs549_reload_preview_gun
parent=gun.get_attach_parent()
assert parent.get_skeletal_mesh_asset().get_name()=='SK_Mannequin'
assert '/Engine/Transient.' in parent.get_path_name()
def xyz(v):return [v.x,v.y,v.z]
def tr(t):return {'t':xyz(t.translation),'q':[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w],'s':xyz(t.scale3d)}
keys=['hand_r','hand_l']+[f+'_0'+str(i)+'_r' for f in ('middle','ring','pinky','thumb','index') for i in (2,3)]
r={'phase_s':parent.get_position(),'gun_relative_before':tr(gun.get_relative_transform()),
   'gun_world_before':tr(gun.get_socket_transform('None',unreal.RelativeTransformSpace.RTS_WORLD)),
   'socket':str(gun.get_attach_socket_name()),'parent':parent.get_path_name(),
   'bones_world_before':{n:tr(parent.get_socket_transform(n,unreal.RelativeTransformSpace.RTS_WORLD)) for n in keys},
   'socket_in_right_hand':tr(unreal.MathLibrary.make_relative_transform(
       parent.get_socket_transform('hand_rSocket_Aim',unreal.RelativeTransformSpace.RTS_WORLD),
       parent.get_socket_transform('hand_r',unreal.RelativeTransformSpace.RTS_WORLD))),
   'native_saved':False}
builtins.cs549_reload_contact_v3_before=(gun.get_attach_socket_name(),gun.get_relative_transform(),parent.get_position())
parent.set_play_rate(0)
parent.set_position(0,False)
(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
unreal.log('CS549_RELOAD_CONTACT_V3_FROZEN_FOR_NATIVE_REFRESH')
