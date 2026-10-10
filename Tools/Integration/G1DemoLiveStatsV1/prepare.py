"""Freeze V6, prepare separate read-only diagnostics, never edit selected source."""
import hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];WORK=ROOT/'tmp/g1-demo-draft04-20261010'
V6=ROOT/'tmp/g1-demo-draft03-20261009/recording_v6/compiled_source_snapshot'
PROJECT=WORK/'recording_stats_v1/Project'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(base):return [dict(path=p.relative_to(base).as_posix(),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(base.rglob('*')) if p.is_file()]
assert not PROJECT.exists()
parent=rows(V6);assert len(parent)==44
shutil.copytree(V6,PROJECT)
private=PROJECT/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private'
for n in ['ParisLiveStats.h','ParisLiveStats.cpp']:shutil.copyfile(Path(__file__).parent/n,private/n)
module=private/'ParisBridgeMissionV1.cpp';s=module.read_text('utf-8')
assert s.count('#include "ParisDemoInput.h"')==1
s=s.replace('#include "ParisDemoInput.h"','#include "ParisDemoInput.h"\n#include "ParisLiveStats.h"')
assert s.count('ParisDemoInput::Initialize();')==1 and s.count('ParisDemoInput::Shutdown();')==1
s=s.replace('ParisDemoInput::Initialize();','ParisDemoInput::Initialize();\n  ParisLiveStats::Initialize();').replace('ParisDemoInput::Shutdown();','ParisLiveStats::Shutdown();ParisDemoInput::Shutdown();')
module.write_text(s,'utf-8')
b=PROJECT/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/ParisBridgeMissionV1.Build.cs'
s=b.read_text('utf-8');assert s.count('"RenderCore"')==1;b.write_text(s.replace('"RenderCore"','"RenderCore", "RHI"'),'utf-8')
changed=[r['path'] for r in parent if sha(PROJECT/r['path'])!=r['sha256']]
assert len(changed)==2 and all('ParisBridgeMissionV1.cpp' in p or p.endswith('.Build.cs') for p in changed)
assert sha(private/'ParisDemoInput.cpp')==sha(V6/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisDemoInput.cpp')
old=ROOT/'tmp/g1-demo-draft03-20261009/recording_v4/Archive/Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'
assert sha(old)=='a6015c94fd91fb73732d4ea18316ba80754d6de0e5d369a16e7e5725c9799472'
retained=WORK/'recording_stats_v1/retained_V6_Game.exe';shutil.copyfile(old,retained);assert sha(retained)==sha(old)
frozen=WORK/'recording_stats_v1/compiled_source_snapshot';shutil.copytree(PROJECT,frozen)
manifest=dict(status='prepared',parent='frozen V6 exact44',parent_files=parent,changed=changed,project=str(PROJECT),files=rows(frozen),scope='Only live read-only diagnostic panel/module wiring/RHI dependency. No input-helper or selected gameplay change',stable_runtime=str(old),retained_v6=str(retained),retained_v6_sha256=sha(retained))
(WORK/'recording_stats_v1/prepare.json').write_text(json.dumps(manifest,indent=2)+'\n','utf-8')
print(json.dumps(dict(status='prepared',files=len(manifest['files']),changed=changed,project=str(PROJECT))))
