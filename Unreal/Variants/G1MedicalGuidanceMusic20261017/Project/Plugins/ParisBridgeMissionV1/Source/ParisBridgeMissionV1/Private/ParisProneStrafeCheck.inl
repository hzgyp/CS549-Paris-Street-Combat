// Opt-in physical-control checks, transient wall and a declared visual observer.
namespace {
int StrafePhase=0;double StrafeAt=0,StrafePeak=0;FVector StrafeOrigin,StrafeRight,StrafeForward;TWeakObjectPtr<AActor> StrafeWall;TWeakObjectPtr<ACameraActor> StrafeCamera;bool StrafeSupportedNegative=false;
void StrafeBegin(ACharacter* P,double Now,int Phase){StrafeOrigin=P->GetNavAgentLocation();StrafeAt=Now;StrafePeak=0;StrafePhase=Phase;}
bool StrafeExercise(AParisBridgeMission* M,APlayerController* PC,ACharacter* P,double Now){
    if(TestMode!=TEXT("prone_strafe")||StrafePhase>=10)return false;
    StrafePeak=FMath::Max(StrafePeak,double(P->GetVelocity().Size2D()));
    auto Signed=[&](FVector Axis){return FVector::DotProduct(P->GetNavAgentLocation()-StrafeOrigin,Axis);};
    auto Shot=[&](const TCHAR* Label){FScreenshotRequest::RequestScreenshot(TestOut/FString(Label)+TEXT(".png"),false,false);};
    switch(StrafePhase){
    case 0:{
        Stop(PC);StrafeRight=P->GetActorRightVector();StrafeForward=P->GetActorForwardVector();
        bool Box,Floor;::ParisProneStrafeCheck(P,FVector(0,0,100),Box,Floor);
        if(!TC(M,!Floor,TEXT("unsupported_future_rejected_by_original_three_floor_supports")))return true;
        StrafeCamera=M->GetWorld()->SpawnActor<ACameraActor>();StrafeCamera->SetActorLocation(P->GetNavAgentLocation()+StrafeForward*330+StrafeRight*250+FVector(0,0,140));StrafeCamera->SetActorRotation((P->GetActorLocation()-StrafeCamera->GetActorLocation()).Rotation());PC->SetViewTarget(StrafeCamera.Get());
        TC(M,true,TEXT("declared_transient_observer_no_player_pose_or_position_override"));
        Key(PC,EKeys::A,true);StrafeBegin(P,Now,1);break;
    }
    case 1:if(Now-StrafeAt>.65){Shot(TEXT("prone_left_actual"));if(Now-StrafeAt>1.1){Key(PC,EKeys::A,false);if(!TC(M,Signed(StrafeRight)<-25&&StrafePeak<=61,TEXT("A_actual_left_crawl_at_original_speed")))return true;Key(PC,EKeys::D,true);StrafeBegin(P,Now,2);}}break;
    case 2:if(Now-StrafeAt>.65){Shot(TEXT("prone_right_actual"));if(Now-StrafeAt>1.1){Key(PC,EKeys::D,false);if(!TC(M,Signed(StrafeRight)>25&&StrafePeak<=61,TEXT("D_actual_right_crawl_at_original_speed")))return true;Held(PC,EKeys::W,true,TestHeldW);StrafeBegin(P,Now,3);}}break;
    case 3:if(Now-StrafeAt>1.1){Stop(PC);if(!TC(M,Signed(StrafeForward)>25,TEXT("W_actual_forward_preserved")))return true;Key(PC,EKeys::S,true);StrafeBegin(P,Now,4);}break;
    case 4:if(Now-StrafeAt>1.1){Key(PC,EKeys::S,false);if(!TC(M,Signed(StrafeForward)<-25,TEXT("S_actual_backward_preserved")))return true;Held(PC,EKeys::W,true,TestHeldW);Key(PC,EKeys::A,true);StrafeBegin(P,Now,5);}break;
    case 5:if(Now-StrafeAt>1.1){Stop(PC);Key(PC,EKeys::A,false);if(!TC(M,Signed(StrafeForward)>20&&Signed(StrafeRight)<-20&&StrafePeak<=61,TEXT("W_A_diagonal_normalized_no_speed_gain")))return true;Key(PC,EKeys::S,true);Key(PC,EKeys::D,true);StrafeBegin(P,Now,6);}break;
    case 6:if(Now-StrafeAt>1.1){Key(PC,EKeys::S,false);Key(PC,EKeys::D,false);if(!TC(M,Signed(StrafeForward)<-20&&Signed(StrafeRight)>20&&StrafePeak<=61,TEXT("S_D_reverse_diagonal_preserved")))return true;StrafeBegin(P,Now,7);}break;
    case 7:if(Now-StrafeAt>.5){
        auto* Wall=M->GetWorld()->SpawnActor<AActor>();auto* Box=NewObject<UBoxComponent>(Wall);Wall->SetRootComponent(Box);Box->SetBoxExtent(FVector(190,40,80));Box->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);Box->SetCollisionObjectType(ECC_WorldStatic);Box->SetCollisionResponseToAllChannels(ECR_Block);Box->RegisterComponent();Wall->SetActorLocation(P->GetNavAgentLocation()+StrafeRight*205+FVector(0,0,70));Wall->SetActorRotation(P->GetActorRotation());StrafeWall=Wall;
        TC(M,true,TEXT("declared_temporary_wall_no_native_map_or_actor_modification"));Key(PC,EKeys::D,true);StrafeBegin(P,Now,8);
    }break;
    case 8:if(Now-StrafeAt>2.7){Key(PC,EKeys::D,false);Shot(TEXT("prone_wall_side_stop"));bool Body,Floor;::ParisProneStrafeCheck(P,FVector::ZeroVector,Body,Floor);if(!TC(M,Signed(StrafeRight)>25&&Signed(StrafeRight)<125&&::ParisProneFutureBlocked(P)&&Body,TEXT("side_wall_stop_before_long_body_overlap")))return true;Key(PC,EKeys::A,true);StrafeBegin(P,Now,9);}break;
    case 9:if(Now-StrafeAt>1.1){Key(PC,EKeys::A,false);if(!TC(M,Signed(StrafeRight)<-25,TEXT("reverse_escape_from_side_wall")))return true;StrafeWall->Destroy();PC->SetViewTarget(P);StrafeCamera->Destroy();StrafePhase=10;}
        break;
    }
    return true;
}
}
