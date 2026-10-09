"""Extend only a fresh private native wrapper with the witnessed agent/settling fix."""
import argparse
import json
from pathlib import Path
from apply_runtime_candidate import ROOT,digest,replace_once

def main():
    p=argparse.ArgumentParser();p.add_argument('identity');a=p.parse_args();out=ROOT/'tmp/mvp-closeout-20261008'/a.identity
    proof=out.parent/'queries_v1/result.json';r=json.loads(proof.read_text())
    assert r['status']=='read_only_recorded_coordinate_queries_complete' and len(r['recorded_coordinate_queries'])==12
    assert all(q['valid']==q['agent_feet_start'] and not q['partial'] for q in r['recorded_coordinate_queries'])
    assert all(q['default_query_extent_cm']=='X=100.000 Y=100.000 Z=120.000' for q in r['recorded_coordinate_queries'])
    previous=json.loads((out/'native_candidate.json').read_text());record=out/'agent_candidate.json';assert not record.exists()
    base=out/'Project/Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1';changes=[]
    for row in previous['changes']:
        target=out/row['path'];assert digest(target)==row['candidate_sha256'];text=target.read_text();before=digest(target)
        if target.suffix=='.h':
            text=replace_once(text,'#include "ParisBridgeMission.generated.h"','#include "BehaviorTree/BTTaskNode.h"\n#include "ParisBridgeMission.generated.h"')
            text=replace_once(text,'class AAIController;','class AAIController;\n\nUCLASS()\nclass PARISBRIDGEMISSIONV1_API UParisG1AgentPlan : public UBTTaskNode\n{\n    GENERATED_BODY()\npublic:\n    UParisG1AgentPlan(const FObjectInitializer& Init);\n    virtual EBTNodeResult::Type ExecuteTask(UBehaviorTreeComponent& OwnerComp,uint8* NodeMemory) override;\n};')
            text=replace_once(text,'    bool bBridgeNavigationValidated = false;','    bool bAgentFeetPlanInstalled = false;\n    bool bBridgeFarBankSettling = false;\n    bool InstallAgentFeetPlan(FString& Error);\n    bool bBridgeNavigationValidated = false;')
        else:
            text=replace_once(text,'#include "BehaviorTree/BehaviorTree.h"','#include "BehaviorTree/BehaviorTree.h"\n#include "BehaviorTree/BehaviorTreeComponent.h"\n#include "BehaviorTree/BTCompositeNode.h"\n#include "BehaviorTree/BTDecorator.h"\n#include "BehaviorTree/BTService.h"')
            text=replace_once(text,'_BridgeConstraintV1Nearbank','_BridgeConstraintV2FeetPlan')
            text=replace_once(text,'SlotPrefix=TEXT("ParisG1V3");','SlotPrefix=TEXT("ParisG1V4");')
            text=replace_once(text,'        if(!ApplyBridgeNavigationConstraint(Error)) { Fail(Error); return; }','        if(!ApplyBridgeNavigationConstraint(Error) || !InstallAgentFeetPlan(Error)) { Fail(Error); return; }')
            old='    double Wanted=FMath::Max(0.0,Progress-(Index==1?450:700)); FVector Goal=BridgePath[0];'
            new='''    if(FVector::Dist2D(Feet,FarBankFeet)<=55 && Player->GetVelocity().Size()<2) bBridgeFarBankSettling=true;
    const double Gap=700-450;
    if(bBridgeFarBankSettling && (BridgePath.Num()<2 || BridgePath.Last().X<5655 || BridgePath[BridgePath.Num()-2].X<5655 || BridgeArcs.Last()-BridgeArcs[BridgeArcs.Num()-2]<2*Gap+55))
    { Fail(TEXT("Far-bank staging lane differs from the validated route.")); return true; }
    const double Wanted=bBridgeFarBankSettling?BridgeArcs.Last()-Index*Gap:FMath::Max(0.0,Progress-(Index==1?450:700));
    FVector Goal=BridgePath[0];'''
            text=replace_once(text,old,new)
            text=replace_once(text,'bool AParisBridgeMission::BuildBridgePath(FString& Error)',(Path(__file__).parent/'AgentFeetPlan.inc').read_text()+'\nbool AParisBridgeMission::BuildBridgePath(FString& Error)')
        target.write_text(text);changes.append(dict(path=str(target.relative_to(out)),prior_native_sha256=before,candidate_sha256=digest(target)))
    record.write_text(json.dumps(dict(scope='PRIVATE G1-only one native plan start-frame correction and measured far-bank settling; original assets/other BT topology/weapon logic preserved',query_receipt_sha256=digest(proof),changes=changes),indent=2)+'\n')
    print(json.dumps({'agent_candidate':a.identity,'changed_mission_files':len(changes)}))

if __name__=='__main__':main()
