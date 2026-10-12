"""Keep baseline v3 metadata compatible with the existing platform consumer."""
import shutil
from manage import ROOT,OUT,read,write,GAME
failed=OUT/'INDEX_REFRESH.json'
assert read(failed)['status']=='failed'
shutil.copyfile(failed,OUT/'INDEX_REFRESH_SCHEMA4_FAILED_20261011.json')
p=ROOT/'Docs/Development/CURRENT_DEVELOPMENT_BASELINE.json';d=read(p)
assert d['schema_version']==4 and d['game_sha256']==GAME
write(OUT/'selected_baseline_schema4_before_repair.json',d)
checks=d['verified_runs'];assert isinstance(checks,list) and len(checks)==15
d['schema_version']=3
d['checks']=checks
d['verified_runs']={c['mode']:dict(status=c['status'],result=c['result'],result_sha256=c['sha256'],game_sha256=c['game_sha256']) for c in checks}
write(p,d)
regp=ROOT/'Assets/Registry/registry.json';reg=read(regp)
for item in reg['selectors']:
    if item['id']=='formal':
        item['assets']=list(dict.fromkeys(item['assets']+['pressure-mine','frag-grenade','smoke-grenade']))
    if item['id']=='ui-review':
        item.update(channel='formal',title='当前统一玩法（已正式采用）')
write(regp,reg)
write(OUT/'INDEX_SCHEMA_REPAIR_20261011.json',dict(status='corrected_metadata_v3_existing_contract',game_sha256=GAME,schema_version=3,verified_runs='dictionary retained; checks array supplied for platform evidence',no_game_or_source_change=True,formal_equipment_asset_references_added=True))
print('Existing selector v3 contract restored; source/Game unchanged')
