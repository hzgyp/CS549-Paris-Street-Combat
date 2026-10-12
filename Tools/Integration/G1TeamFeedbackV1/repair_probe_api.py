"""Keep the failed source/build; adjust only the diagnostic platform-file API."""
import json,shutil,subprocess
from pathlib import Path
from prepare import ROOT,OUT,SOURCE,rows,sha

def main():
    old=OUT/'candidate_v1';build=json.loads((old/'build.json').read_text('utf-8-sig'))
    assert build['status']=='compile_failed' and build['exit_code']==6
    frozen=old/'failed_source_snapshot';assert not frozen.exists();shutil.copytree(SOURCE,frozen)
    original=json.loads((old/'prepare.json').read_text('utf-8-sig'))
    for r in original['source_files']:assert sha(frozen/r['path'])==r['sha256']
    rel='Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisInteractionProbe.cpp'
    shutil.copyfile(Path(__file__).parent/'ParisInteractionProbe.cpp',SOURCE/rel)
    files=rows(SOURCE);changed=[r['path'] for r in original['source_files'] if sha(SOURCE/r['path'])!=r['sha256']]
    assert changed==[rel]
    manifest=json.loads((SOURCE.parent/'SOURCE_MANIFEST.json').read_text('utf-8-sig'));manifest['files']=files
    (SOURCE.parent/'SOURCE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n','utf-8')
    project=OUT/'candidate_v2/Project';assert not project.exists();shutil.copytree(SOURCE,project)
    for n in ['Binaries','Intermediate']:shutil.copytree(old/'Project'/n,project/n)
    command="New-Item -ItemType Junction -Path '"+str(project/'Content').replace("'","''")+"' -Value '"+str(ROOT/'Unreal/ParisStreetCombat/Content').replace("'","''")+"' | Out-Null"
    subprocess.run(['powershell','-NoProfile','-Command',command],check=True)
    result=dict(status='prepared_not_built',project=str(project),source_files=files,source_manifest_sha256=sha(SOURCE.parent/'SOURCE_MANIFEST.json'),changed_from_failed_v1=changed,failed_v1_retained=str(frozen))
    (OUT/'candidate_v2/prepare.json').write_text(json.dumps(result,indent=2)+'\n','utf-8')
    print(json.dumps(dict(status=result['status'],changed=changed)))

if __name__=='__main__':main()
