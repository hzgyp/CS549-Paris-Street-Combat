"""Freeze exact German V11, current epoch and one-map recovery before authoring."""
import math,shutil
from common import *
assert not (BASE/'preflight').exists(),'Preserve occupied checkpoint'
epoch=read(STORE/'Evidence/AlliedNPCFormalV18/selected_v1/result.json')
assert epoch['status']=='formal_allied_native_selection_and_private_sftp_verified'
assert len(epoch['files'])==618 and all(exact(r) for r in epoch['files'])
source=STORE/'Evidence/GermanNPCLowerGripV11/source_frame_v4/result.json'
v11=read(source)
original=read(STORE/'Evidence/GermanNPCOrderedGripV4/offline_v6/result.json')['before_bones']
accepted=v11['after_bones'];parents=v11['parents']
names=[n for n in v11['bone_names'] if n.startswith(('clavicle_','upperarm_','lowerarm_','hand_','index_','middle_','ring_','pinky_','thumb_'))]
assert len(names)==42
rules=[]
for n in names:
    a=tm.local_q(original[parents[n]],original[n]);b=tm.local_q(accepted[parents[n]],accepted[n])
    rules.append({'bone':n,'source_q':a,'accepted_q':b,'delta':tm.qmul(b,tm.qinv(a)),
                  'angle_degrees':tm.angle(a,b)})
hand=accepted['hand_r'];gun=v11['after_gun_world']
relative={'t':tm.inverse_point(hand,gun['t']),'q':tm.local_q(hand,gun),
          's':[gun['s'][i]/hand['s'][i] for i in range(3)]}
assert math.dist(tm.point(hand,relative['t']),gun['t'])<1e-8
audit=read(STORE/'Evidence/WeaponAnimationReuseV1/audit_v1/result.json')['models']['german']
cfg={'schema':1,'source_mesh':audit['path']+'.'+audit['path'].rsplit('/',1)[1],
     'expected_team_id':1,'accepted_holding':True,'release_seconds':.15,
     'rules':rules,'gun_hand_relative':relative,'source_record_sha256':sha(source),
     'origin':'German V11 own accepted visual baseline; NOT retired V12/V13 or Allied/FP parameters',
     'known_visual_limits':'Straight index, small stock overlap/self-contact remain deferred for MVP'}
baseline_paths=[source,STORE/'Evidence/GermanNPCLowerGripV11/frame_failure_views_v1/diagnostic_geometry.npz',
    ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/german-rifle-model-v1/Model/GermanRifle_FineWood_V15.glb']
for folder in ('GermanRifleUEV1/import_v3','GermanRifleUEV1/author_v2'):
    r=read(STORE/'Evidence'/folder/'result.json');assert not r['errors']
    assert all(exact(f) for f in r['native_files']),'Preserve original verified gun packages'
    baseline_paths.extend(ROOT/f['path'] for f in r['native_files'])
baseline=[row(p) for p in dict.fromkeys(baseline_paths)]
binary=[row(PLUGIN/'Binaries/Win64'/n) for n in ('UnrealEditor-ParisNPCGripV15.dll','UnrealEditor-ParisNPCGripV15Editor.dll','UnrealEditor.modules')]
out=BASE/'preflight';out.mkdir(parents=True)
shutil.copy2(MAP,out/'map_before.umap');assert sha(MAP)==sha(out/'map_before.umap')
shutil.copytree(PLUGIN/'Binaries',out/'BinariesBefore')
assert all(sha(out/'BinariesBefore/Win64'/Path(r['path']).name)==r['sha256'] for r in binary)
write(CONFIG,cfg)
write(out/'result.json',{'guards':epoch['files'],'descriptor':row(DESCRIPTOR),'baseline_files':baseline,
    'binary_files':binary,'config_sha256':sha(CONFIG),'rules':len(rules),
    'old_epoch':'AlliedNPCFormalV18 selected_v1 (618)','source_record':row(source),
    'accepted_visual_limits_not_relabelled':True,'user_authorization':'Formal German V11 with gun for MVP,6 October2026'})
print(json.dumps({'exact_rows':618,'German_own_ready_rules':len(rules),'source_mesh':cfg['source_mesh'],'gun_hand':relative}))
