"""Read-only approved FP epoch plus explicitly authorized later B checkpoint."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
BASE = STORE / 'Evidence/AlliedNPCGripV2'
BASELINE = STORE / 'Evidence/NPCGripBaselineV1/native_views_v3/result.json'
spec = importlib.util.spec_from_file_location('npc_guard_checkpoint',
    ROOT / 'Tools/Integration/NPCInteractionV1/common.py')
checkpoint = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checkpoint)

def guards():
    rows = checkpoint.guard_rows()
    assert len(rows) == 611, 'Reconcile a later checkpoint explicitly'
    assert checkpoint.guards_match(rows), 'Preserve changed files; never restore'
    return len(rows)

def sha(path):
    return checkpoint.digest(path)

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')

if __name__ == '__main__':
    print('Exact current combined guards:', guards())
