"""Authorize only the measured existing hold source; private selection, not release."""
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'GripBindingV18'))
from common import ROOT,STORE,guard,inventory,config
BASE=STORE/'Evidence/FPUpperBodyV19'
probe=json.loads((BASE/'holding_probe_v2/result.json').read_text())
stats=json.loads((BASE/'source_analysis_holding_probe_v2/result.json').read_text())
name='W2_Stand_Aim_Idle_IP';clip='/Game/Rifle_01/Animation/In-Place/'+name
s=stats['clip_statistics'][name]['component']['hand_r']
assert not probe['errors'] and probe['source_inputs_unchanged']
assert max(s['span_cm'])<1 and s['max_pair_rotation_degrees']<5
assert not guard()['mismatches'];config()
target=BASE/'holding_selection_v1';assert not target.exists();target.mkdir()
record={'clip_path':clip,'compatible_existing_clip':True,'scope':'native socket motion only; actual target visual acceptance pending',
        'source_inventory':inventory(clip),'right_hand_component_statistics':s,
        'source_proof':'holding_probe_v2','mesh_source_unchanged':True,'selected_formal':False}
(target/'selection.json').write_text(json.dumps(record,indent=2)+'\n')
# Preserve previous native binary/source proof before installing a new module.
backup=target/'prior_plugin';backup.mkdir()
plugin=ROOT/'Unreal/ParisStreetCombat/Plugins/ParisGripBindingV18'
saved=[]
for p in (plugin/'Binaries/Win64').glob('*'):
    if p.is_file():
        (backup/p.name).write_bytes(p.read_bytes());saved.append({'file':p.name,'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(target/'prior_binary_inventory.json').write_text(json.dumps(saved,indent=2)+'\n')
print('Existing holding source selected for isolated proof; prior native binary retained.')
