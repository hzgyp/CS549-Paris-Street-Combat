"""Fresh-read full skin/gun for the one extra tip rotation comparison."""
from pathlib import Path
entry=Path(__file__).with_name('verify_trigger_fit_v10_offline.py')
source=entry.read_text(encoding='utf-8')
for old,new in (
    ("out=BASE/'trigger_pad_v10d'","out=BASE/'tip_curl_v12'"),
    ("assert r['contact_gate_passed'] and not r['errors'] and r['inputs_unchanged']","assert r['comparison_gate_passed'] and not r['errors'] and r['inputs_unchanged']"),
    ("r['selected_surface_record']['actual_index_skin_vertices']","r['pad_skin_vertices']"),
    ("'local_index_gate':True","'local_index_gate':r['contact_gate_passed'],'comparison_only':True")):
    assert source.count(old)==1,old
    source=source.replace(old,new)
exec(compile(source,str(entry)+':v12_fresh','exec'),globals())
