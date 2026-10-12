"""Keep the cooked reflection layout; interaction revision is runtime-only."""
import json, shutil, subprocess
from prepare import ROOT, OUT, SOURCE, rows, sha

def main():
    old=OUT/'candidate_v3'
    plan=json.loads((old/'prepare.json').read_text('utf-8-sig'))
    retained=old/'failed_runtime_source_snapshot'
    assert not retained.exists();shutil.copytree(SOURCE,retained)
    for r in plan['source_files']:assert sha(retained/r['path'])==r['sha256']
    rel='Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Public/ParisBridgeMission.h'
    p=SOURCE/rel;s=p.read_text('utf-8-sig')
    bad='UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="G1 Interaction") int32 InteractionRevision=0;'
    assert s.count(bad)==1
    p.write_text(s.replace(bad,'// Runtime UI feedback revision: keep the existing cooked property schema.\n    int32 InteractionRevision=0;'),'utf-8')
    files=rows(SOURCE)
    assert [r['path'] for r in plan['source_files'] if sha(SOURCE/r['path'])!=r['sha256']]==[rel]
    m=SOURCE.parent/'SOURCE_MANIFEST.json';manifest=json.loads(m.read_text('utf-8-sig'));manifest['files']=files
    m.write_text(json.dumps(manifest,indent=2)+'\n','utf-8')
    project=OUT/'candidate_v4/Project';assert not project.exists();shutil.copytree(SOURCE,project)
    for n in ['Binaries','Intermediate']:shutil.copytree(old/'Project'/n,project/n)
    command="New-Item -ItemType Junction -Path '"+str(project/'Content').replace("'","''")+"' -Value '"+str(ROOT/'Unreal/ParisStreetCombat/Content').replace("'","''")+"' | Out-Null"
    subprocess.run(['powershell','-NoProfile','-Command',command],check=True)
    result=dict(status='prepared_not_built',project=str(project),source_files=files,source_manifest_sha256=sha(m),changed_from_v3=[rel],reason='Runtime-only field; restores exact parent UPROPERTY/UFUNCTION schema for existing unversioned cooked map')
    (OUT/'candidate_v4/prepare.json').write_text(json.dumps(result,indent=2)+'\n','utf-8')
    print(json.dumps(dict(status=result['status'],changed=[rel])))

if __name__=='__main__':main()
