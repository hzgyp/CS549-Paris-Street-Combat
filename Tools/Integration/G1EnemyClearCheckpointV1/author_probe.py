"""Install finite isolated admission scenarios; do not invoke old synchronous checkpoint probe."""
from prepare import SOURCE,ROOT
def main():
 p=SOURCE/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisInteractionProbe.cpp'
 s=p.read_text(encoding='utf-8-sig')
 s=s.replace('#include "UObject/UnrealType.h"','#include "UObject/UnrealType.h"\n#include "UObject/StructOnScope.h"\n#include "EngineUtils.h"\n#include "Components/CapsuleComponent.h"\n#include "AIController.h"\n#include "BrainComponent.h"')
 marker='void Tick(UWorld* W,ELevelTick,float){';assert s.count(marker)==1
 helper='TSharedPtr<FJsonObject> ParseFixture(const FString& Text){TSharedPtr<FJsonObject> Object;auto Reader=TJsonReaderFactory<>::Create(Text);FJsonSerializer::Deserialize(Reader,Object);return Object;}\n'
 s=s.replace(marker,helper+(ROOT/'Tools/Integration/G1EnemyClearCheckpointV1/ClearanceProbe.inc').read_text(encoding='utf-8')+'\n'+marker)
 marker=' const double Age=FPlatformTime::Seconds()-Since;';assert s.count(marker)==1
 s=s.replace(marker,marker+'\n if(Mode==TEXT("enemy_clear")){ClearanceTick(W,M,PC,P,Age);return;}')
 old='check(Mode==TEXT("menu") || Mode==TEXT("checkpoint") || Mode==TEXT("restore"));';assert s.count(old)==1
 s=s.replace(old,'check(Mode==TEXT("menu") || Mode==TEXT("enemy_clear") || Mode==TEXT("restore")); /* Old synchronous/waiting checkpoint expectations are retired for this child. */')
 p.write_text(s,encoding='utf-8')
 print('Installed opt-in clear-only matrix; menu/legacy restore retained; ordinary play has no probe')
if __name__=='__main__':main()
