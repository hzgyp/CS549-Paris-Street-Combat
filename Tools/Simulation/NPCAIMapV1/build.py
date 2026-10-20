"""Read-only inputs -> unique local interaction design board. Requires Pillow."""
import argparse
from collections import Counter
import hashlib
import json
from itertools import groupby
from pathlib import Path
import re
import shutil
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
SRC = Path(__file__).resolve().parent
FIGURES = ROOT / 'tmp/map-survey-overnight-20261013/collections/complete_v3/figures_v1'
REPLAY = ROOT / 'tmp/npc-ai-v2-20261017/run_v6/replay.html'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    out = (ROOT / args.out).resolve()
    assert out.is_relative_to(ROOT / 'tmp/npc-ai-map-v1-20261017')
    assert not out.exists(), 'Retain previous runs; choose a unique output'
    audit = json.loads((FIGURES / 'FIGURE_AUDIT.json').read_text(encoding='utf-8'))
    assert audit['status'] == 'pass_independent_figures_raw_hashes_tile_pixel_parity_scope_counts'
    assert audit['dimensions'] == [720, 960] and audit['cell_cm'] == 25
    assert audit['world_bounds_m'] == [-4, 176, -236, 4]
    assert audit['scopes_merged'] is False
    # Original renderer: (c-c0,r-r0); c=(x_cm+50400)/25-.5,
    # r=(50400-y_cm)/25-.5. Pixel centres, X right/Y down.
    assert audit['grid_origin'] == [2000, 2000]
    analysis_path = FIGURES.parent / 'analysis_v1/ANALYSIS.json'
    analysis = json.loads(analysis_path.read_text(encoding='utf-8'))
    assert sha(analysis_path) == audit['inputs'][str(analysis_path)]
    inputs = []
    images = []
    status_grids = {}
    for scope, layers in [('saved', 3), ('bounded_expanded', 5)]:
        for layer in range(layers):
            pair = {'scope': scope, 'layer': layer}
            for kind in ['candidate', 'status']:
                rel = f'{scope}/L{layer}_{kind}_25cm.png'
                path = FIGURES / rel
                expected = audit['outputs'][rel.replace('/', '\\')]
                assert path.stat().st_size == expected['size_bytes'] and sha(path) == expected['sha256'], rel
                with Image.open(path) as image:
                    assert image.size == (720, 960)
                    if kind == 'status':
                        colours = Counter(image.convert('RGB').get_flattened_data())
                        counts = {name: colours[tuple(rgb)] for name, rgb in audit['status_colours'].items()}
                        expected_counts = audit['scopes'][scope]['layer_status_counts'][str(layer)]
                        assert counts == {name: expected_counts.get(name, 0) for name in audit['status_colours']}
                        assert sum(counts.values()) == 720 * 960
                        pair['counts'] = counts
                        codes = {tuple(rgb): i for i, rgb in enumerate(audit['status_colours'].values())}
                        grid = bytes(codes[rgb] for rgb in image.convert('RGB').get_flattened_data())
                        # Codes use insertion order: unknown=0, rejected=1, non-city=2, city=3.
                        rle = [value for code, values in groupby(grid) for value in (code, sum(1 for _ in values))]
                        restored = bytes(value for i in range(0, len(rle), 2) for value in [rle[i]] * rle[i+1])
                        assert restored == grid
                        status_grids[f'{scope}/L{layer}'] = rle
                    else:
                        assert image.mode == '1'
                        pair['white_centres'] = sum(bool(v) for v in image.get_flattened_data())
                pair[kind] = 'maps/' + rel
                inputs.append({'path': str(path.relative_to(ROOT)), **expected})
            assert pair['white_centres'] == pair['counts']['city_admitted']
            images.append(pair)
    text = REPLAY.read_text(encoding='utf-8')
    match = re.search(r'const evidence=(\{.*?\});\r?\nif\(!evidence\)', text, re.S)
    assert match, 'Canonical replay schema mismatch'
    evidence = json.loads(match.group(1))
    candidates = [run for run in evidence['runs'] if not run['reference']]
    assert len(candidates) == 10
    for run in candidates:
        assert not run['reference'] and run['view_frames']
    guards = [REPLAY, FIGURES / 'FIGURE_AUDIT.json', analysis_path,
              ROOT / 'Docs/Development/CURRENT_NPC_AI_CANDIDATE.json',
              ROOT / 'Docs/Development/CURRENT_TUTORIAL_SOURCE_PENDING.json',
              ROOT / 'tmp/map-survey-continuation-20261013/PROGRESS.json',
              ROOT / 'tmp/map-survey-overnight-20261013/BATCH_QUEUE.json',
              ROOT / 'tmp/map-survey-overnight-20261013/RUN_RESERVATION.json']
    guards += [p for p in (ROOT / 'Tools/Simulation/NPCAIV2').glob('*') if p.is_file()]
    inputs += [{'path': str(p.relative_to(ROOT)), 'size_bytes': p.stat().st_size, 'sha256': sha(p)} for p in guards]
    # Coordinate round-trip independently from the UI implementation.
    for col, row in [(0, 0), (719, 959), (299, 827), (425, 499)]:
        x, y = -4 + (col + .5) * .25, 4 - (row + .5) * .25
        assert abs((x + 4) / .25 - .5 - col) < 1e-9
        assert abs((4 - y) / .25 - .5 - row) < 1e-9
    cp1 = analysis['fixed_planning_anchors_cm']['CP1']
    assert [(cp1[0] / 100 + 4) / .25 - .5, (4 - cp1[1] / 100) / .25 - .5] == [299, 827]
    out.mkdir(parents=True)
    for item in images:
        for kind in ['candidate', 'status']:
            target = out / item[kind]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(FIGURES / item[kind][5:], target)
    data = {'map': {'package': analysis['map'], 'dimensions': audit['dimensions'],
                    'cell_m': .25, 'bounds_m': audit['world_bounds_m'],
                    'surface_ordinals_are_not_floors': True, 'gameplay_travel_passed': False,
                    'scopes_merged': False, 'images': images,
                    'anchors_m': {k: [v / 100 for v in xy] for k, xy in analysis['fixed_planning_anchors_cm'].items()}},
            'evidence': {'config': evidence['config'], 'scenarios': candidates},
            'status_grid_runs': status_grids,
            'canonical_replay_sha256': sha(REPLAY)}
    (out / 'data.js').write_text('window.MAP_SKETCH_DATA=' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf-8')
    for name in ['index.html', 'board.js']:
        shutil.copyfile(SRC / name, out / name)
    (out / 'source_snapshot').mkdir()
    for p in SRC.glob('*'):
        if p.is_file():
            shutil.copyfile(p, out / 'source_snapshot' / p.name)
    receipt = {'status': 'pinned_rasters_and_canonical_traces_local_design_projection',
               'map_pixel_parity_checks': 16, 'status_count_checks': 8,
               'coordinate_roundtrip_checks': 5,
               'inputs': inputs, 'map': data['map'],
               'scope': 'layout_and_synthetic_trace_projection_not_map_simulation',
               'UE_entry': False, 'map_survey_resumed': False, 'shared_source_written': False}
    (out / 'INPUT_RECEIPT.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'out': str(out), 'maps': 16, 'scenarios': 10, 'index_bytes': (out / 'index.html').stat().st_size, 'data_bytes': (out / 'data.js').stat().st_size}))


if __name__ == '__main__':
    main()
