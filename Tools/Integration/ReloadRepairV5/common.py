"""Lane A read-only native guards. Not Catalog or restore authority."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
def records(include_sleeve=False):
    rows=json.loads((ROOT/'tmp/weapon-animation-reuse/preflight_v1.json').read_text())['files']
    rows+=json.loads((ROOT/'Assets/Integration/WEAPON_ANIMATION_REUSE_DRAFT_INVENTORY_20261004.json').read_text())['files']
    rows+=json.loads((ROOT/'Assets/Integration/RELOAD_APPROVED_BINDING_PROOF_INVENTORY_20261004.json').read_text())['files']
    for ident in ('blend_capability_v2','transition_proof_author_v2','owner_blend_author_v1','owner_reframe_author_v2'):
        rows+=json.loads((STORE/'Evidence/ReloadRepairV5'/ident/'result.json').read_text())['packages']
    if include_sleeve:rows+=json.loads((STORE/'Evidence/ReloadRepairV5/sleeve_native_import_v1/result.json').read_text())['packages']
    assert len({r['path'] for r in rows})==len(rows)
    return rows
def check(rows):
    return all((ROOT/r['path']).stat().st_size==r['size_bytes'] and hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256'] for r in rows)
