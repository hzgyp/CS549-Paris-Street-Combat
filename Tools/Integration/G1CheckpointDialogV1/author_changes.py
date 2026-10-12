"""Bounded UI-only source changes against exact reviewed v9."""
from prepare import SOURCE,ROOT
B=SOURCE/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1'
def edit(rel,old,new):
    p=B/rel;s=p.read_text(encoding='utf-8-sig');assert s.count(old)==1,(rel,old[:80]);p.write_text(s.replace(old,new),encoding='utf-8')
edit('Public/ParisBridgeMission.h','    bool InteractCheckpoint();','''    bool InteractCheckpoint();
    // UI lifecycle is deliberately non-reflected; existing cooked layout stays exact.
    FString CheckpointDialogState() const { return SaveDialogState; }
    const FString& CheckpointDialogDetail() const { return SaveDialogDetail; }
    bool CheckpointDialogVisible() const { return SaveDialogState!=TEXT("None"); }
    bool CheckpointDialogLocksGameplay() const { return CheckpointDialogVisible() && SaveDialogState!=TEXT("Waiting"); }
    bool ActivateCheckpointDialog(int32 Button);
    void MarkCheckpointDialogDrawn();''')
edit('Public/ParisBridgeMission.h','    void UpdateCheckpointUI();','''    void UpdateCheckpointUI();
    void UpdateCheckpointDialog();
    void SetCheckpointDialog(const FString& State,const FString& Detail);
    FString SaveDialogState=TEXT("None"),SaveDialogDetail;
    double SaveDialogRequestedAt=0;
    uint64 SaveDialogDrawnFrame=0;
    bool bSaveDialogDrawn=false,bCheckpointSavedThisVisit=false;''')
edit('Public/ParisBridgeMission.h','    bool bMenuLoadEnabled=false,bMenuMouseObserved=false;','''    bool bMenuLoadEnabled=false,bMenuMouseObserved=false;
    bool bCheckpointInputHeld=false,bInteractionDialogMode=false;''')
edit('Private/ParisMissionInteraction.h','}\n}\n\nnamespace ParisInteractionProbe','''}
inline int32 CheckpointHit(FVector2D Screen,FIntPoint Size,bool Failure) {
    if(Size.X<=0 || Size.Y<=0)return INDEX_NONE;
    const double S=FMath::Min(Size.X/1920.,Size.Y/1080.);
    const FVector2D P=(Screen-FVector2D((Size.X-1920*S)*.5,(Size.Y-1080*S)*.5))/S;
    if(P.Y<622 || P.Y>666)return INDEX_NONE;
    if(!Failure)return P.X>=810 && P.X<=1110?0:INDEX_NONE;
    if(P.X>=670 && P.X<=930)return 0;
    return P.X>=990 && P.X<=1250?1:INDEX_NONE;
}
}

namespace ParisInteractionProbe''')
edit('Private/ParisBridgeMission.cpp','''    if(!CheckpointUnlocked()) { CheckpointPromptVisible=false; return; }''','''    UpdateCheckpointDialog();
    if(!CheckpointUnlocked()) { CheckpointPromptVisible=false; return; }''')
edit('Private/ParisBridgeMission.cpp','''    if(!Inside) { CheckpointPromptVisible=false; bCheckpointDismissed=false; }
    else if(!bCheckpointWasInside && !bCheckpointDismissed)''','''    if(!Inside) { CheckpointPromptVisible=false; bCheckpointDismissed=false; bCheckpointSavedThisVisit=false; }
    else if(!bCheckpointWasInside && !bCheckpointDismissed && !CheckpointDialogVisible() && !bCheckpointSavedThisVisit)''')
edit('Private/ParisBridgeMission.cpp','''    ++InteractionRevision;
    if(!InsideCheckpoint()) { Feedback=CheckpointSaveBlockReason(); return false; }
    CheckpointPromptVisible=true; bCheckpointDismissed=false; return true;''','''    ++InteractionRevision;
    if(CheckpointDialogVisible() || (bCheckpointSavedThisVisit && InsideCheckpoint())) return false;
    if(!InsideCheckpoint()) { Feedback=CheckpointSaveBlockReason(); return false; }
    CheckpointPromptVisible=true; bCheckpointDismissed=false; return true;''')
edit('Private/ParisBridgeMission.cpp','''    TGuardValue<bool> Permit(bConfirmedSaveRequest,true);
    if(!SaveCheckpoint()) return false;
    CheckpointPromptVisible=false; bCheckpointDismissed=true;
    UE_LOG(LogTemp,Display,TEXT("PARIS_UX_CHECKPOINT_CONFIRMED serial=%d"),SaveSerial); return true;''','''    if(CheckpointDialogVisible() || bCheckpointSavedThisVisit) return false;
    CheckpointPromptVisible=false; bCheckpointDismissed=true;
    SaveDialogRequestedAt=GetWorld()->GetTimeSeconds();
    const FString Reason=CheckpointSaveBlockReason();
    SetCheckpointDialog(Reason.IsEmpty()?TEXT("Saving"):TEXT("Waiting"),Reason);
    return true; // Accepted explicit request; only original readback can report success.''')
# Prevent the ephemeral feedback strip from duplicating modal save results.
edit('Private/ParisBridgeMission.cpp','''    if(!LastFeedback.IsEmpty() && (Now-FeedbackAt<5 || ProneNotice || M->Phase==TEXT("Error") || M->Phase==TEXT("Lost")))''','''    if(!M->CheckpointDialogVisible() && !LastFeedback.StartsWith(TEXT("Mission saved")) && !LastFeedback.IsEmpty() && (Now-FeedbackAt<5 || ProneNotice || M->Phase==TEXT("Error") || M->Phase==TEXT("Lost")))''')
edit('Private/ParisBridgeMission.cpp','''    if(M->CheckpointUnlocked() && !M->InsideCheckpoint())''','''    if(M->CheckpointUnlocked() && !M->InsideCheckpoint())''')
# Draw last, using exactly the same reference coordinates as the native hit helper.
edit('Private/ParisBridgeMission.cpp','''}

namespace ParisPronePrediction''','''    if(M->CheckpointDialogVisible())
    {
        const FString State=M->CheckpointDialogState();
        const bool Success=State==TEXT("Succeeded"),Failure=State==TEXT("Failed"),Waiting=State==TEXT("Waiting");
        DrawRect(FLinearColor(0,0,0,.30),0,0,Canvas->SizeX,Canvas->SizeY);
        Rect(600,374,720,332,FLinearColor(.016,.025,.021,.97));
        Line(600,374,1320,374,Brass,2);Line(600,706,1320,706,Brass,2);
        const FLinearColor Accent=Success?Ally:Failure?Danger:Brass;
        Circle(960,426,23,Accent,2);
        if(Success){Line(947,426,957,436,Accent,3);Line(957,436,974,417,Accent,3);}
        else Text(Failure?TEXT("!"):TEXT("..."),960,414,20,Accent,true);
        Text(Success?TEXT("CHECKPOINT SAVED"):Failure?TEXT("CHECKPOINT NOT SAVED"):Waiting?TEXT("WAITING TO SAVE"):TEXT("SAVING CHECKPOINT"),960,472,25,Ivory,true,30);
        FString Detail=Success?TEXT("Your progress has been written and verified."):Failure?M->CheckpointDialogDetail():Waiting?M->CheckpointDialogDetail():TEXT("Writing and checking your saved progress...");
        TArray<FString> Words;Detail.ParseIntoArrayWS(Words);TArray<FString> Lines;FString Current;
        for(const auto& Word:Words){if(Current.Len()+Word.Len()+1>65){Lines.Add(Current);Current.Empty();}Current+=(Current.IsEmpty()?TEXT(""):TEXT(" "))+Word;}
        if(!Current.IsEmpty())Lines.Add(Current);
        for(int32 I=0;I<FMath::Min(3,Lines.Num());++I)Text(Lines[I],960,521+I*22,14,Quiet,true);
        if(Success)Text(FString::Printf(TEXT("SAVED REVISION %d"),M->SaveSerial),960,584,12,Brass,true);
        if(Waiting)Text(TEXT("Stop moving and stand up. ESC cancels this request."),960,591,12,Quiet,true);
        if(State!=TEXT("Saving"))
        {
            const int32 Count=Failure?2:1;
            for(int32 I=0;I<Count;++I){const double X=Failure?(I==0?670:990):810,W=Failure?260:300;
                Rect(X,622,W,44,FLinearColor(.075,.085,.055,1));Line(X,622,X+W,622,Brass,1.5);
                Text(Success?TEXT("OK"):Failure?(I==0?TEXT("RETRY"):TEXT("CANCEL")):TEXT("CANCEL"),X+W*.5,634,16,Ivory,true);}
            Text(Failure?TEXT("ENTER / E RETRY    ESC CANCEL"):Success?TEXT("ENTER / ESC TO CONTINUE"):TEXT("ESC TO CANCEL"),960,681,11,Quiet,true);
        }
        M->MarkCheckpointDialogDrawn();
    }
}

namespace ParisPronePrediction''')
edit('Private/ParisMissionInteraction.cpp','''    ++InteractionRevision;
    if(!RequestCheckpointPrompt())return false;''','''    if(CheckpointDialogVisible())return false;
    ++InteractionRevision;
    if(!RequestCheckpointPrompt())return false;''')
edit('Private/ParisMissionInteraction.cpp','''    const bool Menu=InteractionMenuVisible();
    if(!bInteractionModeInitialized || Menu!=bInteractionMenuMode)''','''    const bool Menu=InteractionMenuVisible(),Dialog=M->CheckpointDialogVisible();
    const bool Lock=M->CheckpointDialogLocksGameplay();
    if(Lock!=bCheckpointInputHeld){SetIgnoreMoveInput(Lock);SetIgnoreLookInput(Lock);bCheckpointInputHeld=Lock;}
    if(!bInteractionModeInitialized || Menu!=bInteractionMenuMode || Dialog!=bInteractionDialogMode)''')
edit('Private/ParisMissionInteraction.cpp','''        bInteractionModeInitialized=true;bInteractionMenuMode=Menu;
        bShowMouseCursor=Menu;
        if(Menu)''','''        bInteractionModeInitialized=true;bInteractionMenuMode=Menu;bInteractionDialogMode=Dialog;
        bShowMouseCursor=Menu || Dialog;
        if(Menu || Dialog)''')
edit('Private/ParisMissionInteraction.cpp','''    if(InteractionMenuVisible()) {
        if(Params.Key==EKeys::LeftMouseButton)''','''    if(M->CheckpointDialogVisible()) {
        if(Params.Key==EKeys::LeftMouseButton) {
            if(Params.Event==IE_Pressed){bSwallowMenuClick=true;float X=0,Y=0;int32 W=0,H=0;GetViewportSize(W,H);
                if(GetMousePosition(X,Y)){const int32 Button=ParisMissionInteraction::CheckpointHit(FVector2D(X,Y),FIntPoint(W,H),M->CheckpointDialogState()==TEXT("Failed"));
                    if(Button!=INDEX_NONE)M->ActivateCheckpointDialog(Button);}}
            return true;
        }
        if(Params.Event==IE_Pressed){
            if(Params.Key==EKeys::Escape){M->ActivateCheckpointDialog(M->CheckpointDialogState()==TEXT("Failed")?1:0);return true;}
            if(Params.Key==EKeys::E || Params.Key==EKeys::Enter){if(M->CheckpointDialogState()==TEXT("Succeeded") || M->CheckpointDialogState()==TEXT("Failed"))M->ActivateCheckpointDialog(0);return true;}
        }
        // Always deliver releases to original bindings. Waiting permits standing/stopping.
        if(M->CheckpointDialogLocksGameplay() && Params.Event!=IE_Released)return true;
    }
    if(InteractionMenuVisible()) {
        if(Params.Key==EKeys::LeftMouseButton)''')
p=B/'Private/ParisMissionInteraction.cpp'
p.write_text(p.read_text(encoding='utf-8')+'''
void AParisBridgeMission::SetCheckpointDialog(const FString& State,const FString& Detail) {
    SaveDialogState=State;SaveDialogDetail=Detail;bSaveDialogDrawn=false;SaveDialogDrawnFrame=0;++InteractionRevision;
    UE_LOG(LogTemp,Display,TEXT("PARIS_CHECKPOINT_DIALOG state=%s serial=%d reason=%s"),*State,SaveSerial,*Detail);
}
void AParisBridgeMission::MarkCheckpointDialogDrawn() {
    if(!bSaveDialogDrawn){bSaveDialogDrawn=true;SaveDialogDrawnFrame=GFrameCounter;
        UE_LOG(LogTemp,Display,TEXT("PARIS_CHECKPOINT_DIALOG_DRAW state=%s frame=%llu"),*SaveDialogState,SaveDialogDrawnFrame);}
}
void AParisBridgeMission::UpdateCheckpointDialog() {
    if(SaveDialogState!=TEXT("Waiting") && SaveDialogState!=TEXT("Saving"))return;
    if(!InsideCheckpoint()){
        SetCheckpointDialog(TEXT("None"),FString());Feedback=TEXT("Save cancelled: you left the checkpoint circle.");return;
    }
    const FString Reason=CheckpointSaveBlockReason();
    if(!Reason.IsEmpty()){
        if(GetWorld()->GetTimeSeconds()-SaveDialogRequestedAt>30){SetCheckpointDialog(TEXT("Failed"),TEXT("Save request timed out. ")+Reason);return;}
        if(SaveDialogState!=TEXT("Waiting") || SaveDialogDetail!=Reason)SetCheckpointDialog(TEXT("Waiting"),Reason);
        return;
    }
    if(SaveDialogState==TEXT("Waiting")){SetCheckpointDialog(TEXT("Saving"),FString());return;}
    if(!bSaveDialogDrawn || GFrameCounter<=SaveDialogDrawnFrame+1)return;
    UE_LOG(LogTemp,Display,TEXT("PARIS_CHECKPOINT_DIALOG_WRITE frame=%llu after_draw=%llu"),GFrameCounter,SaveDialogDrawnFrame);
    TGuardValue<bool> Permit(bConfirmedSaveRequest,true);
    if(SaveCheckpoint()){
        CheckpointPromptVisible=false;bCheckpointDismissed=true;bCheckpointSavedThisVisit=true;
        SetCheckpointDialog(TEXT("Succeeded"),FString());
    } else SetCheckpointDialog(TEXT("Failed"),Feedback);
}
bool AParisBridgeMission::ActivateCheckpointDialog(int32 Button) {
    if(SaveDialogState==TEXT("Saving") || !CheckpointDialogVisible())return false;
    if(SaveDialogState==TEXT("Failed") && Button==0){
        SetCheckpointDialog(TEXT("None"),FString());CheckpointPromptVisible=InsideCheckpoint();return ConfirmCheckpoint();
    }
    if(Button<0 || Button>(SaveDialogState==TEXT("Failed")?1:0))return false;
    const bool Saved=SaveDialogState==TEXT("Succeeded");
    SetCheckpointDialog(TEXT("None"),FString());CheckpointPromptVisible=false;bCheckpointDismissed=true;
    if(!Saved)Feedback=TEXT("Checkpoint not saved. Press E inside the circle when ready.");
    return true;
}
''',encoding='utf-8')
# Dedicated shell tools reused only after replacing their task roots/identities.
lane=ROOT/'Tools/Integration/G1CheckpointDialogV1'
for name in ['build.ps1','launch_check.ps1','stage_runtime.py']:
    s=(ROOT/'Tools/Integration/G1TeamCompletionV1'/name).read_text(encoding='utf-8-sig')
    s=s.replace('g1-team-completion-20261010','g1-checkpoint-dialog-20261010').replace('Playtest-G1-Completion-','Playtest-G1-Checkpoint-')
    s=s.replace("frozen['p1_game_sha256']","frozen['parent_game_sha256']")
    s=s.replace('G1TeamP1v920261010','G1Completionv920261010').replace("user='G1Completion'","user='G1Checkpoint'")
    (lane/name).write_text(s,encoding='utf-8')
print('UI changes authored; original transactions must be verified before build')
