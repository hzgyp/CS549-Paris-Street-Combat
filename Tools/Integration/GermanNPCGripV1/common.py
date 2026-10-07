"""German-only current-epoch helpers; no historical guard exceptions."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
BASE=STORE/'Evidence/GermanNPCGripV1'
SNAPSHOT=STORE/'Evidence/AlliedNPCFormalV18/selected_v1/result.json'
REFERENCE=STORE/'Evidence/NPCGripBaselineV1/native_views_v3'
GLB=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/german-rifle-model-v1/Model/GermanRifle_FineWood_V15.glb'
MARKING=Path('C:/Users/hzgyp/AppData/Local/Temp/codex-clipboard-550d5a4d-3526-41a7-abf0-96f5f7124418.png')
sys.path.insert(0,str(ROOT/'Tools/Integration/AlliedNPCGripV2'))
import transform_math as tm
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def row(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'size_bytes':p.stat().st_size}
def guards():
    r=read(SNAPSHOT);assert r['status']=='formal_allied_native_selection_and_private_sftp_verified'
    assert len(r['files'])==618
    bad=[f['path'] for f in r['files'] if not (ROOT/f['path']).is_file()
        or (ROOT/f['path']).stat().st_size!=f['size_bytes'] or sha(ROOT/f['path'])!=f['sha256']]
    assert not bad,bad
    return len(r['files'])
if __name__=='__main__':print('Current approved guards exact:',guards())
