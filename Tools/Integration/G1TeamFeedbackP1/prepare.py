"""Freeze the exact P0 child; prepare a separate, unselected P1 source."""
from pathlib import Path
import hashlib, json, shutil, sys

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT/'tmp/g1-team-feedback-p1-20261010'
SOURCE = ROOT/'Unreal/Variants/G1TeamFeedbackP1_20261010/Project'

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()

def rows(base):
    return [dict(path=p.relative_to(base).as_posix(),size_bytes=p.stat().st_size,sha256=sha(p))
            for p in sorted(base.rglob('*')) if p.is_file()]

def main():
    assert not OUT.exists() and not SOURCE.exists(), 'Preserve occupied attempt'
    parent=json.loads((ROOT/'Docs/Development/CURRENT_INTERACTION_REVIEW.json').read_text('utf-8-sig'))
    assert parent['review_id']=='g1-team-feedback-p0-v4-20261010'
    manifest=ROOT/parent['source_manifest']; assert sha(manifest)==parent['source_manifest_sha256']
    original=ROOT/parent['source_snapshot']; files=json.loads(manifest.read_text('utf-8-sig'))['files']
    assert rows(original)==files and len(files)==45
    game=ROOT/parent['playable_directory']/'Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'
    assert sha(game)==parent['game_sha256']
    original_freeze=json.loads((ROOT/'tmp/g1-team-feedback-20261010/freeze.json').read_text())
    for r in original_freeze['protected_native']:assert sha(ROOT/r['path'])==r['sha256'],r['path']
    user=Path.home()/'AppData/Local/ParisStreetCombat/G1Interaction20261010'
    OUT.mkdir(parents=True);shutil.copytree(original,SOURCE)
    record=dict(parent=parent,parent_files=files,p0_game=str(game),p0_game_sha256=sha(game),
                p0_user_root=str(user),p0_user_files=rows(user),selected_parent_freeze=original_freeze)
    (OUT/'freeze.json').write_text(json.dumps(record,indent=2)+'\n','utf-8')
    print(json.dumps(dict(status='p0_frozen',files=45,native_guards=len(original_freeze['protected_native']))))

if __name__=='__main__': main()
