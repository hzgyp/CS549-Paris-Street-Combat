"""Evaluate the separately named initial population stress level; never infer higher capacity."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]

def main():
    p=argparse.ArgumentParser();p.add_argument('identity');a=p.parse_args()
    out=ROOT/'tmp/mvp-closeout-20261008'/a.identity;target=out/'finite_stress_result.json'
    assert not target.exists(), 'Preserve stress result'
    launch=json.loads((out/'launch.json').read_text());audit=json.loads((out/'read_only_audit.json').read_text())
    perf=json.loads((out/'performance_summary.json').read_text());assert '-ParisCapture' not in launch['arguments']
    assert launch['mode']=='candidate' and audit['rounds']==1 and audit['normal_exit']
    captures=perf['captures'];assert len(captures)==1 and captures[0]['native_final_footer_present']
    actual=captures[0];failed=actual['frame_time_ms']['mean']>1000/60
    result=dict(schedule=[6,12,18],cap=18,measured_total_combatants=6,
        current_population='1 player + 2 original squad Allies + 3 original guards; original lifecycle/deaths retained',
        scope='Separate finite initial population entry on the declared native G1 candidate; original lifecycle/deaths retained. Not sustained six-active load, higher capacity, or an independent/coordinated comparison.',
        limit='60 FPS mean target missed at initial six-person load; stop predeclared schedule' if failed else 'Initial level passes; higher native site/population admission required before next entry',
        status='stop_at_initial_level_performance_limit' if failed else 'initial_level_pass_higher_levels_pending',
        higher_levels=[dict(total=n,status='Not run - first-level stop' if failed else 'Not run - awaiting native admission') for n in [12,18]],
        frames=actual['frame_time_ms']['count'],measured_seconds=actual['measured_seconds'],
        frame_time_ms=actual['frame_time_ms'],average_fps=actual['average_fps'],
        receipt_sha256={name:hashlib.sha256((out/name).read_bytes()).hexdigest() for name in ['launch.json','read_only_audit.json','performance_summary.json']})
    target.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
