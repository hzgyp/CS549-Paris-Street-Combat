"""Preserve final raw local evidence beside the private, immutable delivery."""
import json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import digest
BASE=ROOT/'tmp/g1-playtest-revision-20261008'
OUT=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/G1PlaytestRevisionV1/delivery_v1'

def main():
    delivery=json.loads((OUT/'delivery_receipt.json').read_text())
    frozen=OUT/'FinalQualification'
    assert not frozen.exists(),'Protect existing qualification'
    rows=[]
    for check in delivery['checks']:
        identity=check['identity'];origin=BASE/identity
        audit=origin/'read_only_audit.json'
        assert digest(audit)==check['audit_sha256']
        report=json.loads(audit.read_text())
        assert report['status']=='pass_integrity_numeric_visual_review_separate'
        files=['launch.json','game.log','read_only_audit.json']
        if (origin/'result.json').exists():files.append('result.json')
        files += [x['path'] for x in report['images']]
        for name in files:
            src=origin/name;dst=frozen/identity/name
            dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
            assert digest(src)==digest(dst)
            rows.append(dict(path=dst.relative_to(frozen).as_posix(),size_bytes=dst.stat().st_size,sha256=digest(dst)))
    result=dict(status='frozen_raw_local_qualification',delivery_receipt_sha256=digest(OUT/'delivery_receipt.json'),
        scope='Finite local input/checkpoint and ordinary UI; actual image review recorded separately; no human/full-contact/FPS/course claim',files=rows)
    (frozen/'MANIFEST.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=result['status'],files=len(rows)),indent=2))
if __name__=='__main__':main()
