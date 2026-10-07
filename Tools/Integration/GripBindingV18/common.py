"""Current guards/config and new-namespace inventories; not restore authority."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
BASE=STORE/'Evidence/GripBindingV18'
CONFIG=BASE/'config_v1/binding.json'
def guard():
    rows=json.loads((STORE/'Evidence/ReloadIndexContactV6/map_recovery_v1/result.json').read_text())['files']
    bad=[r['path'] for r in rows if not (ROOT/r['path']).is_file() or (ROOT/r['path']).stat().st_size!=r['size_bytes'] or hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()!=r['sha256']]
    return {'count':len(rows),'mismatches':bad,'known_V6_rate_difference_retained':True}
def config():
    proof=json.loads((BASE/'config_v1/result.json').read_text())
    assert not proof['errors'] and proof['inputs_unchanged']
    assert hashlib.sha256(CONFIG.read_bytes()).hexdigest()==proof['config_sha256']
    return json.loads(CONFIG.read_text())
def inventory(package):
    p=STORE/('Content/'+package.removeprefix('/Game/')+'.uasset')
    return {'package':package,'path':p.relative_to(ROOT).as_posix(),'size_bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
