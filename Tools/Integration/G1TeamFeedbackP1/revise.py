"""Bounded non-reflected policy/HUD changes; keep cooked classes and transactions."""
import json, shutil
from pathlib import Path
from prepare import ROOT, OUT, SOURCE, rows, sha

def replace(s,a,b):
    assert s.count(a)==1,a[:150]
    return s.replace(a,b,1)

def main():
    private=SOURCE/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private'
    for name in ['ParisTeamP1.h','ParisTeamP1.cpp','ParisP1Probe.cpp']:
        shutil.copyfile(Path(__file__).parent/name,private/name)
    cpp=private/'ParisBridgeMission.cpp';s=cpp.read_text('utf-8-sig')
    s=replace(s,'#include "ParisMissionInteraction.h"','#include "ParisMissionInteraction.h"\n#include "ParisTeamP1.h"')
    s=replace(s,'    ParisGameplayAV::Tick(this,Roster);','    if(!Roster.IsEmpty()) ParisTeamP1::UpdatePlayerMovement(Roster[0],false);\n    ParisGameplayAV::Tick(this,Roster);')
    s=replace(s,'        if(!bRegistrySealed && !SealRegistry(Error))','        if(!bRegistrySealed && !bLoadRequested && !ParisTeamP1::ConfigureFreshLayout(this,Error)) { Fail(Error); return; }\n        if(!bRegistrySealed && !SealRegistry(Error))')
    s=replace(s,'    AActor* Gun=Cast<AActor>(Object(Original,TEXT("WeaponAppearance")));','    if(!GetWorld()->URL.HasOption(TEXT("ParisLoad"))) checkf(ParisTeamP1::ConfigureFreshLoadout(Player),TEXT("P1 fresh loadout must conserve the existing eighteen rounds"));\n    AActor* Gun=Cast<AActor>(Object(Original,TEXT("WeaponAppearance")));')
    s=replace(s,'    auto* P=Cast<ACharacter>(GetPawn());','    auto* P=Cast<ACharacter>(GetPawn());\n    ParisTeamP1::UpdatePlayerMovement(P,bGamePaused);')
    start=s.index('    // Native triangle fan is the circular clip')
    end=s.index('    Circle(CX,CY,R+2',start)
    s=s[:start]+'''    // North-up player-centred circle, clipped to the measured texture rectangle.
    const double CX=1742,CY=182,R=136;
    const FVector MapCenter=Player?Player->GetActorLocation():FVector(1912.5,-20662.5,0);
    Halo(CX,CY,R+16,R+16,.42);
    Tri(FVector2D(CX-R,CY-R),FVector2D(CX+R,CY-R),FVector2D(CX+R,CY+R),FLinearColor(0,0,0,0));
    if(MinimapTexture && MinimapTexture->GetResource())
    {
        TArray<FCanvasUVTri> Fan;Fan.Reserve(260);
        for(int32 I=0;I<128;++I)
        {
            const double A=2*PI*I/128,B=2*PI*(I+1)/128;
            const auto Poly=ParisTeamP1::ClipSurvey({FVector2D(MapCenter.X,MapCenter.Y),
                FVector2D(MapCenter.X+2500*FMath::Cos(A),MapCenter.Y-2500*FMath::Sin(A)),
                FVector2D(MapCenter.X+2500*FMath::Cos(B),MapCenter.Y-2500*FMath::Sin(B))});
            for(int32 K=1;K+1<Poly.Num();++K)
            {
                FCanvasUVTri T;const FVector World0(Poly[0],0),World1(Poly[K],0),World2(Poly[K+1],0);
                const auto P0=ParisTeamP1::RadarPoint(World0,MapCenter,CX,CY,R),P1=ParisTeamP1::RadarPoint(World1,MapCenter,CX,CY,R),P2=ParisTeamP1::RadarPoint(World2,MapCenter,CX,CY,R);
                T.V0_Pos=Pt(P0.X,P0.Y);T.V1_Pos=Pt(P1.X,P1.Y);T.V2_Pos=Pt(P2.X,P2.Y);
                T.V0_UV=ParisTeamP1::SurveyUV(World0);T.V1_UV=ParisTeamP1::SurveyUV(World1);T.V2_UV=ParisTeamP1::SurveyUV(World2);
                T.V0_Color=T.V1_Color=T.V2_Color=FLinearColor(.58f,.54f,.39f,.94f);Fan.Add(T);
            }
        }
        if(!Fan.IsEmpty()){FCanvasTriangleItem Item(Fan,MinimapTexture->GetResource());Item.BlendMode=SE_BLEND_Translucent;Canvas->DrawItem(Item);}
    }
''' + s[end:]
    s=replace(s,'    Text(TEXT("G1"),CX,CY+R+13,15,Ivory,true,60);','    const bool Unknown=MapCenter.X<2500||MapCenter.X>7500||MapCenter.Y<-22500||MapCenter.Y>-17500;\n    Text(Unknown?TEXT("25m / UNSURVEYED EDGE"):TEXT("G1 / 25m"),CX,CY+R+13,12,Ivory,true,30);')
    s=replace(s,'    auto MapPoint=[&](FVector V){return FVector2D(CX-R+V.X/10000*(2*R),CY-R+(-15000-V.Y)/10000*(2*R));};','    auto MapPoint=[&](FVector V){return ParisTeamP1::RadarPoint(V,MapCenter,CX,CY,R);};')
    a='''    for(TActorIterator<ACharacter> I(GetWorld());I;++I)
        if((I->ActorHasTag(TEXT("G1_Ally1")) || I->ActorHasTag(TEXT("G1_Ally2"))) && !Flag(*I,TEXT("IsDead"))) Dot(I->GetActorLocation(),Ally,3);'''
    b='''    auto EdgeArrow=[&](FVector2D P,FLinearColor C)
    {
        const FVector2D F=(P-FVector2D(CX,CY)).GetSafeNormal(),Side(-F.Y,F.X),Tip=FVector2D(CX,CY)+F*(R-10);
        Tri(Tip,Tip-F*10+Side*5,Tip-F*10-Side*5,C);return Tip-F*23;
    };
    for(TActorIterator<ACharacter> I(GetWorld());I;++I)
        if(I->ActorHasTag(TEXT("G1_Ally1")) || I->ActorHasTag(TEXT("G1_Ally2")))
        {
            const bool Dead=Flag(*I,TEXT("IsDead"));const auto C=Dead?Quiet:FLinearColor(.35,.95,.45,1);
            FVector2D P=MapPoint(I->GetActorLocation());const bool On=InMap(P,20);
            if(On){Diamond(P.X,P.Y,5,C);if(Dead){Line(P.X-4,P.Y-4,P.X+4,P.Y+4,Ink,2);Line(P.X-4,P.Y+4,P.X+4,P.Y-4,Ink,2);}}
            else P=EdgeArrow(P,C);
            const int32 Id=I->ActorHasTag(TEXT("G1_Ally1"))?1:2;
            Text(FString::Printf(TEXT("A%d %s"),Id,Dead?TEXT("DOWN"):*FString::Printf(TEXT("%.0fm"),FVector::Dist2D(I->GetActorLocation(),MapCenter)/100)),P.X,P.Y+7,11,C,true);
        }'''
    s=replace(s,a,b)
    s=replace(s,'    if(InMap(Goal,12)){Circle(Goal.X,Goal.Y,8,Brass,1.5);Diamond(Goal.X,Goal.Y,4,Brass);}','    if(InMap(Goal,12)){Circle(Goal.X,Goal.Y,8,Brass,1.5);Diamond(Goal.X,Goal.Y,4,Brass);}\n    else {const auto G=EdgeArrow(Goal,Brass);Text(TEXT("G1"),G.X,G.Y-10,11,Brass,true);}')
    s=replace(s,'{Line(953,540,957,540,FLinearColor(.95,.91,.75,.6));Line(963,540,967,540,FLinearColor(.95,.91,.75,.6));}',
'''{const FLinearColor Green(.25,1,.35,1);Line(944,540,954,540,Green,2);Line(966,540,976,540,Green,2);Line(960,524,960,534,Green,2);Line(960,546,960,556,Green,2);Rect(958.5,538.5,3,3,Ink);Rect(959.2,539.2,1.6,1.6,Green);}''')
    cpp.write_text(s,'utf-8')
    av=private/'ParisGameplayAV.cpp';s=av.read_text('utf-8-sig')
    a='    const FString Base=Speed>220?TEXT("step_run"):Speed<90?TEXT("step_slow"):TEXT("step_walk");'
    s=replace(s,a,'    const bool Running=Posture==0&&Flag(C,TEXT("RunHeld"))&&!Flag(C,TEXT("SlowHeld"));\n    const FString Base=Running?TEXT("step_run"):Speed<90?TEXT("step_slow"):TEXT("step_walk");')
    s=replace(s,'    Play(W,S,C,T,Cue,Posture==1?.42:Speed<90?.35:Speed>220?.80:.65);','    Play(W,S,C,T,Cue,Posture==1?.42:Speed<90?.35:Running?.80:.65);')
    av.write_text(s,'utf-8')
    # The P0 finite probe is inherited; its initial/restart expectations match P1.
    probe=private/'ParisInteractionProbe.cpp';s=probe.read_text('utf-8-sig')
    assert s.count('Number(P,TEXT("LoadedAmmo"))==2')==2
    probe.write_text(s.replace('Number(P,TEXT("LoadedAmmo"))==2','Number(P,TEXT("LoadedAmmo"))==8'),'utf-8')
    module=private/'ParisBridgeMissionV1.cpp';s=module.read_text('utf-8-sig')
    s=replace(s,'#include "ParisMissionInteraction.h"','#include "ParisMissionInteraction.h"\n#include "ParisTeamP1.h"')
    s=replace(s,'  ParisInteractionProbe::Initialize();','  ParisInteractionProbe::Initialize();\n  ParisP1Probe::Initialize();')
    s=replace(s,'ParisInteractionProbe::Shutdown();','ParisP1Probe::Shutdown();ParisInteractionProbe::Shutdown();')
    # Finite observer only; exact existing action tests retarget the selected preset.
    s=replace(s,'Peak>140&&Peak<160&&FVector::Dist2D(Feet,Start)>180','Peak>210&&Peak<230&&FVector::Dist2D(Feet,Start)>280')
    s=replace(s,'Peak>290&&Peak<310&&FVector::Dist2D(Feet,Start)>400','Peak>440&&Peak<460&&FVector::Dist2D(Feet,Start)>650')
    s=replace(s,'S->SetNumberField(TEXT("speed"),P->GetVelocity().Size2D());','S->SetNumberField(TEXT("speed"),P->GetVelocity().Size2D());\n   S->SetNumberField(TEXT("animation_rate"),P->GetMesh()->GlobalAnimRateScale);\n   TArray<TSharedPtr<FJsonValue>> Squad;for(TActorIterator<ACharacter> A(W);A;++A)if(A->ActorHasTag(TEXT("G1_Ally1"))||A->ActorHasTag(TEXT("G1_Ally2"))){auto Q=MakeShared<FJsonObject>();Q->SetStringField(TEXT("id"),A->ActorHasTag(TEXT("G1_Ally1"))?TEXT("Ally1"):TEXT("Ally2"));Q->SetStringField(TEXT("feet"),A->GetNavAgentLocation().ToString());Q->SetNumberField(TEXT("speed"),A->GetVelocity().Size2D());Q->SetBoolField(TEXT("dead"),Flag(*A,TEXT("IsDead")));Squad.Add(MakeShared<FJsonValueObject>(Q));}S->SetArrayField(TEXT("allies"),Squad);')
    module.write_text(s,'utf-8')
    (OUT/'revision.json').write_text(json.dumps(dict(status='authored_unbuilt',source_files=len(rows(SOURCE))),indent=2)+'\n','utf-8')
    print('P1 source authored; no cooked assets or reflected declarations changed')

if __name__=='__main__':main()
