"""Explicit phase seek and one-shot observation; native engine evaluates the pose."""
import builtins
import json
from pathlib import Path
import unreal

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/ReloadContactBindingV3/contact_fit_v1'
gun,handle,context=builtins.cs549_reload_preview_gun
parent=gun.get_attach_parent()
assert hasattr(builtins,'cs549_reload_contact_v3_relative')
def xyz(v):return [v.x,v.y,v.z]
def tr(t):return {'t':xyz(t.translation),'q':[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w],'s':xyz(t.scale3d)}
def hollow(side):
    fingers=('middle','ring','pinky','thumb') if side=='r' else ('index','middle','ring','pinky','thumb')
    return sum((parent.get_socket_location(f+'_0'+str(i)+'_'+side) for f in fingers for i in (2,3)),unreal.Vector())/(len(fingers)*2)
def phase(seconds):
    dest=OUT/('phase_'+str(seconds).replace('.','_')+'.json')
    assert not dest.exists()
    parent.set_play_rate(0)
    parent.set_position(seconds,False)
    pending={'frames':0,'callback':None}
    def observe(delta):
        pending['frames']+=1
        if pending['frames']<3:return
        unreal.unregister_slate_post_tick_callback(pending['callback'])
        world=gun.get_socket_transform('None',unreal.RelativeTransformSpace.RTS_WORLD)
        grip=unreal.MathLibrary.transform_location(world,unreal.Vector(-.5,-8,0))
        r={'requested_seconds':seconds,'actual_seconds':parent.get_position(),
           'gun_relative':tr(gun.get_relative_transform()),'gun_world':tr(world),
           'right_hollow':xyz(hollow('r')),'left_hollow':xyz(hollow('l')),
           'right_grip_proxy_error_cm':(hollow('r')-grip).length(),
           'attachment_socket':str(gun.get_attach_socket_name()),'native_saved':False}
        dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
        unreal.log('CS549_RELOAD_CONTACT_PHASE '+json.dumps(r))
    pending['callback']=unreal.register_slate_post_tick_callback(observe)
    builtins.cs549_reload_contact_v3_pending=pending
builtins.cs549_reload_contact_v3_phase=phase
unreal.log('CS549_RELOAD_CONTACT_PHASE_HELPER_READY')
