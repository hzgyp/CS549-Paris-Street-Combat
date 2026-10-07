"""Formal selection helpers. Old failure snapshots are immutable, not updated in place."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
BASE = STORE / 'Evidence/FirstPersonFormalV21'
ENTRY = '/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1'
MAP = 'Unreal/ParisStreetCombat/Content/ParisCombat/Maps/LV_ParisStreetCombat_V1.umap'
CONFIG = STORE / 'Evidence/LeftSupportV20/reuse_pose_v2/binding.json'
CONFIG_SHA = '04f4588cc6922a907f3aaa2bc60d41dec985240e96d3c6c31f1d32dfde3bc7a7'
PACKAGE = '/Game/ParisCombat/FirstPerson/ApprovedV20/DA_PC_FirstPersonGripV20'
PLUGIN = ROOT / 'Unreal/ParisStreetCombat/Plugins/ParisGripBindingV18'
LABEL = 'PC_FirstPersonApprovedV20'


def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')
def sha(path):
    with path.open('rb') as stream: return hashlib.file_digest(stream, 'sha256').hexdigest()
def row(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path), 'size_bytes': path.stat().st_size}
def exact(item):
    path = ROOT / item['path']
    return path.is_file() and path.stat().st_size == item['size_bytes'] and sha(path) == item['sha256']
def guarded_rows():
    # Import by file to avoid this module's identical name shadowing Lane B common.
    import importlib.util
    spec = importlib.util.spec_from_file_location('lane_b_guards', ROOT / 'Tools/Integration/NPCInteractionV1/common.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module.guard_rows()


def check_protected(allow_map=False):
    rows = guarded_rows()
    # Old snapshots use the physical SFTP path; formal references use its Content
    # junction alias. Exempt only this exact resolved map, never a directory.
    map_actual = (ROOT/MAP).resolve()
    mismatches = [f['path'] for f in rows if not exact(f)
        and not (allow_map and (ROOT/f['path']).resolve() == map_actual)]
    return {'count': len(rows), 'mismatches': mismatches, 'authorized_map_exception': allow_map}
