"""Private source/binary/result verification, not Catalog or restoration authority."""
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'GripBindingV18'))
from common import ROOT,STORE,guard,config,CONFIG
BASE=STORE/'Evidence/FPUpperBodyV19'
out=BASE/'verification_v1';assert not out.exists();out.mkdir()
def rec(p):return {'path':p.relative_to(ROOT).as_posix(),'size_bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
r={'guards':guard(),'selected_formal':False,'published':False,'native_packages_authored':[],
   'source_config_sha256':hashlib.sha256(CONFIG.read_bytes()).hexdigest(),'files':[],'trials':{},'motion_stats':{}}
assert not r['guards']['mismatches'];config()
blend=STORE/'Evidence/WeaponPinkyLengthV18/distal_v1/RightPinkyDistalShorter.blend'
assert hashlib.sha256(blend.read_bytes()).hexdigest()=='7a1d0520b11e7d9c8d29377c46909cfa2b65fea39254789e28eff083de404219'
r['accepted_source']=rec(blend)
for folder in [ROOT/'Tools/Integration/FPUpperBodyV19',ROOT/'Unreal/ParisStreetCombat/Plugins/ParisGripBindingV18/Source',ROOT/'Unreal/ParisStreetCombat/Plugins/ParisGripBindingV18/Binaries/Win64']:
    r['files'] += [rec(p) for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
for p in sorted(BASE.glob('*/result.json')):
    trial=json.loads(p.read_text());r['trials'][p.parent.name]={'status':trial.get('status'),'errors':trial.get('errors',[]),'result':rec(p)}
city=json.loads((BASE/sys.argv[1]/'result.json').read_text())
r['city_identity']=sys.argv[1];r['city_status']=city['status'];r['city_errors']=city['errors']
frames=city.get('motion_frames',[])
for phase in sorted(set(f['phase'] for f in frames)):
    rows=[f for f in frames if f['phase']==phase]
    r['motion_stats'][phase]={'count':len(rows),'max_speed_cm_s':max(f['speed'] for f in rows),
       'gun_camera_min_cm':[min(f['gun_camera']['t'][i] for f in rows) for i in range(3)],
       'gun_camera_max_cm':[max(f['gun_camera']['t'][i] for f in rows) for i in range(3)],
       'max_settled_support_cm':max([f['support_cm'] for f in rows if f.get('holding_alpha',0)>=.9999] or [0])}
r['natural_end_samples']=[f for f in frames if 'natural_end_gun_step_cm' in f]
r['captures']=[rec(p) for p in (BASE/sys.argv[1]).glob('*.png')]
r['observations']=len(frames);r['final_native_updates']=frames[-1]['native_updates'] if frames else 0
r['motion_checks']=city.get('motion_checks',{})
r['early_review']=city.get('early_visual_review')
(out/'result.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({k:r[k] for k in ['guards','city_status','city_errors','observations','final_native_updates','motion_checks','natural_end_samples','motion_stats']},indent=2))
