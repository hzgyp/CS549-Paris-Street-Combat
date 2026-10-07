"""Actual GLB named guard/handguard membership, before first pose evaluation."""
from pathlib import Path
entry=Path(__file__).with_name('offline_fit_v2.py').read_text(encoding='utf-8-sig')
old="source=Path(__file__).with_name('offline_fit.py').read_text(encoding='utf-8-sig')"
new=old+"\nsource=source.replace(\"if 'TriggerGuard' in node['name']:part='guard'\",\"if node['name'].startswith('Guard_'):part='guard'\\n            if node['name']=='Wood_UpperHandguard':part='stock'\")"
assert entry.count(old)==1
entry=entry.replace(old,new).replace("OUT=BASE/'offline_v2'","OUT=BASE/'offline_v3'")
exec(compile(entry,str(Path(__file__)), 'exec'))
