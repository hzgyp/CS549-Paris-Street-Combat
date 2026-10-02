"""Read-only UE CSV startup sample summary; never a route/stress FPS pass."""
import argparse
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('csv', type=Path)
args = parser.parse_args()
source_hash = hashlib.sha256(args.csv.read_bytes()).hexdigest()
with args.csv.open(encoding='utf-8-sig', newline='') as handle:
    rows = list(csv.reader(handle))
header = rows[0]
frame_index = header.index('FrameTime')
data = []
for row in rows[1:]:
    if len(row) != len(header):
        continue  # UE metadata trailer is not a frame.
    try:
        value = float(row[frame_index])
    except ValueError:
        continue  # UE repeats the header at the end.
    assert math.isfinite(value) and value > 0, 'Invalid frame sample'
    data.append(row)
assert len(data) == 600, f'Expected the documented 600 frames, observed {len(data)}'

def summarize(records):
    result = {'frames': len(records)}
    for column in ('FrameTime', 'GameThreadTime', 'RenderThreadTime', 'GPUTime'):
        values = [float(row[header.index(column)]) for row in records]
        assert all(math.isfinite(value) and value >= 0 for value in values)
        ordered = sorted(values)
        result[column + '_ms'] = {
            'mean': statistics.mean(values), 'median': statistics.median(values),
            'p95_nearest_rank': ordered[math.ceil(.95 * len(values)) - 1],
            'max': max(values),
        }
    result['fps_from_mean_frame_time'] = 1000 / result['FrameTime_ms']['mean']
    result['frames_over_16_6667_ms'] = sum(float(r[frame_index]) > 1000 / 60 for r in records)
    return result

print(json.dumps({
    'source': str(args.csv), 'sha256': source_hash,
    'scope': 'Stationary offscreen startup, not warmed traversal, AI, stress or performance acceptance',
    'percentile': 'Nearest rank ceil(0.95*N), no outlier removal',
    'all_frames_1_to_600': summarize(data),
    'last_frames_301_to_600': summarize(data[300:]),
    'subset_note': 'Fixed second half, chosen before analysis; includes frame-500 screenshot cost. Not a separate warmed run.',
    'source_unchanged': hashlib.sha256(args.csv.read_bytes()).hexdigest() == source_hash,
}, indent=2))
