"""Exact V13-only private source transformations for the human playtest revision."""
from pathlib import Path

HERE=Path(__file__).resolve().parent

def replace_once(text,old,new):
    assert text.count(old)==1,old[:100]
    return text.replace(old,new,1)

def revise(project):
    base=project/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1'
    header=base/'Public/ParisBridgeMission.h'
    h=header.read_text(encoding='utf-8')
    h=replace_once(h,'class ACharacter;','class ACharacter;\nclass UTexture2D;')
    h=replace_once(h,'    static AParisBridgeMission* Find(const UObject* Context);','''    UFUNCTION(BlueprintPure, Category="G1 Checkpoint") bool CheckpointUnlocked() const;
    UFUNCTION(BlueprintPure, Category="G1 Checkpoint") bool InsideCheckpoint() const;
    UFUNCTION(BlueprintCallable, Category="G1 Checkpoint") bool RequestCheckpointPrompt();
    UFUNCTION(BlueprintCallable, Category="G1 Checkpoint") bool ConfirmCheckpoint();
    UFUNCTION(BlueprintCallable, Category="G1 Checkpoint") void DismissCheckpointPrompt();
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="G1 Checkpoint") bool CheckpointPromptVisible=false;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="G1 Checkpoint") double CheckpointRadius=180;
    static AParisBridgeMission* Find(const UObject* Context);''')
    h=replace_once(h,'    double SafeSeconds = 0;','''    double SafeSeconds = 0;
    bool bCheckpointWasInside=false;
    bool bCheckpointDismissed=false;
    bool bConfirmedSaveRequest=false;
    void UpdateCheckpointUI();''')
    h=replace_once(h,'    virtual void DrawHUD() override;','''    virtual void DrawHUD() override;
private:
    UPROPERTY(Transient) TObjectPtr<UTexture2D> MinimapTexture;
    bool bMapLoadAttempted=false;
    bool bLegacyWidgetRemoved=false;
    double NextMarkerRefresh=0;
    TArray<FVector> CachedEnemyLocations;''')
    h=replace_once(h,'    AParisBridgeGameMode();','    AParisBridgeGameMode();\n    virtual void StartPlay() override;')
    header.write_text(h,encoding='utf-8')
    cpp=base/'Private/ParisBridgeMission.cpp'
    s=cpp.read_text(encoding='utf-8')
    s=replace_once(s,'#include <limits>','''#include <limits>
#include "Blueprint/UserWidget.h"
#include "Blueprint/WidgetBlueprintLibrary.h"
#include "Camera/CameraComponent.h"
#include "DrawDebugHelpers.h"
#include "Engine/Texture2D.h"
#include "ImageUtils.h"
#include "HAL/PlatformProcess.h"
#include "Misc/Paths.h"''')
    s=replace_once(s,'ConfigFingerprint+=TEXT("_BridgeConstraintV2FeetPlan");','ConfigFingerprint+=TEXT("_BridgeConstraintV2FeetPlan_HumanPlaytestUXV5");')
    s=replace_once(s,'SlotPrefix=TEXT("ParisG1V4");','SlotPrefix=TEXT("ParisG1V5");')
    s=replace_once(s,'    const double Wanted=bBridgeFarBankSettling?BridgeArcs.Last()-Index*Gap:FMath::Max(0.0,Progress-(Index==1?450:700));', '''    const double Lag=Index==1?450.0:700.0;
    if(!bBridgeFarBankSettling && Progress<Lag) { Invoke(Controller,TEXT("PC_PolicyHold")); return true; }
    const double Wanted=bBridgeFarBankSettling?BridgeArcs.Last()-Index*Gap:FMath::Max(0.0,Progress-Lag);''')
    s=replace_once(s,'    if(!AllowsPlay()) return;','''    if(!AllowsPlay())
    {
        if(Phase==TEXT("Won")) { UpdateCheckpointUI(); FString Reason; SafeSeconds=IsSafeBoundary(Reason)?SafeSeconds+DeltaSeconds:0; }
        return;
    }''')
    s=replace_once(s,'Feedback=TEXT("G1 bridgehead captured. F5 saves the result; Ctrl+R restarts."); GateBrains(false);', '''Feedback=TEXT("G1 secured. Enter the green checkpoint circle to save."); GateBrains(false);
      if(auto* PC=UGameplayStatics::GetPlayerController(this,0)) { PC->ResetIgnoreMoveInput(); PC->ResetIgnoreLookInput(); }''')
    s=replace_once(s,'    FString Reason; SafeSeconds=IsSafeBoundary(Reason) ? SafeSeconds+DeltaSeconds : 0;','    UpdateCheckpointUI();\n    FString Reason; SafeSeconds=IsSafeBoundary(Reason) ? SafeSeconds+DeltaSeconds : 0;')
    s=replace_once(s,'bool AParisBridgeMission::SaveCheckpoint()\n{','''bool AParisBridgeMission::SaveCheckpoint()
{
    if(!bConfirmedSaveRequest || !CheckpointUnlocked() || !InsideCheckpoint() || Phase!=TEXT("Won"))
    { Feedback=TEXT("Enter the secured checkpoint circle and confirm with E."); return false; }
    if(!Roster.IsEmpty() && (Roster[0]->bIsCrouched || Number(Roster[0],TEXT("DesiredPosture"))!=0))
    { Feedback=TEXT("Stand up before saving this checkpoint."); return false; }''')
    s=replace_once(s,'    GateBrains(AllowsPlay());','''    GateBrains(AllowsPlay());
    if(Phase==TEXT("Won")) if(auto* PC=UGameplayStatics::GetPlayerController(this,0))
    { PC->ResetIgnoreMoveInput(); PC->ResetIgnoreLookInput(); }''')
    s=replace_once(s,'if(Params.Key==EKeys::F5) { M->SaveCheckpoint(); return true; }','''if(Params.Key==EKeys::F5) { M->RequestCheckpointPrompt(); return true; }
            if(Params.Key==EKeys::E && M->CheckpointPromptVisible) { M->ConfirmCheckpoint(); return true; }
            if(Params.Key==EKeys::Escape && M->CheckpointPromptVisible) { M->DismissCheckpointPrompt(); return true; }
            if(Params.Key==EKeys::F6) { M->RestartMission(); return true; }''')
    # Ctrl is now an ordinary posture key; Ctrl+R must never restart the map.
    s=replace_once(s,'            if(Params.Key==EKeys::R && bMissionControlHeld) { M->RestartMission(); return true; }\n','')
    s=s.replace('Ctrl+R','F6')
    s=replace_once(s,'if(!M->AllowsPlay() && Params.Key!=EKeys::Tilde && Params.Key!=EKeys::Escape)', 'if(!M->AllowsPlay() && M->Phase!=TEXT("Won") && Params.Key!=EKeys::Tilde && Params.Key!=EKeys::Escape)')
    s=replace_once(s,'M->SaveCheckpoint(); }','M->RequestCheckpointPrompt(); }')
    start=s.index('void AParisBridgeHUD::DrawHUD()')
    s=s[:start]+(HERE/'RevisionRuntime.inc').read_text(encoding='utf-8')+'\n'+(HERE/'RevisionHUD.inc').read_text(encoding='utf-8')
    cpp.write_text(s,encoding='utf-8')
    build=base/'ParisBridgeMissionV1.Build.cs'
    b=build.read_text(encoding='utf-8')
    b=replace_once(b,'"AIModule",','"UMG", "ImageWrapper", "AIModule",')
    build.write_text(b,encoding='utf-8')
    # Do not carry stopped internal recording experiments into the new product entry.
    # This finite observer is inert without explicit flags. No stopped recorder
    # or runtime pose/resource driver is carried into the new entry.
    (base/'Private/ParisBridgeMissionV1.cpp').write_text('#include "Modules/ModuleManager.h"\n'+(HERE/'RevisionTest.inc').read_text(encoding='utf-8'),encoding='utf-8')
