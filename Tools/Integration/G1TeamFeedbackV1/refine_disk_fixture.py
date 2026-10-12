"""Readonly-negative uses a valid journal copy; do not test invalid deserialization."""
import json,shutil,subprocess
from pathlib import Path
from prepare import ROOT,OUT,SOURCE,rows,sha

def main():
    old=OUT/'candidate_v2';build=json.loads((old/'build.json').read_text('utf-8-sig'))
    assert build['status']=='built_runtime_unverified' and build['exit_code']==0
    retained=old/'compiled_source_snapshot';assert not retained.exists();shutil.copytree(SOURCE,retained)
    plan=json.loads((old/'prepare.json').read_text('utf-8-sig'))
    for r in plan['source_files']:assert sha(retained/r['path'])==r['sha256']
    rel='Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisInteractionProbe.cpp'
    shutil.copyfile(Path(__file__).parent/'ParisInteractionProbe.cpp',SOURCE/rel)
    files=rows(SOURCE);assert [r['path'] for r in plan['source_files'] if sha(SOURCE/r['path'])!=r['sha256']]==[rel]
    manifest=json.loads((SOURCE.parent/'SOURCE_MANIFEST.json').read_text('utf-8-sig'));manifest['files']=files
    (SOURCE.parent/'SOURCE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n','utf-8')
    project=OUT/'candidate_v3/Project';assert not project.exists();shutil.copytree(SOURCE,project)
    for n in ['Binaries','Intermediate']:shutil.copytree(old/'Project'/n,project/n)
    command="New-Item -ItemType Junction -Path '"+str(project/'Content').replace("'","''")+"' -Value '"+str(ROOT/'Unreal/ParisStreetCombat/Content').replace("'","''")+"' | Out-Null"
    subprocess.run(['powershell','-NoProfile','-Command',command],check=True)
    result=dict(status='prepared_not_built',project=str(project),source_files=files,source_manifest_sha256=sha(SOURCE.parent/'SOURCE_MANIFEST.json'),changed_from_v2=[rel],reason='Write-negative uses readonly valid journal, not unrelated corrupt-file deserialization; no production change')
    (OUT/'candidate_v3/prepare.json').write_text(json.dumps(result,indent=2)+'\n','utf-8')
    print(json.dumps(dict(status=result['status'],changed=[rel])))

if __name__=='__main__':main()
