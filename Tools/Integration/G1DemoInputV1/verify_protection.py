"""Read-only selected-source, normal Game and user-file protection verification."""
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];WORK=ROOT/'tmp/g1-demo-draft03-20261009'
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--revision',default='recording_v6');p.add_argument('--receipt',required=True);args=p.parse_args()
    assert args.revision.startswith('recording_v') and args.revision[11:].isdigit()
    dest=WORK/args.receipt;assert dest.parent==WORK and not dest.exists()
    plan=json.loads((WORK/(args.revision+'_prepare.json')).read_text('utf-8-sig'));checks=[]
    for group,base,rows in [('selected_source',Path(plan['parent_source']),plan['parent_manifest']['files']),('normal_user_files',Path(plan['user_saves_root']),plan['user_saves'])]:
        for row in rows:
            f=base/row['path'];checks.append(dict(group=group,path=row['path'],exact=f.exists() and sha(f)==row['sha256']))
        if group=='normal_user_files':
            actual={x.relative_to(base).as_posix() for x in base.rglob('*') if x.is_file()} if base.exists() else set()
            assert actual=={x['path'] for x in rows},'Normal user file set changed'
    game=Path(plan['normal_playable'])/'Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'
    game_sha=sha(game);assert game_sha==plan['parent_game_sha256']
    assert all(x['exact'] for x in checks)
    result=dict(status='protected_source_user_files_game_exact',normal_game_sha256=game_sha,checks=checks,scope='Read-only protection, not gameplay/media/course acceptance')
    dest.write_text(json.dumps(result,indent=2)+'\n','utf-8');print(json.dumps(dict(status=result['status'],checked=len(checks),game_sha256=game_sha)),flush=True)
if __name__=='__main__':main()
