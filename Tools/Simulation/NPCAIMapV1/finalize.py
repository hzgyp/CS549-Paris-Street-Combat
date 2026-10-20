"""One-time bounded receipt/routing; does not alter existing game or AI pointers."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / 'tmp/npc-ai-map-v1-20261017/run_v3'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p, value):
    with p.open('x', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    inputs = json.loads((RUN / 'INPUT_RECEIPT.json').read_text(encoding='utf-8'))
    browser = json.loads((RUN / 'BROWSER_VERIFY.json').read_text(encoding='utf-8'))
    assert browser['passed'] == browser['total'] == 22 and not browser['errors']
    changed = [item['path'] for item in inputs['inputs'] if
               (ROOT / item['path']).stat().st_size != item['size_bytes'] or sha(ROOT / item['path']) != item['sha256']]
    assert not changed, changed
    for p in Path(__file__).parent.glob('*.py'):
        ast.parse(p.read_text(encoding='utf-8'), filename=str(p))
    receipt = {'status': 'local_map_design_board_verified_not_measured_interaction_simulation',
               'protected_inputs': len(inputs['inputs']), 'changed_inputs': changed,
               'rasters_byte_identical': 16, 'colour_count_checks': 8,
               'status_pixel_reconstruction_checks': 8, 'coordinate_checks': 5,
               'browser_checks': 22, 'python_ast': 'pass',
               'visual_review': ['map-focus.jpg', 'map-mobile.jpg'],
               'mobile_display_was_resized': True,
               'failed_workflow_retained': 'run_v2 canvas readback SecurityError; zero checks not pass',
               'index_bytes': (RUN / 'index.html').stat().st_size,
               'data_bytes': (RUN / 'data.js').stat().st_size,
               'map_survey_resumed': False, 'UE_entry': False, 'shared_source_written': False}
    write(RUN / 'FINAL_RECEIPT.json', receipt)
    files = [p for p in RUN.rglob('*') if p.is_file()]
    files += [p for folder in ['Tools/Simulation/NPCAIMapV1', 'Docs/Development/NPCAIMapV1'] for p in (ROOT / folder).glob('*') if p.is_file()]
    items = [{'path': str(p.relative_to(ROOT)), 'size_bytes': p.stat().st_size, 'sha256': sha(p)} for p in sorted(set(files))]
    total = sum(item['size_bytes'] for item in items)
    handoff = {'status': receipt['status'], 'entry': str((RUN / 'index.html').relative_to(ROOT)),
               'keep_adjacent_files': ['index.html', 'board.js', 'data.js', 'maps/'],
               'files': items, 'inventoried_files': len(items), 'inventoried_bytes': total,
               'replay_recomputed_against_map': False, 'original_AI_replay_preserved': True}
    write(RUN / 'SOURCE_HANDOFF.json', handoff)
    pointer = {'status': receipt['status'], 'date': '2026-10-17',
               'implementation': 'Docs/Development/NPCAIMapV1/IMPLEMENTATION_20261017.md',
               'implementation_zh': 'Docs/Development/NPCAIMapV1/IMPLEMENTATION_20261017_ZH.md',
               'result': 'Docs/Development/NPCAIMapV1/RESULT_20261017.md',
               'result_zh': 'Docs/Development/NPCAIMapV1/RESULT_20261017_ZH.md',
               'source': 'Tools/Simulation/NPCAIMapV1', 'selected_run': str(RUN.relative_to(ROOT)),
               'entry': handoff['entry'], 'handoff': str((RUN / 'SOURCE_HANDOFF.json').relative_to(ROOT)),
               'handoff_sha256': sha(RUN / 'SOURCE_HANDOFF.json'),
               'index_bytes': receipt['index_bytes'], 'data_bytes': receipt['data_bytes'],
               'browser_checks': 22, 'map_rasters': 16, 'protected_inputs_unchanged': 37,
               'algorithm_authority': 'Docs/Development/CURRENT_NPC_AI_CANDIDATE.json',
               'measured_map_policy_simulation': False, 'UE_runtime_acceptance': False,
               'shared_source_native_written': False, 'new_build_authorized': False,
               'map_survey_resumed': False, 'human_design_acceptance': 'pending'}
    write(ROOT / 'Docs/Development/CURRENT_NPC_AI_MAP_SKETCH.json', pointer)
    print(json.dumps({'files': len(items), 'inventoried_bytes': total, 'protected_unchanged': len(inputs['inputs']), 'browser': '22/22', 'entry': handoff['entry']}))


if __name__ == '__main__':
    main()
