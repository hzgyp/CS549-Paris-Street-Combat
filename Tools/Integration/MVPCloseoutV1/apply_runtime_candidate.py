"""Apply only the documented private G1 native route candidate to a fresh wrapper."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def replace_once(text, old, new):
    if text.count(old)!=1: raise ValueError('Unknown or repeated candidate anchor: '+old[:80])
    return text.replace(old,new,1)

def main():
    p=argparse.ArgumentParser();p.add_argument('identity');a=p.parse_args()
    out=ROOT/'tmp/mvp-closeout-20261008'/a.identity
    prerequisite=json.loads((out.parent/'cohort_nativefinish_v1/result.json').read_text())
    assert prerequisite['status']=='pass_three_scripted_integrated_rounds_human_gate_pending'
    assert len(prerequisite['rounds'])==3
    proof=prerequisite['events']
    assert sum(e.get('event')=='both_allies_original_55cm_25sec_far_bank_gate_pass' for e in proof)==3
    receipt=out/'native_candidate.json';assert not receipt.exists(), 'Preserve candidate identity'
    plugin=out/'Project/Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1'
    originals=ROOT/'Unreal/ParisStreetCombat/Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1'
    changes=[]
    for rel in ['Private/ParisBridgeMission.cpp','Public/ParisBridgeMission.h']:
        target=plugin/rel; original=originals/rel
        assert target.read_bytes()==original.read_bytes(), 'Only exact baseline wrapper can be patched'
        text=target.read_text();before=digest(target)
        if rel.endswith('.cpp'):
            text=replace_once(text,'#include "NavigationSystem.h"','#include "NavigationSystem.h"\n#include "NavMesh/RecastNavMesh.h"\n#include "NavAreas/NavArea_Null.h"')
            text=replace_once(text,'    FString Prefix;','    ConfigFingerprint+=TEXT("_BridgeConstraintV1Nearbank");\n    SlotPrefix=TEXT("ParisG1V3");\n    FString Prefix;')
            text=replace_once(text,'        GateBrains(false);\n        if(bLoadRequested)',
                '        if(!ApplyBridgeNavigationConstraint(Error)) { Fail(Error); return; }\n        GateBrains(false);\n        if(bLoadRequested)')
            text=replace_once(text,'    const FVector Ends[] = {FVector(-3162.5,-25937.5,110.116898),FVector(1950,-20650,114.262990),FarBankFeet};',
                '    if(InitialLocations.Num()!=6 || !IsValid(Roster[0])) { Error=TEXT("Original near-bank roster absent."); return false; }\n'
                '    const FVector InitialFeet=InitialLocations[0]-FVector(0,0,Roster[0]->GetCapsuleComponent()->GetScaledCapsuleHalfHeight());\n'
                '    const FVector Ends[] = {InitialFeet,FVector(1950,-20650,114.262990),FarBankFeet};')
            fragment=(Path(__file__).parent/'NativeBridgeConstraint.inc').read_text()
            text=replace_once(text,'bool AParisBridgeMission::BuildBridgePath(FString& Error)',fragment+'\nbool AParisBridgeMission::BuildBridgePath(FString& Error)')
        else:
            text=replace_once(text,'    bool bBridgeTransitArmed = false;','    bool bBridgeNavigationValidated = false;\n    bool ApplyBridgeNavigationConstraint(FString& Error);\n    bool bBridgeTransitArmed = false;')
        target.write_text(text)
        changes.append(dict(path=str(target.relative_to(out)),original_sha256=before,candidate_sha256=digest(target)))
    receipt.write_text(json.dumps(dict(scope='UNSELECTED private native G1 constraint/nearbank centreline/checkpoint epoch; canonical inputs unchanged',
        prerequisite_sha256=digest(out.parent/'cohort_nativefinish_v1/result.json'),changes=changes),indent=2)+'\n')
    print(json.dumps({'candidate':a.identity,'changed_mission_files':len(changes)}))

if __name__=='__main__': main()
