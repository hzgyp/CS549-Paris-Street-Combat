"""Use the formal selector as the single recovery-map owner in the platform."""
import shutil
from manage import ROOT,OUT,GAME,read,write
job=read(OUT/'INDEX_REFRESH.json')
assert job['status']=='failed' and 'UNIQUE constraint' in job['error']
shutil.copyfile(OUT/'INDEX_REFRESH.json',OUT/'INDEX_REFRESH_DUPLICATE_RECOVERY_FAILED_20261011.json')
for name in ['CURRENT_UI_REVIEW','CURRENT_EQUIPMENT_INPUT_REVIEW']:
    p=ROOT/'Docs/Development'/(name+'.json');d=read(p)
    assert d['game_sha256']==GAME and d['retirement_map']=='Docs/Development/G1GameplayBaselineAdoption20261011/RECOVERY_MAP_20261011.json'
    write(OUT/(name+'_before_recovery_owner_repair.json'),d)
    d['retired_playable_recovery_map']=d.pop('retirement_map')
    d['current_baseline']='Docs/Development/CURRENT_DEVELOPMENT_BASELINE.json'
    write(p,d)
write(OUT/'RECOVERY_OWNER_REPAIR_20261011.json',dict(status='formal_selector_single_recovery_owner',reason='Platform recovery entity identity uses map path; three selectors importing the same map duplicated entity id',delegates=['CURRENT_UI_REVIEW','CURRENT_EQUIPMENT_INPUT_REVIEW'],no_game_source_or_recovery_bytes_changed=True))
print('Formal recovery owner retained; review selectors delegate without duplicate import')
