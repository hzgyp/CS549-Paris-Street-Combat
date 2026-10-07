"""Confirm an authorized map alias difference; preserve original author receipt."""
from formal_common import *
OUT=BASE/'author_guard_verification_v2'
assert not OUT.exists()
author=read(BASE/'author_v1/result.json')
assert author['status']=='saved_selected_requires_fresh_reopen' and author['map_saved']
changed=[f['path'] for f in guarded_rows() if not exact(f)]
assert changed and {(ROOT/p).resolve() for p in changed}=={(ROOT/MAP).resolve()},changed
assert all(exact(f) for f in author['saved_files'])
guards=check_protected(True);assert not guards['mismatches']
write(OUT/'result.json',{'status':'passed_authorized_exact_map_alias_only',
    'changed_old_guard_paths':changed,'same_resolved_map':True,'changed_physical_files':1,
    'other_guard_row_count':len(guarded_rows())-len(changed),
    'other_guard_bytes_exact':True,'author_map_config_hashes_exact':True,
    'old_author_receipt_preserved':True,'new_native_save':False,'guards':guards})
print(json.dumps({'status':'passed_authorized_exact_map_alias_only','other_guard_row_count':len(guarded_rows())-len(changed),'changed_physical_files':1}))
