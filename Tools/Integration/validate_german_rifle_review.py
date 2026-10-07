"""Independent recorded-sample validation; never rewrite the failed raw report."""
import json
import math
from german_rifle_ue_common import ROOT, STORE, guard, read, sha, new_output

source = STORE / 'Evidence/GermanRifleUEV1/review_v3/result.json'
report = read(source)
out = new_output('review_validation_v1')
rows = [a for s in report['samples'] for a in s['germans']]
deviations = [abs(v - 1) for a in rows for v in a['gun_scale']]
checks = {
    'no_reported_runtime_errors': not report['errors'],
    'all_samples_have_three_equipped_germans': bool(rows) and all(len(s['germans']) == 3 for s in report['samples']),
    'finite_unit_scale_within_1e_6': all(math.isfinite(v) and abs(v - 1) <= 1e-6 for a in rows for v in a['gun_scale']),
    'no_collision_all_samples': all('NO_COLLISION' in a['collision'] for a in rows),
    'grip_anchor_below_1cm': bool(rows) and max(a['grip_error_cm'] for a in rows) < 1,
    'retained_other_raw_checks': all(value for key, value in report['checks'].items() if key != 'all_guns_unit_scale_no_collision'),
    'protected_412_inputs_unchanged': guard() == 412,
}
result = {
    'status': 'recorded_numeric_checks_passed_not_visual_or_human_acceptance' if all(checks.values()) else 'failed',
    'source': {'path': source.relative_to(ROOT).as_posix(), 'sha256': sha(source), 'raw_status': report['status']},
    'checks': checks, 'sample_count': len(report['samples']), 'actor_samples': len(rows),
    'unit_scale_tolerance': 1e-6, 'max_scale_deviation': max(deviations),
    'max_grip_error_cm': max(a['grip_error_cm'] for a in rows),
    'visual_limitations': [
        'Walk-side image is standing after movement, not a walking-phase proof.',
        'Reload images contain generic open-hand poses; early/mid rendered poses appear repeated despite differing bone snapshots.',
        'Late/recovery views have foreground obstruction; numeric samples do not establish visible reload recovery/contact.',
        'Do not claim matched-phase visual reload acceptance from these captures.',
    ],
    'human_review': 'pending', 'raw_report_changed': False,
}
(out / 'result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: result[k] for k in ('status', 'sample_count', 'actor_samples', 'max_scale_deviation', 'max_grip_error_cm')}, indent=2))
assert all(checks.values()), checks
