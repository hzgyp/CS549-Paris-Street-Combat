"""One measured correction after the retained double-contact/overlap negative."""
import json,shutil,subprocess
from common import ROOT,OUT,digest,save,row
def main():
    prior=json.loads((OUT/'candidate_v1/prepare.json').read_text('utf-8-sig'));old=OUT/'candidate_v1/Project';new=OUT/'candidate_v2/Project'
    assert not new.exists(),'Preserve occupied measured source identity'
    for r in prior['source_files']:
        assert digest(old/r['path'])==r['sha256'];dest=new/r['path'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(old/r['path'],dest)
    command="New-Item -ItemType Junction -Path '"+str(new/'Content').replace("'","''")+"' -Value '"+str(ROOT/'Unreal/ParisStreetCombat/Content').replace("'","''")+"' | Out-Null"
    subprocess.run(['C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe','-NoProfile','-Command',command],check=True)
    cpp=new/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisGameplayAV.cpp';s=cpp.read_text('utf-8-sig')
    def replace(a,b):
        nonlocal s
        assert s.count(a)==1,a[:120];s=s.replace(a,b,1)
    replace('double Height=0,Drop=0,LastContact=-100;bool Descending=false;', 'double Height=0,Drop=0,LastContact=-100,Low=0;bool Descending=false,Armed=true;')
    replace(' if(!S.Ready||!S.Cues.Contains(Cue)',
      ' if(!S.AuditDir.IsEmpty()&&FParse::Param(FCommandLine::Get(),TEXT("ParisAVSoloPlayer"))&&!C->IsPlayerControlled())return;\n if(!S.Ready||!S.Cues.Contains(Cue)')
    replace('T.Feet[I].Height=Z[I];T.Feet[I].Drop=0;T.Feet[I].Descending=false;',
      'T.Feet[I].Height=Z[I];T.Feet[I].Low=Z[I];T.Feet[I].Armed=true;T.Feet[I].Drop=0;T.Feet[I].Descending=false;')
    replace('  auto& F=T.Feet[I];const double Dz=Z[I]-F.Height;F.Height=Z[I];',
      '  auto& F=T.Feet[I];const double Dz=Z[I]-F.Height;F.Height=Z[I];F.Low=FMath::Min(F.Low,Z[I]);\n'
      '  // A planted heel/toe roll is not another step; require a fresh visible lift.\n'
      '  if(!F.Armed&&Z[I]>=F.Low+1.0&&Z[I]>=Z[1-I]+1.5)F.Armed=true;')
    replace('   if(F.Drop>=1.2&&', '   if(F.Armed&&F.Drop>=1.2&&')
    replace('    F.LastContact=Now;T.LastStep=Now;', '    F.LastContact=Now;F.Armed=false;F.Low=Z[I];T.LastStep=Now;')
    replace('TEXT("jump"),.48);','TEXT("jump"),.65);')
    cpp.write_text(s,'utf-8')
    prior['project']=str(new);prior['source_files']=[row(new/r['path'],new) for r in prior['source_files']]
    prior['status']='measured_contact_latch_and_solo_audit_prepared_runtime_unverified';prior['negative_reference']='candidate_v1 d889ff5c / checks/actions/foot_contact_plot.png / verify_v1_overlap_failed.py'
    save(OUT/'candidate_v2/prepare.json',prior)
    shutil.copytree(OUT/'candidate_v1/Audio',OUT/'candidate_v2/Audio')
    for name in ['build','launch_check']:
        src=Path(__file__).parent/(name+'.ps1');text=src.read_text('utf-8-sig').replace('candidate_v1','candidate_v2')
        if name=='launch_check':
            text=text.replace("('checks/'+$Mode)","('checks_solo/'+$Mode)").replace("'-ParisUXTest='+$Mode","'-ParisUXTest='+$Mode")
            text=text.replace("'-ini:Engine:[Audio]:UnfocusedVolumeMultiplier=1.0'","'-ParisAVSoloPlayer','-ini:Engine:[Audio]:UnfocusedVolumeMultiplier=1.0'")
            text=text.replace('ParisFootV220261009_','ParisFootV2Solo20261009_')
        (Path(__file__).parent/(name+'_measured.ps1')).write_text(text,'utf-8')
    print(json.dumps(dict(source_files=42,correction='Lift-rearmed foot latch; audit-only player isolation; takeoff gain.65',parent_game='d889ff5c')))
if __name__=='__main__':
    from pathlib import Path
    main()
