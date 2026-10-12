from pathlib import Path
p=Path(__file__).parent/'ParisTacticalEquipment.cpp'
s=p.read_bytes().replace(b'#include "ParisTacticalEquipment.h"',b'#include "ParisTacticalEquipment.h"\r\n#include "RenderTimer.h"\r\n#include "RHI.h"')
p.write_bytes(s)
p=Path(__file__).parent/'ParisEquipmentChecks.inl';s=p.read_bytes()
# Define diagnostics after their serialization prerequisite.
start=s.index(b'void SmokeReceipt(');end=s.index(b'\r\n',start)+2
receipt=s[start:end];s=s[:start]+s[end:]
mark=b'bool Expect('
s=s.replace(mark,receipt+b'TArray<TSharedPtr<FJsonValue>> PerfSamples;double PerfLastWall=0;\r\n'+mark,1)
marker=b'    if(CheckMode==TEXT("restore_equipment")'
perf=b'''    if(CheckMode==TEXT("performance")){
        if(CheckStep==0){if(M->Phase!=TEXT("Ready"))return;auto* D=Display(W,P);if(!D||!Flag(D,TEXT("Initialized")))return;M->StartMission();CheckClock=0;CheckStep=120;PerfLastWall=FPlatformTime::Seconds();return;}
        const double Now=FPlatformTime::Seconds(),FrameMs=(Now-PerfLastWall)*1000;PerfLastWall=Now;
        if(CheckClock>1){auto R=MakeShared<FJsonObject>();R->SetNumberField(TEXT("seconds"),CheckClock);R->SetNumberField(TEXT("frame_ms"),FrameMs);R->SetNumberField(TEXT("game_ms"),FPlatformTime::ToMilliseconds(GGameThreadTime));R->SetNumberField(TEXT("draw_ms"),FPlatformTime::ToMilliseconds(GRenderThreadTime));R->SetNumberField(TEXT("gpu_ms"),FPlatformTime::ToMilliseconds(RHIGetGPUFrameCycles(0)));R->SetNumberField(TEXT("actors"),Combatants(W).Num());R->SetNumberField(TEXT("clouds"),S.Clouds.Num());R->SetNumberField(TEXT("balls"),S.Balls.Num());R->SetStringField(TEXT("phase"),M->Phase.ToString());PerfSamples.Add(MakeShared<FJsonValueObject>(R));}
        if(CheckStep==120&&CheckClock>2){PC->SetControlRotation(FRotator(20,0,0));Tap(PC,EKeys::Q);CheckStep=121;}
        if(CheckStep==121&&CheckClock>6){Tap(PC,EKeys::G);CheckStep=122;}
        if(CheckClock>16){auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("scope"),TEXT("Current six actors; normal AI; real G/Q input; no relocation/hold/additional NPCs; 1080p quality2 capped60; Editor open"));O->SetArrayField(TEXT("samples"),PerfSamples);FFileHelper::SaveStringToFile(JsonText(O),*(CheckOut/TEXT("PERFORMANCE.json")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);FinishCheck(W,PerfSamples.Num()>100&&S.SmokeThrown==1&&S.FragThrown==1,TEXT("Current roster combined equipment performance recorded; not large population stress acceptance"));}return;
    }
'''
assert s.count(marker)==1;s=s.replace(marker,perf+marker);p.write_bytes(s)
print('Read-only opt-in six-actor performance check authored; serializer prerequisite corrected')
