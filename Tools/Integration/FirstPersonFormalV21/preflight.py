"""Back up only the explicitly replaced formal map/module/selection metadata."""
import shutil
from formal_common import *

OUT = BASE / 'preflight_v1'
assert not OUT.exists(), 'Preserve occupied backup identity'
guards = check_protected(); assert not guards['mismatches'], guards
assert sha(CONFIG) == CONFIG_SHA
runtime = read(STORE/'Evidence/FPUpperBodyV19/verification_v1/result.json')
assert exact(runtime['accepted_source'])
files = [ROOT/MAP, ROOT/'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject',
         ROOT/'Assets/Sync/manifests/paris-gameplay-native-playtest.json', ROOT/'Assets/Sync/CATALOG.json']
files += list((PLUGIN/'Binaries/Win64').glob('*'))
files += [PLUGIN/'ParisGripBindingV18.uplugin']
OUT.mkdir(parents=True)
backups = []
for source in files:
    if not source.is_file(): continue
    dest = OUT/'before'/source.relative_to(ROOT)
    dest.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(source, dest)
    assert sha(dest) == sha(source)
    backups.append(row(source))
write(OUT/'result.json', {'status':'verified_backup', 'guards':guards, 'files':backups,
      'accepted_source':runtime['accepted_source'], 'config_sha256':CONFIG_SHA,
      'old_guard_rows':guarded_rows(), 'old_algorithms':[row(PLUGIN/'Source/ParisGripBindingV18/Private'/name)
      for name in ('ParisGripV18Actor.cpp','ParisFPUpperBodyV19Actor.cpp')]})
print(json.dumps({'status':'verified_backup', 'files':len(backups), 'guard_count':guards['count']}))
