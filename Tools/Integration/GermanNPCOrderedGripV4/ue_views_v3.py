"""Fresh immutable final clearance candidate; same verified actual-enum viewer."""
from pathlib import Path
entry=Path(__file__).with_name('ue_views_v2.py').read_text(encoding='utf-8-sig')
needle="exec(compile(entry,str(Path(__file__)),'exec'))"
extra="entry=entry.replace(\"offline_v6/result.json\",\"final_clearance_v7/result.json\")\n"+needle
# v2 reads the base viewer later, so replacement belongs immediately after its
# source read, not only in the thin v2 wrapper text.
entry=entry.replace("entry=Path(__file__).with_name('ue_views.py').read_text(encoding='utf-8-sig')",
    "entry=Path(__file__).with_name('ue_views.py').read_text(encoding='utf-8-sig').replace('offline_v6/result.json','final_clearance_v7/result.json')")
exec(compile(entry,str(Path(__file__)),'exec'))
