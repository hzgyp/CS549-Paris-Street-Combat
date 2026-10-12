"""Freeze the selected parent, native assets and normal user files; create a child."""
from pathlib import Path
import hashlib, json, shutil

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'tmp/g1-team-feedback-20261010'
SOURCE = ROOT / 'Unreal/Variants/G1TeamFeedback20261010/Project'

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''): h.update(b)
    return h.hexdigest()

def rows(base):
    return [dict(path=p.relative_to(base).as_posix(), size_bytes=p.stat().st_size, sha256=sha(p))
            for p in sorted(base.rglob('*')) if p.is_file()]

def main():
    assert not OUT.exists() and not SOURCE.exists(), 'Preserve occupied attempt'
    parent = json.loads((ROOT/'Docs/Development/CURRENT_DEVELOPMENT_BASELINE.json').read_text('utf-8-sig'))
    assert parent['baseline_id']=='g1-foot-contact-audio-v2-20261009'
    manifest_path = ROOT/parent['source_manifest']
    assert sha(manifest_path)==parent['source_manifest_sha256']
    original = ROOT/parent['source_snapshot']
    manifest = json.loads(manifest_path.read_text('utf-8-sig'))
    assert len(manifest['files'])==42
    for r in manifest['files']:
        assert (original/r['path']).stat().st_size==r['size_bytes'] and sha(original/r['path'])==r['sha256']
    normal = ROOT/parent['playable_directory']
    game = normal/'Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'
    assert sha(game)==parent['game_sha256']
    catalog_path=ROOT/'Assets/Sync/CATALOG.json'
    catalog=json.loads(catalog_path.read_text('utf-8-sig'))
    ids={'rifle-animset-pro-original','us-paratrooper-original','german-soldier-original',
         'character-ue582-integration-baseline','rifle-pro-mocap-ue582-selected',
         'paris-gameplay-native-playtest','german-rifle-model','paris-g1-recorded-audio'}
    guards=[]
    for entry in catalog['active_manifests']:
        if entry['asset_id'] not in ids: continue
        path=ROOT/entry['path']; assert sha(path)==entry['sha256']
        for r in json.loads(path.read_text('utf-8-sig'))['files']:
            p=ROOT/r['path']; assert p.stat().st_size==r['size_bytes'] and sha(p)==r['sha256'],r['path']
            guards.append(dict(path=r['path'],size_bytes=r['size_bytes'],sha256=r['sha256']))
    user = Path.home()/'AppData/Local/ParisStreetCombat/G1PlaytestFoleyV220261009'
    user_rows=rows(user) if user.exists() else []
    OUT.mkdir(parents=True)
    shutil.copytree(original,SOURCE)
    result=dict(status='parent_frozen_child_unmodified',parent=parent,parent_files=manifest['files'],
                catalog_sha256=sha(catalog_path),protected_native=guards,normal_game=str(game),
                normal_game_sha256=sha(game),user_root=str(user),user_files=user_rows,
                source=str(SOURCE),normal_playable=str(normal))
    (OUT/'freeze.json').write_text(json.dumps(result,indent=2)+'\n','utf-8')
    print(json.dumps(dict(status=result['status'],parent_files=42,native_guards=len(guards),normal_user_files=len(user_rows))))

if __name__=='__main__': main()
