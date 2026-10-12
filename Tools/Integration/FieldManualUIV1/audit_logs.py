"""Classify the actual final logs without hiding inherited handled ensures."""
from pathlib import Path
import sys,re
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/TacticalEquipmentV1'))
from prepare import OUT,read,write
logs=[]
for mode in ['pause','equipment_pause','pages','confirm','pages_small']:
    logs.append(ROOT/'tmp/g1-combat-ui-20261011/checks'/('ui_'+mode+'_field_v2')/'game.log')
for mode in ['menu','enemy_clear','p1','throw','smoke','interactions','mine_range','mine_post_clear','mine_post_clear_frag','save_equipment','restore_equipment','restore_legacy','restore_v16_equipment','performance']:
    logs.append(OUT/'checks'/(mode+'_ui_field_v2')/'game.log')
result=[]
for p in logs:
    text=p.read_text('utf-8-sig',errors='replace')
    fatal=[line for line in text.splitlines() if re.search(r'Fatal error|Assertion failed|DEVICE_HUNG|EXCEPTION_ACCESS_VIOLATION|FIELD_MANUAL_FONT.*required',line)]
    ensures=[line for line in text.splitlines() if 'Ensure condition failed:' in line]
    other_ensures=[line for line in ensures if 'GetStaticMaterials()[MaterialIndex].UVChannelData.bInitialized' not in line]
    other_errors=[line for line in text.splitlines() if ': Error:' in line and 'LogOutputDevice: Error:' not in line]
    assert not fatal and not other_ensures,(str(p),fatal,other_ensures)
    result.append(dict(path=p.relative_to(ROOT).as_posix(),inherited_mine_UV_handled_ensure_count=len(ensures),other_error_lines=other_errors,fatal_count=len(fatal),normal_exit=read(p.parent/'launch.json')['exit_code']))
write(ROOT/'tmp/g1-field-manual-ui-20261011/LOG_REVIEW.json',dict(status='classified_no_new_fatal_or_ensure',known_issue='Existing mine runtime static-mesh UV streaming-data handled ensure retained; not a zero-warning result',logs=result))
print('19 final logs: no fatal/new ensure; inherited UV handled ensures retained')
for row in result:
    if row['other_error_lines']:print(row['path'],row['other_error_lines'])
