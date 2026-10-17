// Opt-in diagnostics use original input/physics. Combat-clear fixtures are declared.
namespace {
int CopyPhase=0;bool CopyBefore=false;
FString TestMode,TestOut;bool TestInitialized=false,TestDone=false,TestAction=false,TestHeldW=false,TestHeldShift=false,TestPracticeTaken=false,TestCancelChecked=false,TestReplayChecked=false,TestLoadSent=false,TestSupplyAimed=false;
int TestLast=-1,TestDialogPhase=0;double TestBegin=0,TestAt=0,TestNext=0,TestTraceAt=0;FVector TestPrevious=FVector::ZeroVector;double TestTravel=0;
TArray<TSharedPtr<FJsonValue>> TestChecks;
int TestCrawlPhase=0;FVector TestCrawlOrigin;double TestCrawlYaw=0;bool TestHeldA=false,TestHeldD=false,TestHeldS=false;
TSharedPtr<FJsonObject> TParse(const FString& Text){TSharedPtr<FJsonObject> O;auto R=TJsonReaderFactory<>::Create(Text);return FJsonSerializer::Deserialize(R,O)?O:nullptr;}
FString TJson(const TSharedPtr<FJsonObject>& O){FString T;auto W=TJsonWriterFactory<>::Create(&T);FJsonSerializer::Serialize(O.ToSharedRef(),W);return T;}
FString TCompact(const TSharedPtr<FJsonObject>& O){FString T;auto W=TJsonWriterFactory<TCHAR,TCondensedJsonPrintPolicy<TCHAR>>::Create(&T);FJsonSerializer::Serialize(O.ToSharedRef(),W);return T;}
void TestFinish(AParisBridgeMission* M,const FString& Status){
    if(TestDone)return;TestDone=true;auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("status"),Status);O->SetStringField(TEXT("mode"),TestMode);O->SetStringField(TEXT("scope"),TEXT("Opt-in native movement/input and real durable saves; declared direct-damage fixture only for combat checkpoint checks; not human natural-combat acceptance."));
    O->SetArrayField(TEXT("checks"),TestChecks);O->SetNumberField(TEXT("wall_seconds"),FPlatformTime::Seconds()-TestBegin);O->SetNumberField(TEXT("actual_player_travel_cm"),TestTravel);O->SetStringField(TEXT("state"),M->ReadMissionState());
    FString JournalReason;if(M->CanLoadCheckpoint(JournalReason))O->SetStringField(TEXT("journal"),M->InspectCheckpointJournal());
    FFileHelper::SaveStringToFile(TJson(O),*(TestOut/TEXT("RESULT.json")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);FPlatformMisc::RequestExit(false);
}
bool TC(AParisBridgeMission* M,bool Pass,const FString& Label){auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("name"),Label);O->SetBoolField(TEXT("pass"),Pass);TestChecks.Add(MakeShared<FJsonValueObject>(O));if(!Pass)TestFinish(M,TEXT("failed_")+Label);return Pass;}
void Key(APlayerController* PC,FKey K,bool Press){PC->InputKey(FInputKeyEventArgs::CreateSimulated(K,Press?IE_Pressed:IE_Released,Press?1:0));}
void Tap(APlayerController* PC,FKey K){Key(PC,K,true);Key(PC,K,false);}
void Held(APlayerController* PC,FKey K,bool Value,bool& Flag){if(Value!=Flag){Key(PC,K,Value);Flag=Value;}}
void Stop(APlayerController* PC){Held(PC,EKeys::W,false,TestHeldW);Held(PC,EKeys::LeftShift,false,TestHeldShift);}
void Aim(APlayerController* PC,FVector Target,double PitchOffset=0){FVector Eye;FRotator View;PC->GetPlayerViewPoint(Eye,View);auto R=(Target-Eye).Rotation();R.Pitch+=PitchOffset;PC->SetControlRotation(R);}
bool WalkTo(AParisBridgeMission* M,APlayerController* PC,ACharacter* P,FVector Target,double Radius=65,bool Sprint=false,bool Direct=false){
    const FVector Feet=P->GetNavAgentLocation();if(FVector::Dist2D(Feet,Target)<Radius){Stop(PC);return true;}
    FVector Next=Target;if(!Direct){auto* Path=UNavigationSystemV1::FindPathToLocationSynchronously(M->GetWorld(),Feet,Target,P);if(!Path||!Path->IsValid()||Path->IsPartial()){TC(M,false,TEXT("probe_route_partial"));return false;}for(auto V:Path->PathPoints)if(FVector::Dist2D(Feet,V)>65){Next=V;break;}}
    PC->SetControlRotation(FRotator(0,(Next-Feet).Rotation().Yaw,0));Held(PC,EKeys::LeftShift,Sprint,TestHeldShift);Held(PC,EKeys::W,true,TestHeldW);return false;
}
void TestDamage(ACharacter* P){auto* F=P->FindFunction(TEXT("PC_ApplyDamage"));check(F);FStructOnScope Params(F);auto* A=CastField<FNumericProperty>(F->FindPropertyByName(TEXT("Amount")));check(A);A->SetFloatingPointPropertyValue(A->ContainerPtrToValuePtr<void>(Params.GetStructMemory()),1000);P->ProcessEvent(F,Params.GetStructMemory());}
void Negative(AParisBridgeMission* M,const TSharedPtr<FJsonObject>& Root){
    auto Check=[&](const TCHAR* Label,TFunction<void(TSharedPtr<FJsonObject>)> Mutate){auto C=TParse(TJson(Root));Mutate(C);FString E;return TC(M,!M->ValidateEquipmentReviewPayload(TJson(C),E),Label);};
    Check(TEXT("reject_unearned_frag"),[](auto O){auto E=O->GetObjectField(TEXT("equipment"));E->SetNumberField(TEXT("frag"),E->GetNumberField(TEXT("frag"))+1);});
    Check(TEXT("reject_supply_receipt_mismatch"),[](auto O){auto E=O->GetObjectField(TEXT("equipment"))->GetArrayField(TEXT("supplies"))[0]->AsObject();E->SetNumberField(TEXT("frag_remaining"),1);});
    Check(TEXT("reject_fake_completed_bridgehead"),[](auto O){O->SetStringField(TEXT("phase"),TEXT("Won"));auto T=O->GetObjectField(TEXT("tutorial"));T->SetStringField(TEXT("checkpoint"),TEXT("CP1"));T->SetNumberField(TEXT("step"),Complete);T->SetBoolField(TEXT("combat_open"),true);T->SetBoolField(TEXT("complete"),true);});
    Check(TEXT("reject_unearned_recruit"),[](auto O){O->GetObjectField(TEXT("tutorial"))->SetArrayField(TEXT("recruit_history"),{MakeShared<FJsonValueBoolean>(false),MakeShared<FJsonValueBoolean>(true)});});
    Check(TEXT("reject_duplicate_actor_id"),[](auto O){O->GetArrayField(TEXT("actors"))[2]->AsObject()->SetStringField(TEXT("id"),TEXT("Ally1"));});
}
}
#include "ParisProneStrafeCheck.inl"
#include "ParisProneTurnCheck.inl"
void Diagnostics(AParisBridgeMission* M,float){
    if(!Enabled())return;
    if(!TestInitialized){TestInitialized=true;if(!FParse::Value(FCommandLine::Get(),TEXT("ParisTutorialCheck="),TestMode))return;FParse::Value(FCommandLine::Get(),TEXT("ParisTutorialOut="),TestOut);IFileManager::Get().MakeDirectory(*TestOut,true);TestBegin=FPlatformTime::Seconds();}
    if(TestMode.IsEmpty()||TestDone||M->GetWorld()->IsPaused())return;
    auto* PC=UGameplayStatics::GetPlayerController(M,0);auto* P=PC?Cast<ACharacter>(PC->GetPawn()):nullptr;if(!P)return;
    if(M->Phase==TEXT("Error")){TestFinish(M,TEXT("failed_preparation_")+M->Feedback);return;}
    if(FPlatformTime::Seconds()-TestBegin>210){TestFinish(M,TEXT("failed_deadline"));return;}
    const double Now=M->GetWorld()->GetTimeSeconds();auto& S=State(M);auto& E=ParisTacticalEquipment::Session(M->GetWorld());
    if(Now>TestTraceAt&&M->Phase!=TEXT("Preparing")){TestTraceAt=Now+.2;auto R=MakeShared<FJsonObject>();const FVector Feet=P->GetNavAgentLocation();R->SetNumberField(TEXT("frame"),GFrameCounter);R->SetNumberField(TEXT("time"),Now);R->SetNumberField(TEXT("step"),S.Stage);R->SetArrayField(TEXT("feet"),{MakeShared<FJsonValueNumber>(Feet.X),MakeShared<FJsonValueNumber>(Feet.Y),MakeShared<FJsonValueNumber>(Feet.Z)});R->SetNumberField(TEXT("yaw"),P->GetActorRotation().Yaw);R->SetNumberField(TEXT("control_pitch"),PC->GetControlRotation().Pitch);R->SetNumberField(TEXT("look_axis"),P->GetInputAxisValue(TEXT("PC_LookYaw")));R->SetNumberField(TEXT("crawl_distance"),S.CrawlDistance);R->SetBoolField(TEXT("crawl_armed"),S.CrawlArmed);R->SetBoolField(TEXT("turn_blocked"),::ParisProneTurnBlocked(P));R->SetNumberField(TEXT("turn_check_phase"),TurnPhase);R->SetNumberField(TEXT("right_axis"),P->GetInputAxisValue(TEXT("PC_MoveRight")));R->SetNumberField(TEXT("posture"),Num(P,TEXT("DesiredPosture")));R->SetNumberField(TEXT("half_height"),P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight());R->SetBoolField(TEXT("grounded"),P->GetCharacterMovement()->IsMovingOnGround());const bool Physical=(TestMode==TEXT("copy_training")||TestMode==TEXT("full")||TestMode==TEXT("crawl_controls")||TestMode==TEXT("prone_strafe")||TestMode==TEXT("prone_turn"))&&S.Stage>=Look||TestMode==TEXT("combat_cp1")&&S.Stage>=Combat;if(Physical&&TestPrevious!=FVector::ZeroVector)TestTravel+=FVector::Dist2D(TestPrevious,Feet);TestPrevious=Physical?Feet:FVector::ZeroVector;FFileHelper::SaveStringToFile(TCompact(R)+TEXT("\n"),*(TestOut/TEXT("movement.jsonl")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM,&IFileManager::Get(),FILEWRITE_Append);}
    if(M->Phase==TEXT("Preparing"))return;
    if(TestMode==TEXT("restore_cp0")||TestMode==TEXT("restore_cp1")||TestMode==TEXT("combat_cp1")||TestMode==TEXT("supply_capacity")){
        if(M->Phase==TEXT("Ready")&&!TestLoadSent){TestLoadSent=true;M->LoadCheckpoint();return;}
        if(M->VerifiedRestoreState.IsEmpty())return;
        if(TestMode.StartsWith(TEXT("restore"))){
            if(!TC(M,TestMode==TEXT("restore_cp0")?M->Phase==TEXT("TrainingCheckpoint")&&!S.CombatOpen&&S.CP0Saved:M->Phase==TEXT("Won")&&S.Done,TEXT("restored_checkpoint_phase")))return;
            auto J=TParse(M->InspectCheckpointJournal())->GetObjectField(TEXT("snapshot")),V=TParse(M->VerifiedRestoreState);
            if(!TC(M,TJson(J->GetObjectField(TEXT("equipment")))==TJson(V->GetObjectField(TEXT("equipment"))),TEXT("restore_exact_equipment_without_grants")))return;
            for(int I=0;I<6;++I){auto A=J->GetArrayField(TEXT("actors"))[I]->AsObject(),B=V->GetArrayField(TEXT("actors"))[I]->AsObject();for(const TCHAR* K:{TEXT("health"),TEXT("loaded"),TEXT("reserve"),TEXT("shots")})if(!TC(M,A->GetNumberField(K)==B->GetNumberField(K),FString::Printf(TEXT("restore_actor%d_%s"),I,K)))return;}
            TestFinish(M,TEXT("pass_")+TestMode);return;
        }
    }
    if(TestMode==TEXT("supply_capacity")&&!M->VerifiedRestoreState.IsEmpty()){
        if(!S.CombatOpen){if(M->InsideCheckpoint())Tap(PC,EKeys::Enter);return;}
        if(!TestAction){for(TActorIterator<ACharacter>I(M->GetWorld());I;++I)if(!I->IsPlayerControlled())if(auto* A=Cast<AAIController>(I->GetController())){if(auto* F=A->FindFunction(TEXT("PC_EnableCombat"))){FStructOnScope Args(F);FindFProperty<FBoolProperty>(F,TEXT("Enabled"))->SetPropertyValue_InContainer(Args.GetStructMemory(),false);A->ProcessEvent(F,Args.GetStructMemory());}if(A->GetBrainComponent())A->GetBrainComponent()->StopLogic(TEXT("Declared finite-supply isolation"));A->StopMovement();}TestAction=true;TC(M,true,TEXT("declared_npc_brain_isolation_for_supply_test"));}
        if(WalkTo(M,PC,P,E.Supplies[1].Position+FVector(-110,0,0),40)){
            Aim(PC,E.Supplies[1].Position+FVector(0,0,25));if(Now<TestNext)return;
            if(!TestSupplyAimed){TestSupplyAimed=true;TestNext=Now+.35;return;}
            const int BeforeRounds=E.Grant,BeforeFrag=E.FragGrant,BeforeSmoke=E.SmokeGrant;Tap(PC,EKeys::E);
            if(!TC(M,E.Frag==4&&E.Smoke==4&&E.Supplies[1].FragRemaining==1&&E.Supplies[1].SmokeRemaining==1&&E.FragGrant==BeforeFrag+1&&E.SmokeGrant==BeforeSmoke+1&&E.Grant==BeforeRounds+16,TEXT("actual_partial_grenade_grant_leaves_stock")))return;
            const int R=E.Grant,F=E.FragGrant,G=E.SmokeGrant;Tap(PC,EKeys::E);
            if(!TC(M,E.Grant==R&&E.FragGrant==F&&E.SmokeGrant==G&&E.Supplies[1].FragRemaining==1&&E.Supplies[1].SmokeRemaining==1,TEXT("full_categories_and_empty_rounds_do_not_regrant")))return;
            FScreenshotRequest::RequestScreenshot(TestOut/TEXT("partial_supply.png"),false,false);TestFinish(M,TEXT("pass_supply_capacity"));
        }return;
    }
    if(TestMode==TEXT("copy_training")&&CopyPhase>0){
       if(FScreenshotRequest::IsScreenshotRequested())return;
       if(CopyPhase==1){if(Now-TestAt<.4)return;Tap(PC,EKeys::Escape);CopyPhase=2;TestAt=Now;return;}
       if(CopyPhase==2){if(Now-TestAt<.4)return;if(!TC(M,TrainingCheckpointSaved(M)&&M->LivingDefenders==3&&!CombatStarted(M)&&Heading(M)==TEXT("BASIC TRAINING SAVED")&&Goal(M).Equals(M->FarBankFeet,.01)&&!KeyHint(M).Contains(TEXT("SAVE IN CIRCLE")),TEXT("actual_saved_CP0_three_live_guards_and_bridge_C_guidance")))return;FScreenshotRequest::RequestScreenshot(TestOut/TEXT("cp0_saved_hud.png"),false,false);CopyPhase=3;return;}
       TestFinish(M,TEXT("pass_copy_training_actual_CP0_save"));return;
   }
   if(TestMode==TEXT("copy_training")&&FScreenshotRequest::IsScreenshotRequested())return;
   if(M->Phase==TEXT("Lost")){TestFinish(M,TEXT("failed_player_death"));return;}
    if(M->Phase==TEXT("Ready")){if(M->ReadySeconds>1)Tap(PC,EKeys::Enter);return;}
    if(S.Stage>=Crawl&&S.Stage<=Fire&&ProneTurnExercise(M,PC,P,Now))return;
    if(S.Stage>=Crawl&&S.Stage<=Stand&&TestMode==TEXT("prone_strafe")&&StrafePhase>0&&StrafeExercise(M,PC,P,Now))return;
    if(S.Stage!=TestLast){Stop(PC);Held(PC,EKeys::A,false,TestHeldA);Held(PC,EKeys::D,false,TestHeldD);Held(PC,EKeys::S,false,TestHeldS);Key(PC,EKeys::LeftControl,false);Key(PC,EKeys::E,false);Key(PC,EKeys::LeftMouseButton,false);TestAction=false;TestAt=Now;TestNext=Now+.25;TestLast=S.Stage;FScreenshotRequest::RequestScreenshot(TestOut/FString::Printf(TEXT("step_%02d.png"),S.Stage),false,false);}
    if(Now<TestNext)return;
    switch(S.Stage){
    case Look:PC->AddYawInput(20);break;
    case Walk:WalkTo(M,PC,P,WalkFeet);break;
    case Run:WalkTo(M,PC,P,RunFeet,65,true);break;
    case Jump:if(!TestAction){Key(PC,EKeys::SpaceBar,true);TestAction=true;TestAt=Now;}else if(Now-TestAt>.6)Key(PC,EKeys::SpaceBar,false);break;
    case Crouch:if(!TestAction){Key(PC,EKeys::LeftControl,true);TestAction=true;}break;
    case Crawl:{
        if(Num(P,TEXT("DesiredPosture"))!=2){
            if(WalkTo(M,PC,P,CrawlStart,40)&&!TestAction){
                const double Delta=FMath::FindDeltaAngleDegrees(PC->GetControlRotation().Yaw,(CrawlEnd-CrawlStart).Rotation().Yaw);
                if(FMath::Abs(Delta)>2){PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::MouseX,IE_Axis,FMath::Clamp(Delta/2.5,-5.,5.)));break;}
                Tap(PC,EKeys::Z);TestAction=true;TestNext=Now+.6;
            }break;
        }
        if(P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight()>=35)break;
        if(StrafeExercise(M,PC,P,Now))break;
        // Actual four-key lesson. No pawn/control heading assignment while prone.
        if(TestCrawlPhase==0){Stop(PC);TestAt=Now;Held(PC,EKeys::W,true,TestHeldW);TestCrawlPhase=1;}
        else if(TestCrawlPhase==1&&Now-TestAt>1.5){Stop(PC);Held(PC,EKeys::S,true,TestHeldS);TestAt=Now;TestCrawlPhase=2;}
        else if(TestCrawlPhase==2&&Now-TestAt>1.5){Held(PC,EKeys::S,false,TestHeldS);Held(PC,EKeys::A,true,TestHeldA);TestAt=Now;TestCrawlPhase=3;}
        else if(TestCrawlPhase==3&&Now-TestAt>1.0){Held(PC,EKeys::A,false,TestHeldA);Held(PC,EKeys::D,true,TestHeldD);TestAt=Now;TestCrawlPhase=4;}
        else if(TestCrawlPhase==4&&Now-TestAt>1.0){Held(PC,EKeys::D,false,TestHeldD);Held(PC,EKeys::W,true,TestHeldW);TestCrawlPhase=5;}
        break;
    }
    case Stand:if(!TestAction){Tap(PC,EKeys::Z);TestAction=true;}break;
    case Fire:Aim(PC,ThrowFeet+FVector(0,0,25));Tap(PC,EKeys::LeftMouseButton);TestNext=Now+1;break;
    case Reload:if(!TestAction){Tap(PC,EKeys::R);TestAction=true;}break;
    case Frag:case Smoke:{
        if(S.Stage==Frag&&!TestPracticeTaken){if(WalkTo(M,PC,P,SupplyFeet+FVector(-110,0,0),45)){Aim(PC,E.Supplies[0].Position+FVector(0,0,25));Tap(PC,EKeys::E);TestPracticeTaken=E.ConsolidatedSupply?E.Supplies[0].Remaining==16&&E.Supplies[0].FragRemaining==2&&E.Supplies[0].SmokeRemaining==2:E.Supplies[2].Remaining==0;TestNext=Now+.3;}return;}
        Aim(PC,ThrowFeet+FVector(0,0,100));auto R=PC->GetControlRotation();R.Pitch=20;PC->SetControlRotation(R);
        const int Wanted=S.Stage==Frag?1:2;if(!TestAction){if(E.SelectedSlot!=Wanted){Tap(PC,EKeys::MouseScrollDown);TestNext=Now+.25;return;}Key(PC,EKeys::LeftMouseButton,true);TestAction=true;TestAt=Now;}
        else if(Now-TestAt>.9)Key(PC,EKeys::LeftMouseButton,false);break;}
    case Supply:if(WalkTo(M,PC,P,Goal(M),45)){Aim(PC,E.Supplies[0].Position+FVector(0,0,25));Tap(PC,EKeys::E);TestNext=Now+.3;}break;
    case Disarm:
        if(!TestReplayChecked){Stop(PC);Aim(PC,E.Supplies[0].Position+FVector(0,0,25));const int G=E.Grant,F=E.FragGrant,C=E.SmokeGrant;Tap(PC,EKeys::E);TestReplayChecked=true;if(!TC(M,E.Grant==G&&E.FragGrant==F&&E.SmokeGrant==C,TEXT("empty_box_repeat_no_grants")))return;}
        if(WalkTo(M,PC,P,Goal(M),35)&&P->GetVelocity().Size()<15){Aim(PC,E.Traps[2].Position+FVector(0,0,6));if(!TestAction){Key(PC,EKeys::E,true);TestAction=true;TestAt=Now;}else if(!TestCancelChecked&&Now-TestAt>.7){Key(PC,EKeys::E,false);if(!TC(M,E.DisarmClock==0&&E.Traps[2].State==TEXT("Armed"),TEXT("disarm_release_cancels")))return;TestCancelChecked=true;TestAction=false;TestNext=Now+.3;}}break;
    case Recruit:{int I=!S.History[0]?0:1;auto* C=Pawn(M->GetWorld(),I==0?TEXT("Ally1"):TEXT("Ally2"));if(S.Dialog>=0){if(TestDialogPhase==0){FScreenshotRequest::RequestScreenshot(TestOut/FString::Printf(TEXT("recruit%d_default_join.png"),I+1),false,false);TestDialogPhase=1;TestNext=Now+.5;}else if(TestDialogPhase==1){Tap(PC,EKeys::Right);FScreenshotRequest::RequestScreenshot(TestOut/FString::Printf(TEXT("recruit%d_cancel_selected.png"),I+1),false,false);TestDialogPhase=2;TestNext=Now+.5;}else if(TestDialogPhase==2){Tap(PC,EKeys::Left);FScreenshotRequest::RequestScreenshot(TestOut/FString::Printf(TEXT("recruit%d_join_selected.png"),I+1),false,false);TestDialogPhase=3;TestNext=Now+.5;}else{Tap(PC,EKeys::Enter);TestDialogPhase=0;TestNext=Now+.3;}}else if(WalkTo(M,PC,P,C->GetNavAgentLocation(),160)){Aim(PC,C->GetActorLocation()+FVector(0,0,30));Tap(PC,EKeys::E);TestNext=Now+.3;}break;}
    case CP0:
        if(!WalkTo(M,PC,P,CP0Feet,45))break;
        if(TestMode==TEXT("combat_cp1")){if(!M->CheckpointDialogVisible())Tap(PC,EKeys::Enter);TestNext=Now+.4;break;}
        if(Now-TestAt<5)break;
        if(TestMode==TEXT("copy_training")&&!CopyBefore){CopyBefore=true;FScreenshotRequest::RequestScreenshot(TestOut/TEXT("cp0_before_save.png"),false,false);TestNext=Now+.3;break;}
        if(M->CheckpointDialogState()==TEXT("Succeeded")){
            auto J=TParse(M->InspectCheckpointJournal())->GetObjectField(TEXT("snapshot"));FFileHelper::SaveStringToFile(TJson(J),*(TestOut/TEXT("expected_cp0.json")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
            if(!TC(M,J->GetStringField(TEXT("phase"))==TEXT("TrainingCheckpoint")&&M->LivingDefenders==3&&S.History[0]&&S.History[1],TEXT("cp0_durable_before_combat")))return;
            if(!TC(M,Num(P,TEXT("LoadedAmmo"))+Num(P,TEXT("ReserveAmmo"))+Num(P,TEXT("ShotSequence"))==12+E.Grant&&E.Frag+E.FragThrown==1+E.FragGrant&&E.Smoke+E.SmokeThrown==1+E.SmokeGrant,TEXT("three_resource_conservation")))return;
            Negative(M,J);if(TestDone)return;if(TestMode==TEXT("copy_training")){FScreenshotRequest::RequestScreenshot(TestOut/TEXT("cp0_save_success.png"),false,false);CopyPhase=1;TestAt=Now;}else TestFinish(M,TEXT("pass_tutorial_cp0_native_inputs"));return;
        }
        if(!M->CheckpointDialogVisible()){Tap(PC,EKeys::E);TestNext=Now+.5;}break;
    case Combat:
        if(TestMode==TEXT("combat_cp1")){
            if(!TestAction){for(const TCHAR* ID:{TEXT("German1"),TEXT("German2"),TEXT("German3")})TestDamage(Pawn(M->GetWorld(),ID));TestAction=true;TC(M,true,TEXT("declared_original_damage_endpoint_guard_clear_fixture"));}
        }break;
    case CP1:
        if(!WalkTo(M,PC,P,M->BridgeheadFeet,50))break;
        if(!M->CheckpointDialogVisible()){Tap(PC,EKeys::E);TestNext=Now+.5;}break;
    case Complete:
        if(M->CheckpointDialogState()==TEXT("Succeeded")){if(TC(M,M->LivingDefenders==0&&M->SaveSerial>=2,TEXT("cp1_enemy_clear_durable_save")))TestFinish(M,TEXT("pass_combat_cp1"));}break;
    default:break;
    }
    if(TestMode==TEXT("combat_cp1")&&S.Stage==CP0&&S.CP0Saved&&!M->CheckpointDialogVisible()&&M->InsideCheckpoint())Tap(PC,EKeys::Enter);
}
