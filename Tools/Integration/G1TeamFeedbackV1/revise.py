"""Bounded interaction changes; prove protected algorithms remain byte-identical."""
import json, shutil, hashlib
from pathlib import Path
from prepare import ROOT, OUT, SOURCE, sha, rows

def one(s,a,b):
    assert s.count(a)==1,a[:100]
    return s.replace(a,b,1)

def main():
    frozen=json.loads((OUT/'freeze.json').read_text('utf-8'))
    for r in frozen['parent_files']: assert sha(SOURCE/r['path'])==r['sha256']
    plugin=SOURCE/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1'
    header=plugin/'Public/ParisBridgeMission.h';s=header.read_text('utf-8-sig')
    s=one(s,'    static AParisBridgeMission* Find', '''    bool InteractCheckpoint();
    bool CanLoadCheckpoint(FString& Reason) const;
    FString CheckpointSaveBlockReason() const;
    // Runtime UI feedback revision: keep the existing cooked property schema.
    int32 InteractionRevision=0;
    static AParisBridgeMission* Find''')
    s=one(s,'    virtual bool InputKey(const FInputKeyEventArgs& Params) override;', '''    virtual bool InputKey(const FInputKeyEventArgs& Params) override;
    virtual void PlayerTick(float DeltaTime) override;
    bool InteractionMenuVisible() const;
    int32 InteractionMenuSelection() const { return MenuSelection; }
    bool MenuActionEnabled(int32 Index) const { return Index>=0 && Index<3 && (Index!=1 || bMenuLoadEnabled); }
    bool SelectMenuAtScreen(FVector2D Mouse,FIntPoint Size);
    bool ActivateInteractionMenu();
    void RefreshInteractionMenu();''')
    s=one(s,'    bool bMissionControlHeld = false;', '''    bool bMissionControlHeld = false;
    bool HandleInteractionInput(const FInputKeyEventArgs& Params);
    bool bInteractionModeInitialized=false,bInteractionMenuMode=false,bSwallowMenuClick=false;
    bool bMenuLoadEnabled=false,bMenuMouseObserved=false;
    int32 MenuSelection=0;
    double NextMenuCheck=0;
    FVector2D LastMenuMouse=FVector2D::ZeroVector;
    FString MenuLoadReason;''')
    header.write_text(s,'utf-8')
    cpp=plugin/'Private/ParisBridgeMission.cpp';before=cpp.read_text('utf-8-sig');s=before
    s=one(s,'#include "ParisBridgeMission.h"','#include "ParisBridgeMission.h"\n#include "ParisMissionInteraction.h"')
    s=one(s,'''        if(Name(C,TEXT("ActionState"))!=TEXT("Ready") || !C->GetCharacterMovement()->IsMovingOnGround() || C->GetVelocity().Size()>2)
        { Reason=TEXT("Wait until everyone is grounded, still, and finished acting."); return false; }''', '''        if(!C->GetCharacterMovement()->IsMovingOnGround())
        { Reason=StableIds[I]+TEXT(": wait until grounded."); return false; }
        if(Name(C,TEXT("ActionState"))!=TEXT("Ready"))
        { Reason=StableIds[I]+TEXT(": wait for the current action to finish."); return false; }
        if(C->GetVelocity().Size()>2)
        { Reason=StableIds[I]+TEXT(": stop moving before saving."); return false; }''')
    s=one(s,'{ Reason=TEXT("An NPC combat transaction is active."); return false; }',
          '{ Reason=StableIds[I]+TEXT(": wait for the combat transaction to finish."); return false; }')
    s=one(s,'''bool AParisBridgePlayerController::InputKey(const FInputKeyEventArgs& Params)
{
    AParisBridgeMission* M''','''bool AParisBridgePlayerController::InputKey(const FInputKeyEventArgs& Params)
{
    if(HandleInteractionInput(Params))return true;
    AParisBridgeMission* M''')
    s=one(s,'''            if(Params.Key==EKeys::E && M->CheckpointPromptVisible) { M->ConfirmCheckpoint(); return true; }
''','')
    s=one(s,'''    if(!InsideCheckpoint()) { Feedback=TEXT("Clear all three guards, then enter the gold checkpoint circle."); return false; }
    CheckpointPromptVisible=true;''','''    ++InteractionRevision;
    if(!InsideCheckpoint()) { Feedback=CheckpointSaveBlockReason(); return false; }
    CheckpointPromptVisible=true;''')
    s=one(s,'''    CheckpointPromptVisible=false; bCheckpointDismissed=true;
    Feedback=TEXT("Checkpoint not saved. Leave and re-enter when ready.");''','''    ++InteractionRevision;
    CheckpointPromptVisible=false; bCheckpointDismissed=true;
    Feedback=TEXT("Checkpoint not saved. Press E inside the circle when ready.");''')
    s=one(s,'''    if(!CheckpointPromptVisible || !InsideCheckpoint()) return false;
    TGuardValue<bool> Permit''','''    ++InteractionRevision;
    if(!CheckpointPromptVisible || !InsideCheckpoint()) { Feedback=CheckpointSaveBlockReason(); return false; }
    TGuardValue<bool> Permit''')
    old='''    if(M->Phase==TEXT("Ready"))
    {
        Halo(960,774,240,80,.34);
        Text(TEXT("G1 BRIDGEHEAD"),960,740,19,Ivory,true,100);
        Key(TEXT("ENTER"),811,792,80);Text(TEXT("BEGIN MISSION"),910,797,15,Ivory,false,50);
    }'''
    new='''    auto* MenuPC=Cast<AParisBridgePlayerController>(PlayerOwner);
    const bool MenuVisible=MenuPC && MenuPC->InteractionMenuVisible();
    if(MenuVisible)
    {
        Halo(960,837,380,190,.80);
        Text(M->Phase==TEXT("Ready")?TEXT("G1 BRIDGEHEAD"):TEXT("MISSION ENDED"),960,692,24,Ivory,true,100);
        const FString Labels[]={M->Phase==TEXT("Ready")?TEXT("BEGIN MISSION"):TEXT("RESTART MISSION"),TEXT("LOAD CHECKPOINT"),TEXT("EXIT GAME")};
        for(int32 I=0;I<3;++I)
        {
            const float Y=750+I*58;const bool Selected=MenuPC->InteractionMenuSelection()==I,Enabled=MenuPC->MenuActionEnabled(I);
            Rect(750,Y,420,44,FLinearColor(.014,.020,.018,.90));
            if(Selected){Line(750,Y,1170,Y,Brass,1.5);Line(750,Y+44,1170,Y+44,Brass,1.5);}
            Text(Labels[I],960,Y+12,18,Enabled?(Selected?Ivory:Brass):Quiet,true,25);
            if(!Enabled)Text(TEXT("NO VALID SAVE"),1190,Y+15,11,Quiet,false);
        }
        Text(TEXT("MOUSE / UP / DOWN / TAB    ENTER TO SELECT"),960,941,12,Quiet,true);
    }
    if(M->CheckpointPromptVisible)
    {
        const FString Block=M->CheckpointSaveBlockReason();
        Halo(960,906,440,28,.65);
        Text((Block.IsEmpty()?TEXT("READY TO SAVE - PRESS E"):Block.ToUpper()).Left(100),960,894,13,Block.IsEmpty()?Ivory:Brass,true);
    }'''
    s=one(s,old,new)
    s=one(s,'    static FString LastFeedback;static double FeedbackAt=0;',
          '    static FString LastFeedback;static double FeedbackAt=0;static int32 LastRevision=-1;')
    s=one(s,'if(LastFeedback!=M->Feedback){LastFeedback=M->Feedback;FeedbackAt=Now;}',
          'if(LastFeedback!=M->Feedback || LastRevision!=M->InteractionRevision){LastFeedback=M->Feedback;LastRevision=M->InteractionRevision;FeedbackAt=Now;}')
    s=one(s,'!LastFeedback.IsEmpty() && M->Phase!=TEXT("Ready") &&', '!LastFeedback.IsEmpty() &&')
    s=one(s,'''if(!Routine) {Halo(960,916,370,29,.30);Text(LastFeedback.Left(90),960,906,12,M->Phase==TEXT("Error")?Danger:Quiet,true);}''',
          '''if(!Routine) {const double Y=MenuVisible?978:M->CheckpointPromptVisible?943:916;Halo(960,Y,420,25,.55);Text(LastFeedback.Left(100),960,Y-10,13,M->Phase==TEXT("Error")?Danger:Ivory,true);}''')
    # The save journal, resource capture/validation, weapon/lifecycle/restore and navigation algorithms stay exact.
    checks=[]
    for a,b in [('bool AParisBridgeMission::SaveCheckpoint()','bool AParisBridgeMission::ApplySnapshot('),
                ('bool AParisBridgeMission::ValidateSnapshot(','bool AParisBridgeMission::SaveCheckpoint()'),
                ('bool AParisBridgeMission::ApplySnapshot(','bool AParisBridgePlayerController::InputKey('),
                ('bool AParisBridgeMission::StartMission()','bool AParisBridgeMission::IsSafeBoundary(')]:
        assert s[s.index(a):s.index(b)]==before[before.index(a):before.index(b)],a
        checks.append(a)
    cpp.write_text(s,'utf-8')
    for name in ['ParisMissionInteraction.h','ParisMissionInteraction.cpp']:
        shutil.copyfile(Path(__file__).parent/name,plugin/'Private'/name)
    files=rows(SOURCE)
    changed=[r['path'] for r in frozen['parent_files'] if sha(SOURCE/r['path'])!=r['sha256']]
    assert changed==['Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisBridgeMission.cpp',
                     'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Public/ParisBridgeMission.h']
    manifest=dict(format='paris-source-snapshot-v1',scope='Bounded menu/checkpoint interaction child; source unselected pending review',files=files)
    (SOURCE.parent/'SOURCE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n','utf-8')
    (OUT/'revision.json').write_text(json.dumps(dict(status='revised_not_built',changed=changed,added=2,files=files,
          protected_algorithm_checks=checks),indent=2)+'\n','utf-8')
    print(json.dumps(dict(status='revised_not_built',source_files=len(files),changed=changed,protected_blocks_exact=len(checks))))

if __name__=='__main__':main()
