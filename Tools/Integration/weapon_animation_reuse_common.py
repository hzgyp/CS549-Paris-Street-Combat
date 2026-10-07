"""New animation package guards. No source asset mutation or secrets."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
JOURNAL = ROOT / 'tmp/weapon-animation-reuse'
CHECKPOINT = JOURNAL / 'preflight_v1.json'
BASE = '/Game/ParisCombat/Blueprints/WeaponAnimationReuseV1'
RELOAD = '/Game/ParisCombat/Animation/WeaponAnimationReuseV1/AS_PC_D059AimReloadV1'
SOURCE_RELOAD = '/Game/Rifle_01/Animation/In-Place/W2_Stand_Aim_Reload_IP'
SHOOT = '/Game/RifleAnimsetPro/Animations/InPlace/Rifle_ShootOnce'
PLAYER = BASE + '/BP_PCParisAnimationPlayerV1'
OWNER = BASE + '/BP_PCAnimationOwnerViewV2'


def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def guard():
    rows = read(CHECKPOINT)['files']
    for row in rows:
        p = ROOT / row['path']
        assert p.stat().st_size == row['size_bytes'] and sha(p) == row['sha256'], row['path']
    return len(rows)


def output(identity):
    assert identity.replace('_', '').isalnum()
    out = STORE / 'Evidence/WeaponAnimationReuseV1' / identity
    assert not out.exists(), 'Preserve occupied evidence identity'
    out.mkdir(parents=True)
    return out


def record(package):
    p = STORE / 'Content' / (package.removeprefix('/Game/') + '.uasset')
    return {'package': package, 'path': p.relative_to(ROOT).as_posix(),
            'size_bytes': p.stat().st_size, 'sha256': sha(p)}


def preflight():
    assert not CHECKPOINT.exists()
    rows = read(ROOT / 'tmp/german-rifle-ue-v1/preflight_v1.json')['files']
    rows += read(ROOT / 'Assets/Integration/GERMAN_RIFLE_UE_DRAFT_INVENTORY_20261004.json')['files']
    rows += read(ROOT / 'Assets/Sync/manifests/rifle-pro-mocap-ue582-selected.json')['files']
    by_path = {}
    for f in rows:
        p = ROOT / f['path']
        assert sha(p) == f['sha256'], f['path']
        by_path[f['path']] = {'path': f['path'], 'sha256': f['sha256'],
                              'size_bytes': p.stat().st_size}
    # Failed native German V1 stays protected too, even if not selected in inventory.
    for p in (STORE / 'Content/ParisCombat/Weapons/GermanRifleUEV1').rglob('*.uasset'):
        by_path[p.relative_to(ROOT).as_posix()] = {'path': p.relative_to(ROOT).as_posix(),
            'size_bytes': p.stat().st_size, 'sha256': sha(p)}
    JOURNAL.mkdir(parents=True, exist_ok=True)
    CHECKPOINT.write_text(json.dumps({'files': list(by_path.values()),
        'map_selection': False, 'catalog_selection': False}, indent=2) + '\n', encoding='utf-8')
    print('Protected files:', guard())


if __name__ == '__main__':
    preflight()
