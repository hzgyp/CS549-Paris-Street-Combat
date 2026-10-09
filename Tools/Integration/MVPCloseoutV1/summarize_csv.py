"""Preserve full native CSV frame statistics; never infer a complete test pass."""
import argparse
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path


def stats(values):
    values = sorted(values)
    if not values:
        raise ValueError('No finite native samples')
    return dict(count=len(values), mean=statistics.mean(values),
                median=statistics.median(values), p95=values[math.ceil(.95*len(values))-1],
                maximum=values[-1])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    parser.add_argument('--scope', required=True)
    args = parser.parse_args()
    output = args.run / 'performance_summary.json'
    if output.exists():
        raise FileExistsError('Preserve occupied summary identity')
    results = []
    for path in sorted((args.run / 'CSV').glob('*.csv')):
        with path.open(encoding='utf-8-sig', newline='') as stream:
            raw_rows = list(csv.DictReader(stream))
        rows = [row for row in raw_rows if row.get('FrameTime') != 'FrameTime'
                and not (row.get('EVENTS') or '').startswith('[HasHeaderRowAtEnd]')]
        footer_valid = len(raw_rows) >= 2 and (raw_rows[-1].get('EVENTS') or '').startswith('[HasHeaderRowAtEnd]') and raw_rows[-2].get('FrameTime') == 'FrameTime'
        metrics = {}
        for name in ['FrameTime', 'GameThreadTime', 'RenderThreadTime', 'GPUTime',
                     'GameThreadTime_CriticalPath', 'RenderThreadTime_CriticalPath',
                     'MemoryFreeMB', 'TransientMemoryUsedMB']:
            values = []
            for row in rows:
                try:
                    value = float(row[name])
                except (KeyError, ValueError, TypeError):
                    continue  # Native CSV footer/metadata, never frame trimming.
                if math.isfinite(value):
                    values.append(value)
            if values:
                metrics[name] = stats(values)
        frame = [float(row['FrameTime']) for row in rows
                 if row.get('FrameTime') and row['FrameTime'].replace('.', '', 1).isdigit()]
        assert frame and all(math.isfinite(x) and x > 0 for x in frame)
        results.append(dict(file=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                            native_final_footer_present=footer_valid,
                            measurement_status='complete_native_csv' if footer_valid else 'incomplete_prefix_not_performance_acceptance',
                            frame_time_ms=stats(frame), average_fps=1000/statistics.mean(frame) if footer_valid else None,
                            partial_prefix_fps=None if footer_valid else 1000/statistics.mean(frame),
                            measured_seconds=sum(frame)/1000,
                            structural_header_metadata_rows=len(raw_rows)-len(rows),
                            hitches_over_50ms=sum(x > 50 for x in frame),
                            hitches_over_100ms=sum(x > 100 for x in frame), metrics=metrics))
    assert results, 'Native CSV missing'
    receipt = dict(scope=args.scope, trimmed_frames=0, captures=results,
                   acceptance='Actual measurements only; use matching functional and release records')
    output.write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps({**receipt, 'captures': [{k:v for k,v in x.items() if k != 'metrics'} for x in results]}, indent=2))


if __name__ == '__main__':
    main()
