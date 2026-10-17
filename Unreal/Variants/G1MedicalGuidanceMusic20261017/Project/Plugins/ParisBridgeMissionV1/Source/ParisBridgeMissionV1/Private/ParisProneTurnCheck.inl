// Native input checks: no pawn position/rotation assignment while prone.
namespace {
int TurnPhase=0;double TurnAt=0,TurnBase=0,TurnPitch=0,TurnPeak=0;FVector TurnOrigin,TurnForward,TurnRight;TWeakObjectPtr<AActor> TurnWall;
void TurnBegin(ACharacter* P,double Now,int Phase){TurnPhase=Phase;TurnAt=Now;TurnOrigin=P->GetNavAgentLocation();TurnPeak=0;}
bool ProneTurnExercise(AParisBridgeMission* M,APlayerController* PC,ACharacter* P,double Now){
    if(TestMode!=TEXT("prone_turn")||TurnPhase>=14)return false;
    const FVector Feet=P->GetNavAgentLocation();TurnPeak=FMath::Max(TurnPeak,double(P->GetVelocity().Size2D()));
    auto Mouse=[&](FKey Key,double Value){const double Span=FMath::Clamp(double(M->GetWorld()->GetDeltaSeconds())*60.,1.,24.);PC->InputKey(FInputKeyEventArgs::CreateSimulated(Key,IE_Axis,Value*Span));};
    auto Shot=[&](const TCHAR* Name){FScreenshotRequest::RequestScreenshot(TestOut/FString(Name)+TEXT(".png"),false,false);};
    auto Release=[&](){Stop(PC);Held(PC,EKeys::A,false,TestHeldA);Held(PC,EKeys::D,false,TestHeldD);Held(PC,EKeys::S,false,TestHeldS);};
    auto Clear=[&](){bool Body,Floor;return ::ParisProneStrafeCheck(P,FVector::ZeroVector,Body,Floor);};
    switch(TurnPhase){
    case 0:{
        const FVector Spot=(CrawlStart+CrawlEnd)*.5;
        if(!WalkTo(M,PC,P,Spot,25))return true;
        const double Required=(CrawlEnd-CrawlStart).Rotation().Yaw,Delta=FMath::FindDeltaAngleDegrees(PC->GetControlRotation().Yaw,Required);
        if(FMath::Abs(Delta)>2){Mouse(EKeys::MouseX,FMath::Clamp(Delta/2.5,-5.,5.));return true;}
        if(!TC(M,!State(M).CrawlArmed&&State(M).CrawlDistance==0,TEXT("standing_or_crouched_travel_does_not_count")))return true;
        TurnBase=P->GetActorRotation().Yaw;Tap(PC,EKeys::Z);TurnBegin(P,Now,1);break;
    }
    case 1:if(Now-TurnAt>.7&&P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight()<35&&Name(P,TEXT("ActionState"))==TEXT("Ready")&&State(M).CrawlArmed){
        if(!TC(M,FVector::Dist2D(Feet,CrawlStart)>85&&State(M).CrawlArmed,TEXT("prone_lesson_arms_outside_old_start_gate")))return true;
        TurnBase=P->GetActorRotation().Yaw;TurnBegin(P,Now,2);
    }else if(Now-TurnAt>4)TC(M,false,TEXT("native_transition_lesson_arming_deadline"));break;
    case 2:{const double Yaw=FMath::FindDeltaAngleDegrees(TurnBase,P->GetActorRotation().Yaw);
        if(Yaw<15)Mouse(EKeys::MouseX,2);else{if(!TC(M,Clear()&&State(M).CrawlDistance<1,TEXT("actual_MouseX_right_body_turn_without_fake_travel")))return true;Shot(TEXT("prone_mouse_right"));TurnBase=P->GetActorRotation().Yaw;TurnBegin(P,Now,3);}
        if(Now-TurnAt>6&&TurnPhase==2)TC(M,false,TEXT("mouse_right_turn_deadline"));break;}
    case 3:{const double Yaw=FMath::FindDeltaAngleDegrees(TurnBase,P->GetActorRotation().Yaw);
        if(Yaw>-15)Mouse(EKeys::MouseX,-2);else{if(!TC(M,Clear(),TEXT("actual_MouseX_left_body_turn")))return true;Shot(TEXT("prone_mouse_left"));TurnPitch=PC->GetControlRotation().Pitch;TurnBegin(P,Now,4);}
        if(Now-TurnAt>6&&TurnPhase==3)TC(M,false,TEXT("mouse_left_turn_deadline"));break;}
    case 4:if(FMath::Abs(FMath::FindDeltaAngleDegrees(TurnPitch,PC->GetControlRotation().Pitch))<10){Mouse(EKeys::MouseY,2);if(Now-TurnAt>6)TC(M,false,TEXT("mouse_pitch_first_deadline"));}
        else{if(!TC(M,Clear(),TEXT("actual_MouseY_first_pitch_direction")))return true;TurnPitch=PC->GetControlRotation().Pitch;TurnBegin(P,Now,5);}break;
    case 5:if(FMath::Abs(FMath::FindDeltaAngleDegrees(TurnPitch,PC->GetControlRotation().Pitch))<10){Mouse(EKeys::MouseY,-2);if(Now-TurnAt>6)TC(M,false,TEXT("mouse_pitch_reverse_deadline"));}
        else{if(!TC(M,Clear(),TEXT("actual_MouseY_reverse_pitch_direction")))return true;TurnForward=P->GetActorForwardVector();TurnRight=P->GetActorRightVector();TurnBase=P->GetActorRotation().Yaw;
            auto* Wall=M->GetWorld()->SpawnActor<AActor>();auto* Box=NewObject<UBoxComponent>(Wall);Wall->SetRootComponent(Box);Box->SetBoxExtent(FVector(190,20,80));Box->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);Box->SetCollisionObjectType(ECC_WorldStatic);Box->SetCollisionResponseToAllChannels(ECR_Block);Box->RegisterComponent();Wall->SetActorLocation(Feet+TurnRight*110+FVector(0,0,70));Wall->SetActorRotation(P->GetActorRotation());TurnWall=Wall;TC(M,true,TEXT("declared_transient_rotational_wall_fixture"));TurnBegin(P,Now,6);}break;
    case 6:if(Now-TurnAt<3)Mouse(EKeys::MouseX,4);else{
        const double Yaw=FMath::FindDeltaAngleDegrees(TurnBase,P->GetActorRotation().Yaw);
        if(!TC(M,Yaw>1&&Yaw<40&&Clear()&&::ParisProneTurnBlocked(P),TEXT("mouse_turn_stops_before_long_body_wall_overlap")))return true;
        Shot(TEXT("prone_mouse_wall_stop"));TurnBegin(P,Now,7);
    }break;
    case 7:if(FMath::FindDeltaAngleDegrees(TurnBase,P->GetActorRotation().Yaw)>1){Mouse(EKeys::MouseX,-2);if(Now-TurnAt>6)TC(M,false,TEXT("mouse_wall_reverse_deadline"));}
        else{if(!TC(M,Clear(),TEXT("actual_reverse_mouse_turn_escapes_wall")))return true;TurnWall->Destroy();TurnForward=P->GetActorForwardVector();TurnRight=P->GetActorRightVector();Held(PC,EKeys::W,true,TestHeldW);TurnBegin(P,Now,8);}break;
    case 8:if(Now-TurnAt>4.7){Stop(PC);
        if(!TC(M,State(M).Stage==Crawl&&State(M).CrawlDistance>=250&&State(M).CrawlAxisTravel[1]<15&&TurnPeak<=61,TEXT("W_only_2_5m_does_not_complete_four_direction_lesson")))return true;
        if(!TC(M,!M->Feedback.StartsWith(TEXT("Prone turn blocked"))&&!M->Feedback.StartsWith(TEXT("Prone path blocked")),TEXT("old_blocked_notice_clears_on_admitted_movement")))return true;
        Shot(TEXT("prone_checklist_missing_directions"));Held(PC,EKeys::S,true,TestHeldS);TurnBegin(P,Now,9);
    }break;
    case 9:if(Now-TurnAt>4.7){Held(PC,EKeys::S,false,TestHeldS);if(!TC(M,State(M).Stage==Crawl&&State(M).CrawlAxisTravel[1]>=15,TEXT("S_counts_actual_reverse_but_missing_A_D_retains_lesson")))return true;Held(PC,EKeys::A,true,TestHeldA);TurnBegin(P,Now,10);}break;
    case 10:if(Now-TurnAt>1.2){Held(PC,EKeys::A,false,TestHeldA);if(!TC(M,State(M).Stage==Crawl&&State(M).CrawlAxisTravel[2]>=15,TEXT("A_counts_actual_lateral_but_missing_D_retains_lesson")))return true;Held(PC,EKeys::D,true,TestHeldD);TurnBegin(P,Now,11);}break;
    case 11:if(State(M).Stage==Stand){Release();if(!TC(M,(State(M).Mask&(1<<(Crawl-1)))!=0&&FVector::Dist2D(Feet,CrawlEnd)>110,TEXT("actual_four_direction_lesson_auto_advances_without_old_endpoint")))return true;Shot(TEXT("prone_complete_stand_prompt"));TurnBegin(P,Now,12);}
        else if(Now-TurnAt>2)TC(M,false,TEXT("four_direction_completion_deadline"));break;
    case 12:if(Now-TurnAt>.4){Tap(PC,EKeys::Z);TurnBegin(P,Now,13);}break;
    case 13:if(State(M).Stage==Fire){if(!TC(M,P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight()>90,TEXT("native_Z_stands_then_auto_enters_shooting_lesson")))return true;TurnPhase=14;return false;}
        else if(Now-TurnAt>3)TC(M,false,TEXT("stand_to_shooting_deadline"));break;
    }
    return true;
}
}
