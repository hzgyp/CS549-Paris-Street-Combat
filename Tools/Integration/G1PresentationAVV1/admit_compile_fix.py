import json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'tmp/g1-av-revision-20261009'
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import digest
old=BASE/'candidate_v1';new=BASE/'candidate_v2';assert not new.exists()
receipt=json.loads((old/'prepare.json').read_text('utf-8-sig'));project=Path(receipt['project'])
assert json.loads((old/'build.json').read_text('utf-8-sig'))['status']=='compile_failed'
frozen=old/'FrozenSource';assert not frozen.exists()
for row in receipt['private_source_files']+[dict(path='WW2FranceLiberation.uproject',sha256=receipt['descriptor_sha256'])]:
    p=project/row['path'];assert digest(p)==row['sha256']
    q=frozen/row['path'];q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
cpp=project/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisGameplayAV.cpp'
before=cpp.read_text('utf-8');assert before.count('O.ToSharedRef()')==2
after=before.replace('O.ToSharedRef()','O');assert after==(Path(__file__).parent/'ParisGameplayAV.cpp').read_text('utf-8')
cpp.write_text(after,'utf-8');new.mkdir();shutil.copytree(old/'Audio',new/'Audio');shutil.copytree(old/'UI',new/'UI')
receipt['identity']='candidate_v2';receipt['compile_failure_frozen_source']=frozen.as_posix()
receipt['private_source_files']=[dict(r,sha256=digest(project/r['path']),size_bytes=(project/r['path']).stat().st_size) for r in receipt['private_source_files']]
receipt['correction']='Exactly two shared-ref Serialize call arguments; same owned Project/cache, no runtime yet'
(new/'prepare.json').write_text(json.dumps(receipt,indent=2)+'\n','utf-8')
print(json.dumps(dict(status=receipt['status'],identity='candidate_v2',frozen_source=str(frozen))))
