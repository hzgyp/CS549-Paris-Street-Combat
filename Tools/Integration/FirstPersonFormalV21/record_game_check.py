"""Verify saved ordinary native entry, not lifecycle/FPS/package acceptance."""
from formal_common import *
LOG = ROOT/'tmp/first-person-formal-v21/ordinary_game_v1.log'
OUT = BASE/'ordinary_game_v1'
assert not OUT.exists()
text = LOG.read_text(encoding='utf-8-sig',errors='replace')
assert '-game -DisablePlugins=ParisEditorBridge,PythonScriptPlugin' in text
assert 'Paris approved first-person native binding ready; original gameplay retained' in text
assert 'Paris approved first-person setup stopped' not in text
assert 'LogExit: Exiting.' in text and 'Fatal error:' not in text
guards=check_protected(True);assert not guards['mismatches'],guards
author=read(BASE/'author_v1/result.json');assert all(exact(f) for f in author['saved_files'])
write(OUT/'result.json',{'status':'passed_ordinary_saved_game_native_auto_bind',
    'python_plugin_disabled':True,'editor_bridge_disabled':True,'script_injection':False,
    'native_self_exit_seconds_flag':45,'map_config_saved_hashes_verified':True,
    'native_ready_log_observed':True,'guards':guards,'log_sha256':sha(LOG),
    'shipping_build':False,'fps_acceptance':False,'lifecycle_acceptance':False})
print(json.dumps({'status':'passed_ordinary_saved_game_native_auto_bind','guard_count':guards['count']}))
