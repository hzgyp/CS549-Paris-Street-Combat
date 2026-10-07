"""Offline cause-first review of immutable construction/evidence. No Unreal launch."""
import argparse
import hashlib
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
parser = argparse.ArgumentParser()
parser.add_argument('--identity', required=True)
args = parser.parse_args()
assert re.fullmatch(r'[a-zA-Z0-9_]+', args.identity)
out = STORE / 'Evidence/ReloadRepairV5' / args.identity
assert not out.exists(), 'Preserve occupied evidence identity'
out.mkdir(parents=True)
(out / 'source.py').write_bytes(Path(__file__).read_bytes())

paths = {
    'owner_constructor': STORE / 'Evidence/PlayerActionsV1/owner_author_v2/source.py',
    'proof_constructor': STORE / 'Evidence/ReloadContactBindingV3/binding_proof_author_v2/source.py',
    'framing_constructor': STORE / 'Evidence/ContinuousArmsNativeV1/author_v3/source.py',
    'frozen_views': STORE / 'Evidence/ReloadContactBindingV3/binding_proof_views_v2/result.json',
}
inputs = {name: {'path': path.relative_to(ROOT).as_posix(),
                  'size_bytes': path.stat().st_size,
                  'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
          for name, path in paths.items()}
owner = paths['owner_constructor'].read_text()
proof = paths['proof_constructor'].read_text()
framing = paths['framing_constructor'].read_text()
views = json.loads(paths['frozen_views'].read_text())
assert not views['errors']

def line(source, token):
    matches = [{'line': i + 1, 'text': text} for i, text in enumerate(source.splitlines()) if token in text]
    assert matches, token
    return matches

held = [row for row in line(owner, 'PlayAnimation') if "held=run" in row['text']]
assert len(held) == 1 and 'Rifle_Idle' in held[0]['text']
evidence = {
    'ready_condition': line(owner, "B='Ready'"),
    'holding_immediate_play': held,
    'proof_retains_holding_play_inserts_leader_only': line(proof, 'insert_after(g,holding[0]'),
    'framing_ready_branch': line(framing, "A=ready,B=math"),
    'held_recalculates_framing': line(framing, "held=put(g,held,'FramingT'"),
    'reload_preserves_framing': line(framing, "reload=put(g,reload,'ViewT'"),
}
finish = next(s for s in views['samples'] if s['phase'] == 'reload_finish')
reset = next(s for s in views['samples'] if s['phase'] == 'reset_ready')
endpoint_gap = math.dist(finish['display_right'], reset['display_right'])

guards = json.loads((ROOT / 'tmp/weapon-animation-reuse/preflight_v1.json').read_text())['files']
guards += json.loads((ROOT / 'Assets/Integration/WEAPON_ANIMATION_REUSE_DRAFT_INVENTORY_20261004.json').read_text())['files']
guards += json.loads((ROOT / 'Assets/Integration/RELOAD_APPROVED_BINDING_PROOF_INVENTORY_20261004.json').read_text())['files']
mismatches = []
for row in guards:
    path = ROOT / row['path']
    if not path.is_file() or path.stat().st_size != row['size_bytes'] or hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
        mismatches.append(row['path'])
report = {
    'status': 'offline_diagnosis_only_not_repaired' if not mismatches else 'blocked_native_guard_conflict',
    'native_authored': False, 'map_saved': False, 'runtime_test_run': False,
    'inputs': inputs, 'construction_source_findings': evidence,
    'finding': 'Existing Ready entry directly plays Rifle_Idle and separately recomputes held framing. Proof retains this switch. No constructed transition in that path.',
    'limitations': [
        'Construction source is not a newly queried compiled graph or natural-end runtime trace.',
        'Two potentially discontinuous switches are identified; their separate causal contribution requires native observation.',
        'Missing return clip is unproved. Prefer existing-clip transition after native cause proof, not new motion.',
        'Index penetration and sleeve cause remain unproved; no finger/skin edit authorized by this audit.',
        'Frozen finish vs explicit reset is not a measured adjacent-frame or natural-completion jump.',
    ],
    'prior_frozen_endpoint_comparison': {
        'finish_pose_seconds': finish['pose_seconds'],
        'reset_pose_seconds': reset['pose_seconds'],
        'display_right_proxy_gap_cm': endpoint_gap,
        'is_natural_transition': False,
    },
    'protected_count': len(guards), 'mismatches': mismatches,
    'next': 'Minimal safe natural-end pose/framing/transaction observation, under lane A native reservation; no existing failed author/visual job rerun.',
}
(out / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'status': report['status'], 'protected': len(guards),
                  'mismatches': len(mismatches), 'prior_nonadjacent_endpoint_gap_cm': endpoint_gap,
                  'result': str(out / 'result.json')}, indent=2))
if mismatches:
    raise SystemExit(2)
