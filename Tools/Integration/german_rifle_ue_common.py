"""Exact accepted-input guards for the bounded UE integration; no secret access."""
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
BASE = '/Game/ParisCombat/Weapons/GermanRifleUEV1'
JOURNAL = ROOT / 'tmp/german-rifle-ue-v1'
GUARDS = JOURNAL / 'preflight_v1.json'
GLB = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/german-rifle-model-v1/Model/GermanRifle_FineWood_V15.glb'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def guard():
    rows = read(GUARDS)['files']
    for row in rows:
        p = ROOT / row['path']
        assert p.stat().st_size == row['size_bytes'] and sha(p) == row['sha256'], row['path']
    return len(rows)


def new_output(identity):
    assert identity.replace('_', '').isalnum()
    out = STORE / 'Evidence/GermanRifleUEV1' / identity
    assert not out.exists(), 'Preserve occupied evidence identity'
    out.mkdir(parents=True)
    return out


def preflight():
    assert not GUARDS.exists(), 'Do not overwrite a protection checkpoint'
    selected = read(ROOT / 'Assets/Sync/manifests/paris-gameplay-native-playtest.json')
    native = read(ROOT / 'Assets/Integration/CITY_CONTINUOUS_ARMS_NATIVE_INVENTORY_20261003.json')
    actions = read(ROOT / 'Assets/Integration/PLAYER_ACTIONS_DRAFT_INVENTORY_20261003.json')
    model = read(ROOT / 'Assets/Sync/manifests/german-rifle-model.json')
    author = read(ROOT / actions['source_evidence']['author']['path'])
    rows = selected['files'] + native['files'] + actions['files'] + model['files'] + author['source_guards']
    by_path = {}
    for row in rows:
        p = ROOT / row['path']
        assert sha(p) == row['sha256'], row['path']
        item = {'path': row['path'], 'sha256': row['sha256'],
                'size_bytes': row.get('size_bytes', p.stat().st_size)}
        assert item['path'] not in by_path or by_path[item['path']] == item, item['path']
        by_path[item['path']] = item
    for p in (STORE / 'Content/WW2City/Maps').glob('*.umap'):
        by_path[p.relative_to(ROOT).as_posix()] = {'path': p.relative_to(ROOT).as_posix(), 'size_bytes': p.stat().st_size, 'sha256': sha(p)}
    for p in [ROOT / 'Assets/Sync/CATALOG.json', ROOT / 'Unreal/ParisStreetCombat/Config/DefaultInput.ini']:
        by_path[p.relative_to(ROOT).as_posix()] = {'path': p.relative_to(ROOT).as_posix(), 'size_bytes': p.stat().st_size, 'sha256': sha(p)}
    b = GLB.read_bytes()
    size = struct.unpack_from('<I', b, 12)[0]
    gltf = json.loads(b[20:20 + size])
    assert len(gltf['meshes']) == 24 and len(gltf['images']) == 36
    muzzle = next(n for n in gltf['nodes'] if n.get('name') == 'Muzzle_Donor_Insert')
    a = gltf['accessors'][gltf['meshes'][muzzle['mesh']]['primitives'][0]['attributes']['POSITION']]
    tip = a['max'][0] + muzzle.get('translation', [0, 0, 0])[0]
    # glTF (X,Y,Z) -> UE (X,-Z,Y), then UE yaw +90. Muzzle center -> +Y83.23.
    offset = [muzzle['translation'][2] * -100, 83.23 - tip * 100, -muzzle['translation'][1] * 100]
    # Assembly/source wrist station x=-.068,z=-.03m, not borrowed M1 grip coords.
    anchor = [0.0, 83.23 - (a['max'][0] + .068) * 100, -3.0]
    payload = {'status': 'exact_inputs_guarded', 'files': list(by_path.values()),
               'model_version': model['asset_version'], 'native_import_yaw_deg': 90,
               'native_import_offset_cm': offset, 'grip_anchor_cm': anchor,
               'muzzle_cm': [0, 83.23, 0], 'original_tip_x_m': a['max'][0],
               'triangles': 24466, 'length_cm': 110.7303977,
               'owner': 'yg745', 'catalog_selection_changed': False}
    JOURNAL.mkdir(parents=True, exist_ok=True)
    GUARDS.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
    print('Protected files:', guard(), 'native offset:', offset, 'grip:', anchor)


if __name__ == '__main__':
    preflight()
