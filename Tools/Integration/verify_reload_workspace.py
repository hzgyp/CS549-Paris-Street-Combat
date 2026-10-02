"""Authenticated read/CRUD of only new reload workspace and temporary probes."""
import hashlib
import json
import os
import subprocess
import uuid
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SHARE=ROOT/'Assets/LocalShared/SFTP'
STORE=SHARE/'workspaces/yg745/paris-gameplay-v1'
OUT=ROOT/'tmp/paris-reload-draft-20261002-v1'
fresh=json.loads((STORE/'Evidence/P4/SimplifiedReload20261002/fresh_v2.json').read_text())
assert fresh['status']=='pass_fresh_bounded_reload_only'
commands=[]
for n,e in enumerate(fresh['assets']):
    p=ROOT/e['path'];dest=OUT/f'workspace-{n}.dat'
    commands.append(f'get "/{p.relative_to(SHARE).as_posix()}" "{dest.as_posix()}"')
first=OUT/'workspace-crud-first.txt';second=OUT/'workspace-crud-second.txt';download=OUT/'workspace-crud-download.txt'
first.write_bytes(b'Reload CRUD initial\n');second.write_bytes(b'Reload CRUD changed\n')
remote='/workspaces/yg745/paris-gameplay-v1/Content/ParisCombat/Blueprints/Characters/SimplifiedReloadDraft/_probe_'+uuid.uuid4().hex
commands += [f'mkdir "{remote}"',f'put "{first.as_posix()}" "{remote}/probe.txt"',f'put "{second.as_posix()}" "{remote}/probe.txt"',f'rename "{remote}/probe.txt" "{remote}/renamed.txt"',f'get "{remote}/renamed.txt" "{download.as_posix()}"',f'rm "{remote}/renamed.txt"',f'rmdir "{remote}"']
profile=Path(os.environ['USERPROFILE'])
process=subprocess.run(['sftp','-b','-','-i',str(profile/'.ssh/cs549_sftp_ed25519'),'-o','UserKnownHostsFile='+str(profile/'.ssh/known_hosts_cs549'),'-o','StrictHostKeyChecking=yes','-o','IdentitiesOnly=yes','-P','22222','cs549sftp@127.0.0.1'],input='\n'.join(commands)+'\n',capture_output=True,text=True)
(OUT/'workspace-sftp.log').write_text(process.stdout+'\n'+process.stderr,encoding='utf-8')
assert process.returncode==0, 'Read private task log; exact probe targets only'
for n,e in enumerate(fresh['assets']):
    p=OUT/f'workspace-{n}.dat'
    assert p.stat().st_size==e['size_bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==e['sha256']
assert download.read_bytes()==second.read_bytes()
(OUT/'workspace-verification.json').write_text(json.dumps({'status':'complete','new_blueprint_downloads_verified':3,'CRUD':'create/change/rename/read/delete passed; only exact UUID temporary probes removed','external_routing_or_teammates':'not retested'},indent=2)+'\n',encoding='utf-8')
print('All three new Blueprint workspace files downloaded and SHA-256 verified; shared CRUD passed')
