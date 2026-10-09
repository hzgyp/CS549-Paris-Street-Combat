void AParisBridgeHUD::DrawHUD()
{
    Super::DrawHUD(); if(!Canvas || !PlayerOwner) return;
    auto* M=AParisBridgeMission::Find(this); auto* Player=Cast<ACharacter>(PlayerOwner->GetPawn());
    if(!M) return;
    if(!bLegacyWidgetRemoved)
    {
        TArray<UUserWidget*> Widgets;
        UWidgetBlueprintLibrary::GetAllWidgetsOfClass(this,Widgets,UUserWidget::StaticClass(),false);
        for(auto* W:Widgets) if(W && W->GetClass()->GetPathName().StartsWith(TEXT("/Game/ParisCombat/UI/CityGameplayV1/WBP_PCParisStatusV1"))) W->RemoveFromParent();
        bLegacyWidgetRemoved=true;
    }
    if(!bMapLoadAttempted)
    {
        bMapLoadAttempted=true;
        const FString File=FPaths::ConvertRelativePathToFull(FPaths::Combine(FPlatformProcess::BaseDir(),TEXT("../../UI/g1_minimap.png")));
        MinimapTexture=FImageUtils::ImportFileAsTexture2D(File);
        if(!MinimapTexture) { UE_LOG(LogTemp,Error,TEXT("PARIS_UX_MINIMAP_MISSING %s"),*File); }
        else { UE_LOG(LogTemp,Display,TEXT("PARIS_UX_HUD_READY minimap=%dx%d metric_bounds=0,-25000,10000,-15000 legacy_widget_removed=1"),MinimapTexture->GetSizeX(),MinimapTexture->GetSizeY()); }
    }
    const float S=FMath::Min(Canvas->SizeX/1920.f,Canvas->SizeY/1080.f);
    const float OX=(Canvas->SizeX-1920*S)*.5f,OY=(Canvas->SizeY-1080*S)*.5f;
    const FLinearColor Cream(.91f,.90f,.81f,1),Muted(.57f,.63f,.54f,1),Olive(.65f,.76f,.44f,1),
        Amber(1,.77f,.31f,1),Danger(.95f,.29f,.22f,1),Panel(.035f,.05f,.043f,.88f);
    auto Rect=[&](float X,float Y,float W,float H,FLinearColor C){DrawRect(C,OX+X*S,OY+Y*S,W*S,H*S);};
    auto Line=[&](float X,float Y,float XX,float YY,FLinearColor C,float T=1){DrawLine(OX+X*S,OY+Y*S,OX+XX*S,OY+YY*S,C,T*S);};
    auto Text=[&](const FString& V,float X,float Y,float Scale=1.f,FLinearColor C=FLinearColor::White){DrawText(V,C,OX+X*S,OY+Y*S,GEngine->GetMediumFont(),Scale*S);};
    auto Small=[&](const FString& V,float X,float Y,FLinearColor C=FLinearColor::White){DrawText(V,C,OX+X*S,OY+Y*S,GEngine->GetSmallFont(),S);};
    auto Border=[&](float X,float Y,float W,float H,FLinearColor C){Line(X,Y,X+W,Y,C);Line(X+W,Y,X+W,Y+H,C);Line(X+W,Y+H,X,Y+H,C);Line(X,Y+H,X,Y,C);};
    FString Objective=TEXT("Preparing squad and equipment");
    if(M->Phase==TEXT("Ready")) Objective=TEXT("CROSS THE RIVER  |  ENTER TO BEGIN");
    else if(M->Phase==TEXT("Crossing")) Objective=TEXT("Cross bridge C with your squad");
    else if(M->Phase==TEXT("Clearing")) Objective=FString::Printf(TEXT("Secure G1  |  %d guards remaining"),M->LivingDefenders);
    else if(M->Phase==TEXT("Occupying")) Objective=TEXT("Guards cleared  |  Occupy the bridgehead");
    else if(M->Phase==TEXT("Won")) Objective=TEXT("G1 SECURED  |  CHECKPOINT AVAILABLE");
    else if(M->Phase==TEXT("Lost")) Objective=TEXT("MISSION LOST  |  F9 LOAD / F6 RESTART");
    else if(M->Phase==TEXT("Error")) Objective=TEXT("MISSION STOPPED  |  SEE RUN LOG");
    Rect(38,36,650,91,Panel);Rect(38,36,4,91,Amber);
    Small(TEXT("PARIS  /  G1 BRIDGEHEAD"),58,47,Muted);Text(Objective,58,70,.95f,Cream);
    Small(TEXT("Liberation squad  /  Cross bridge C and secure G1"),58,103,Muted);

    // Fixed metric local ground overview: +X to the right, +Y to the top.
    const float MX=1572,MY=38,MW=310,MH=310;
    Rect(MX-10,MY-10,MW+20,MH+52,Panel);
    if(MinimapTexture) DrawTexture(MinimapTexture,OX+MX*S,OY+MY*S,MW*S,MH*S,0,0,1,1,FLinearColor::White,BLEND_Opaque);
    Border(MX,MY,MW,MH,Muted);Small(TEXT("G1 SECTOR"),MX+8,MY+MH+12,Muted);
    Small(TEXT("N"),MX+MW*.5f-3,MY+7,Cream);
    Line(MX+MW-100,MY+MH+19,MX+MW-7,MY+MH+19,Muted,2);
    Small(TEXT("30 m"),MX+MW-66,MY+MH+4,Cream);
    auto MapPoint=[&](FVector V){return FVector2D(MX+V.X/10000*MW,MY+(-15000-V.Y)/10000*MH);};
    auto InMap=[&](FVector2D P){return P.X>=MX+5 && P.X<=MX+MW-5 && P.Y>=MY+5 && P.Y<=MY+MH-5;};
    auto Dot=[&](FVector V,FLinearColor C,float R){const auto P=MapPoint(V);if(InMap(P)) Rect(P.X-R,P.Y-R,R*2,R*2,C);};
    for(TActorIterator<ACharacter> I(GetWorld());I;++I) if((I->ActorHasTag(TEXT("G1_Ally1")) || I->ActorHasTag(TEXT("G1_Ally2"))) && !Flag(*I,TEXT("IsDead")))
        Dot(I->GetActorLocation(),Olive,4);
    if(Player)
    {
        const auto P=MapPoint(Player->GetActorLocation());const double Angle=FMath::DegreesToRadians(PlayerOwner->GetControlRotation().Yaw);
        if(InMap(P))
        {
            const FVector2D F(FMath::Cos(Angle),-FMath::Sin(Angle)),R(-F.Y,F.X);
            const auto A=P+F*11,B=P-F*6+R*6,C=P-F*6-R*6;
            Line(A.X,A.Y,B.X,B.Y,Cream,2);Line(B.X,B.Y,C.X,C.Y,Cream,2);Line(C.X,C.Y,A.X,A.Y,Cream,2);
        }
        if(GetWorld()->GetTimeSeconds()>=NextMarkerRefresh)
        {
            NextMarkerRefresh=GetWorld()->GetTimeSeconds()+.2;CachedEnemyLocations.Reset();
            FVector Eye;FRotator View;PlayerOwner->GetPlayerViewPoint(Eye,View);
            const FVector Forward=View.Vector();
            for(TActorIterator<ACharacter> I(GetWorld());I;++I) if((I->ActorHasTag(TEXT("G1_German1")) || I->ActorHasTag(TEXT("G1_German2")) || I->ActorHasTag(TEXT("G1_German3"))) && !Flag(*I,TEXT("IsDead")))
            {
                const FVector Delta=I->GetActorLocation()-Eye;
                if(Delta.SizeSquared()<FMath::Square(10000.0) && FVector::DotProduct(Forward,Delta.GetSafeNormal())>=.70710678 && PlayerOwner->LineOfSightTo(*I)) CachedEnemyLocations.Add(I->GetActorLocation());
            }
        }
    }
    for(const auto& V:CachedEnemyLocations) Dot(V,Danger,3);
    const FVector Goal=M->Phase==TEXT("Crossing")?M->FarBankFeet:M->BridgeheadFeet;
    auto G=MapPoint(Goal);
    if(InMap(G)) { Border(G.X-6,G.Y-6,12,12,M->CheckpointUnlocked()?Olive:Amber); }
    if(M->CheckpointUnlocked())
    {
        const auto CP=MapPoint(M->BridgeheadFeet);
        if(InMap(CP))
        {
            for(int32 I=0;I<20;++I) { const double A=I*2*PI/20,B=(I+1)*2*PI/20;Line(CP.X+9*FMath::Cos(A),CP.Y+9*FMath::Sin(A),CP.X+9*FMath::Cos(B),CP.Y+9*FMath::Sin(B),Olive,2); }
        }
    }
    // Authoritative resource display; no separate UI health/ammo model.
    if(Player)
    {
        const double HP=Number(Player,TEXT("Health")),Loaded=Number(Player,TEXT("LoadedAmmo")),Reserve=Number(Player,TEXT("ReserveAmmo")),Capacity=Number(Player,TEXT("Capacity"));
        Rect(38,915,350,128,Panel);Small(TEXT("SQUAD LEADER"),58,931,Muted);
        Text(FString::Printf(TEXT("%.0f"),HP),58,952,1.65f,HP<=25?Danger:Cream);
        Small(TEXT("HEALTH"),123,964,Muted);Rect(58,1001,306,10,FLinearColor(.15f,.18f,.14f));
        Rect(58,1001,306*FMath::Clamp(HP/100.0,0.0,1.0),10,HP<=25?Danger:Olive);
        Small(FString::Printf(TEXT("ALLIED SQUAD  %d / 2"),M->LivingAllies),58,1021,Muted);
        Rect(1510,884,372,159,Panel);Small(TEXT("M1 GARAND"),1533,901,Muted);
        Text(FString::Printf(TEXT("%02.0f"),Loaded),1533,924,2.7f,Loaded<=2?Amber:Cream);
        Text(FString::Printf(TEXT("/  %02.0f"),Reserve),1639,947,1.45f,Muted);
        Small(TEXT("LOADED                 RESERVE"),1535,985,Muted);
        const int32 Cap=FMath::Clamp(int32(Capacity),1,16);
        for(int32 I=0;I<Cap;++I) Rect(1535+I*21,1006,12,17,I<Loaded?Olive:FLinearColor(.20f,.24f,.19f));
        Small(FString::Printf(TEXT("%d-RD LOAD"),int32(Capacity)),1720,1010,Muted);
        if(Reserve>=0 && Capacity>0) Small(FString::Printf(TEXT("RESERVE  %d x %d  + %d RD"),int32(Reserve)/int32(Capacity),int32(Capacity),int32(Reserve)%int32(Capacity)),1514,1050,Muted);
        if(Name(Player,TEXT("ActionState"))==TEXT("Reloading")) Text(TEXT("RELOADING"),868,778,.9f,Amber);
        else if(Loaded<=0) Text(TEXT("R  RELOAD"),868,778,.9f,Amber);
        if(M->AllowsPlay() || M->Phase==TEXT("Won"))
        { Line(952,540,958,540,Cream);Line(962,540,968,540,Cream);Line(960,532,960,538,Cream);Line(960,542,960,548,Cream); }
    }
    const FString Feedback=M->Feedback;
    if(!Feedback.IsEmpty())
    { Rect(475,845,970,37,Panel);Small(Feedback,491,857,M->Phase==TEXT("Error")?Danger:Amber); }
    Small(TEXT("SHIFT Run   ALT Slow   SPACE Jump   CTRL Crouch   Z Prone   R Reload   F9 Load   F6 Restart"),480,1044,Muted);
    if(M->CheckpointPromptVisible)
    {
        Rect(631,670,658,147,Panel);Rect(631,670,4,147,Olive);
        Text(TEXT("CHECKPOINT  /  G1 SECURED"),659,690,.85f,Olive);
        Text(TEXT("Save your checkpoint?"),659,721,1.3f,Cream);
        Text(TEXT("[ E ]  SAVE      [ ESC ]  LATER"),659,774,.95f,Cream);
    }
    if(M->Phase==TEXT("Ready"))
    {
        Rect(660,440,600,152,Panel);Text(TEXT("G1 BRIDGEHEAD"),692,463,1.5f,Cream);
        Text(TEXT("[ ENTER ]  BEGIN MISSION"),692,527,1.1f,Amber);
    }
    if(M->CheckpointUnlocked() && !M->InsideCheckpoint())
    {
        FVector2D Screen;
        if(PlayerOwner->ProjectWorldLocationToScreen(M->BridgeheadFeet+FVector(0,0,100),Screen) && Screen.X>0 && Screen.X<Canvas->SizeX && Screen.Y>0 && Screen.Y<Canvas->SizeY)
            DrawText(TEXT("CHECKPOINT"),Olive,Screen.X,Screen.Y,GEngine->GetMediumFont(),S);
    }
}
