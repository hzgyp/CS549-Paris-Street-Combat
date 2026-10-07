"""Unsaved V11/V12 extra existing fingertip curl; gun/all other bones unchanged."""
from pathlib import Path
wrapper_source=Path(__file__).with_name('ue_index_curl_v11e_views.py')
source=wrapper_source.read_text(encoding='utf-8')
for old,new in (
    ('Unsaved requested rearward/index-tip comparison; blade contact remains failed.',__doc__),
    ('CS549_ALLIED_INDEX_CURL_V11_ID','CS549_ALLIED_TIP_CURL_V12_ID'),
    ('index_curl_v11e/result.json','tip_curl_v12/result.json'),
    ('trigger_fit_native_v10/result.json','index_curl_native_v11/result.json'),
    ('index_curl_v11_native_comparison_contact_failed','tip_curl_v12_native_comparison_requires_review'),
    ('PC_AlliedIndexCurlV11','PC_AlliedTipCurlV12'),
    ("':index_curl_v11_comparison'","':tip_curl_v12_comparison'"),
    ("assert trial['comparison_only'] and not trial['contact_gate_passed']","assert trial['comparison_only'] and trial['comparison_gate_passed']"),
    ("entry.with_name('ue_trigger_fit_v10_views.py'))","entry.with_name('ue_trigger_fit_v10_views.py'),wrapper_source)")):
    assert source.count(old)>=1,old
    source=source.replace(old,new)
exec(compile(source,str(wrapper_source)+':v12','exec'),globals())
