"""Install opt-in checks; copy mutable build caches, never hard-link authoring."""
import json, shutil, subprocess
from pathlib import Path
from prepare import ROOT, OUT, SOURCE, rows, sha

def main():
    assert (OUT/'revision.json').exists()
    private=SOURCE/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private'
    shutil.copyfile(Path(__file__).parent/'ParisInteractionProbe.cpp',private/'ParisInteractionProbe.cpp')
    module=private/'ParisBridgeMissionV1.cpp';s=module.read_text('utf-8-sig')
    assert s.count('#include "ParisBridgeMission.h"')==1
    s=s.replace('#include "ParisBridgeMission.h"','#include "ParisBridgeMission.h"\n#include "ParisMissionInteraction.h"',1)
    assert s.count('  ParisGameplayAV::Initialize();')==1
    s=s.replace('  ParisGameplayAV::Initialize();','  ParisGameplayAV::Initialize();\n  ParisInteractionProbe::Initialize();',1)
    assert s.count('ParisGameplayAV::Shutdown();')==1
    s=s.replace('ParisGameplayAV::Shutdown();','ParisInteractionProbe::Shutdown();ParisGameplayAV::Shutdown();',1)
    module.write_text(s,'utf-8')
    files=rows(SOURCE);assert len(files)==45
    manifest=dict(format='paris-source-snapshot-v1',scope='Menu/checkpoint child and explicitly opt-in native diagnostic; parent weapon/resource/save/native assets preserved; unselected pending human review',files=files)
    (SOURCE.parent/'SOURCE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n','utf-8')
    project=OUT/'candidate_v1/Project';assert not project.exists()
    shutil.copytree(SOURCE,project)
    parent=ROOT/'tmp/g1-foot-contact-audio-v2-20261009/candidate_v2/Project'
    for name in ['Binaries','Intermediate']:
        assert (parent/name).is_dir();shutil.copytree(parent/name,project/name)
    command="New-Item -ItemType Junction -Path '"+str(project/'Content').replace("'","''")+"' -Value '"+str(ROOT/'Unreal/ParisStreetCombat/Content').replace("'","''")+"' | Out-Null"
    subprocess.run(['powershell','-NoProfile','-Command',command],check=True)
    result=dict(status='prepared_not_built',project=str(project),source_files=files,source_manifest_sha256=sha(SOURCE.parent/'SOURCE_MANIFEST.json'))
    (OUT/'candidate_v1/prepare.json').write_text(json.dumps(result,indent=2)+'\n','utf-8')
    print(json.dumps(dict(status=result['status'],source_files=45,project=str(project))))

if __name__=='__main__':main()
