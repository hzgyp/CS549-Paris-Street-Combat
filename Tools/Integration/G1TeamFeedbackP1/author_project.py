"""Copy the source and mutable build caches; reuse protected Content by junction."""
import json, shutil, subprocess
from prepare import ROOT, OUT, SOURCE, rows, sha

def main():
    assert (OUT/'revision.json').exists()
    files=rows(SOURCE);assert len(files)==48
    manifest=dict(format='paris-source-snapshot-v1',scope='Unselected P1 child of P0 v4: loadout/movement/HUD/initial layout; original cooked reflection and transactions retained',files=files)
    (SOURCE.parent/'SOURCE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n','utf-8')
    project=OUT/'candidate_v1/Project';assert not project.exists();shutil.copytree(SOURCE,project)
    parent=ROOT/'tmp/g1-team-feedback-20261010/candidate_v4/Project'
    for name in ['Binaries','Intermediate']:shutil.copytree(parent/name,project/name)
    command="New-Item -ItemType Junction -Path '"+str(project/'Content').replace("'","''")+"' -Value '"+str(ROOT/'Unreal/ParisStreetCombat/Content').replace("'","''")+"' | Out-Null"
    subprocess.run(['powershell','-NoProfile','-Command',command],check=True)
    (OUT/'candidate_v1/prepare.json').write_text(json.dumps(dict(status='prepared_not_built',project=str(project),source_files=files,source_manifest_sha256=sha(SOURCE.parent/'SOURCE_MANIFEST.json')),indent=2)+'\n','utf-8')
    old=ROOT/'Tools/Integration/G1TeamFeedbackV1'
    dest=ROOT/'Tools/Integration/G1TeamFeedbackP1'
    for name in ['build.ps1','launch_check.ps1','launch_route.ps1']:
        s=(old/name).read_text('utf-8-sig').replace('g1-team-feedback-20261010','g1-team-feedback-p1-20261010').replace('ParisTeamP0_','ParisTeamP1_')
        if name=='build.ps1':s=s.replace('candidate_v4','candidate_v5').replace('candidate_v3','candidate_v4').replace('candidate_v2','candidate_v3').replace("'candidate_v1','candidate_v3','candidate_v4','candidate_v5'","'candidate_v1','candidate_v2','candidate_v3','candidate_v4'")
        if name=='launch_route.ps1':s=s.replace("('-ParisUXTest='+$Mode)","('-ParisAVAuditOut=\"'+$taskOut+'/av\"'),('-ParisUXTest='+$Mode)")
        (dest/name).write_text(s,'utf-8')
    print(json.dumps(dict(status='prepared_not_built',source_files=48,project=str(project))))

if __name__=='__main__':main()
