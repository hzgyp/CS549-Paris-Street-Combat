"""Freeze the selected baseline and create independent, immutable build identities."""
from pathlib import Path
import argparse, hashlib, json, os, shutil, subprocess
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'tmp/g1-tactical-equipment-20261010'
INNER = 'Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'

def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def read(p): return json.loads(p.read_text('utf-8-sig'))
def write(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes((json.dumps(obj, indent=2, ensure_ascii=False)+'\n').encode('utf-8'))
def rows(root):
    return [dict(path=p.relative_to(root).as_posix(), size_bytes=p.stat().st_size, sha256=sha(p))
            for p in sorted(root.rglob('*')) if p.is_file()]
def source_rows(project):
    return [r for directory in ['Source','Plugins','Config'] if (project/directory).exists()
            for r in rows(project/directory)
            if not r['path'].startswith(('Binaries/','Intermediate/'))]

def prepare(revision, parent_revision=None):
    target = OUT/revision
    assert not target.exists(), 'Preserve occupied candidate identity'
    selected = read(ROOT/'Docs/Development/CURRENT_DEVELOPMENT_BASELINE.json')
    assert selected['game_sha256']=='b40409b08830cc0e1d306ceab0575d7e61db382f50853426bbda58d08f385079'
    assert sha(ROOT/selected['source_manifest'])==selected['source_manifest_sha256']
    if not OUT.exists():
        parent_files = read(ROOT/selected['source_manifest'])['files']
        assert rows(ROOT/selected['source_snapshot'])==parent_files
        assert sha(ROOT/selected['playable_directory']/INNER)==selected['game_sha256']
        native = read(ROOT/'tmp/g1-enemy-clear-checkpoint-20261010/freeze.json')['protected_native']
        for r in native: assert sha(ROOT/r['path'])==r['sha256'], r['path']
        user = Path.home()/'AppData/Local/ParisStreetCombat/G1EnemyClearv320261010'
        write(OUT/'freeze.json', dict(parent=selected,parent_files=parent_files,protected_native=native,
            catalog_sha256=sha(ROOT/'Assets/Sync/CATALOG.json'), user_root=str(user),user_files=rows(user)))
    project = target/'Project'
    parent = OUT/parent_revision/'Project' if parent_revision else ROOT/selected['active_authoring_project']
    if not parent_revision: parent = parent.parent
    assert parent.is_dir()
    snapshot = ROOT/selected['source_snapshot']
    if parent_revision:
        shutil.copytree(parent, project, ignore=shutil.ignore_patterns('Content','Binaries','Intermediate','Saved','DerivedDataCache','__pycache__'))
    else: shutil.copytree(snapshot, project)
    for folder in ['Binaries','Intermediate']:
        if (parent/folder).exists(): shutil.copytree(parent/folder,project/folder)
    cmd = "New-Item -ItemType Junction -Path '"+str(project/'Content').replace("'","''")+"' -Value '"+str(ROOT/'Unreal/ParisStreetCombat/Content').replace("'","''")+"' | Out-Null"
    subprocess.run(['powershell','-NoProfile','-Command',cmd],check=True,capture_output=True)
    write(target/'prepare.json',dict(status='independent_source_prepared',revision=revision,project=str(project),parent_revision=parent_revision))
    print(json.dumps(dict(status='prepared',revision=revision,project=str(project))))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('revision');ap.add_argument('--parent');a=ap.parse_args()
    assert a.revision.startswith('candidate_') and a.revision.replace('_','').isalnum()
    prepare(a.revision,a.parent)
