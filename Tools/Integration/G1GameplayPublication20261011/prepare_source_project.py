"""Prepare a new source76 wrapper from a verified extracted private package."""
import argparse,hashlib,json,os,shutil,stat,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def read(p):return json.loads(p.read_text('utf-8-sig'))
def verify(p,r):
    assert p.is_file() and p.stat().st_size==r['size_bytes'],str(p)
    with p.open('rb') as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==r['sha256'],str(p)
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--packaged-root',required=True);ap.add_argument('--target',default='tmp/Team-G1-Gameplay20261011/Project');a=ap.parse_args()
    baseline=read(ROOT/'Docs/Development/CURRENT_DEVELOPMENT_BASELINE.json')
    assert baseline['active_source_files']==76
    manifest=ROOT/baseline['source_manifest']
    with manifest.open('rb') as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==baseline['source_manifest_sha256']
    target=Path(os.path.abspath(ROOT/a.target));assert target.is_relative_to(ROOT/'tmp') and not target.exists(),'Use a new tmp target; preserve existing work'
    for p in target.parents:
        if p==ROOT:break
        if p.exists():assert not p.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT
    content=ROOT/'Unreal/ParisStreetCombat/Content';assert content.is_dir(),'First restore selected city/native Content using TEAM_PLAYTEST_ZH'
    source=ROOT/baseline['source_snapshot'];rows=read(manifest)['files']
    assert len(rows)==76
    for r in rows:verify(source/r['path'],r)
    pkg=Path(a.packaged_root)
    archive=read(ROOT/baseline['sftp_manifest'])
    for r in archive['archive_members']:verify(pkg/r['path'],r)
    target.mkdir(parents=True)
    for r in rows:
        dst=target/r['path'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source/r['path'],dst);verify(dst,r)
    prefix='Windows/WW2FranceLiberation/'
    for r in archive['archive_members']:
        if r['path'].startswith(tuple(prefix+x+'/' for x in ['Audio','Equipment','UI'])):
            dst=target/r['path'][len(prefix):];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(pkg/r['path'],dst);verify(dst,r)
    command="New-Item -ItemType Junction -Path '"+str(target/'Content').replace("'","''")+"' -Value '"+str(content).replace("'","''")+"' | Out-Null"
    subprocess.run(['powershell','-NoProfile','-Command',command],check=True,capture_output=True)
    print(target/'WW2FranceLiberation.uproject')
    print('Exact76 and runtime resources prepared. Build a matching UE5.8.2 Editor before entry; no old DLL copied.')
if __name__=='__main__':main()
