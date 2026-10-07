"""One disposable-render backface parity correction; source asset unchanged."""
import hashlib
import json
import sys
import traceback
from pathlib import Path
import bpy
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'WeaponTriggerAlignmentV2'))
from blender_contact_common import ROOT,STORE,load,mat,skin,transform
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'WeaponTriggerPivotV12'))
from pivot_common import guarded_files

BASE=STORE/'Evidence/FirstPersonV18Acceptance'
OUT=BASE/'projection_v2'
assert not OUT.exists()
OUT.mkdir()
original=json.loads((BASE/'projection_v1/result.json').read_text())
assert not original['errors'] and original['inputs_unchanged']
r={'scope':__doc__,'errors':[],'native_authored':False,'formal_selection':False,'deleted_files':[]}
try:
    d=load()
    bones={n:mat(t) for n,t in d['poses']['0.0']['bones_component'].items()}
    v18=json.loads((STORE/'Evidence/WeaponPinkyLengthV18/distal_v1/result.json').read_text())
    gun0=np.array(v18['baseline_gun_component_matrix'])
    control_arm=transform(skin(d['p'],d['weights'],{n:bones[n]@d['invref'][n] for n in d['invref'] if n in bones}),np.linalg.inv(gun0))*.01
    control_gun=transform(d['gp'],np.linalg.inv(gun0)@bones['hand_r']@d['relative'])*.01
    bpy.ops.wm.open_mainfile(filepath=str(BASE/'projection_v1/CompleteArmsProjectionOnly.blend'),load_ui=False,use_scripts=False)
    arms,gun=bpy.data.objects['Frozen V16 continuous arms'],bpy.data.objects['Frozen V16 M1']
    current_arm=np.array([tuple(v.co) for v in arms.data.vertices])
    current_gun=np.array([tuple(v.co) for v in gun.data.vertices])
    r['material_copies']=[]
    for obj in (arms,gun):
        for index,old in enumerate(list(obj.data.materials)):
            new=old.copy()
            new.use_backface_culling=True
            obj.data.materials[index]=new
            r['material_copies'].append({'from':old.name,'to':new.name,'use_backface_culling':new.use_backface_culling})
    scene=bpy.context.scene
    for label,a,g in [('source_control',control_arm,control_gun),('accepted_V18',current_arm,current_gun)]:
        for obj,points in ((arms,a),(gun,g)):
            for vertex,p in zip(obj.data.vertices,points):vertex.co=p
            obj.data.update()
        scene.render.filepath=str(OUT/(label+'_first_person.png'))
        bpy.ops.render.render(write_still=True)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'CompleteArmsProjectionOnly.blend'))
    r['native_frame_control']=original['native_frame_control']
    r['status']='corrected_projection_requires_control_and_candidate_visual_review'
except Exception:
    r['status']='stopped_viewer_error'
    r['errors'].append(traceback.format_exc())
finally:
    r['source_inputs_unchanged']=all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in original['input_hashes'].items())
    r['guards']=guarded_files()
    (OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(r),flush=True)
    if r['errors'] or not r['source_inputs_unchanged'] or r['guards']['mismatches']:raise SystemExit(1)
