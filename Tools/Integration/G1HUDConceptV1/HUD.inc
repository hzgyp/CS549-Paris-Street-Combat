void AParisBridgeHUD::DrawHUD()
{
    Super::DrawHUD(); if(!Canvas || !PlayerOwner) return;
    auto* M=AParisBridgeMission::Find(this);auto* Player=Cast<ACharacter>(PlayerOwner->GetPawn());
    if(!M) return;
    if(!bLegacyWidgetRemoved)
    {
        TArray<UUserWidget*> Widgets;
        UWidgetBlueprintLibrary::GetAllWidgetsOfClass(this,Widgets,UUserWidget::StaticClass(),false);
        for(auto* W:Widgets) if(W && W->GetClass()->GetPathName().StartsWith(TEXT("/Game/ParisCombat/UI/CityGameplayV1/WBP_PCParisStatusV1"))) W->RemoveFromParent();
        bLegacyWidgetRemoved=true;
    }
    const FString UIDir=FPaths::ConvertRelativePathToFull(FPaths::Combine(FPlatformProcess::BaseDir(),TEXT("../../UI")));
    if(!bMapLoadAttempted)
    {
        bMapLoadAttempted=true;
        MinimapTexture=FImageUtils::ImportFileAsTexture2D(FPaths::Combine(UIDir,TEXT("g1_minimap.png")));
        if(!MinimapTexture) { UE_LOG(LogTemp,Error,TEXT("PARIS_UX_MINIMAP_MISSING")); }
        else { UE_LOG(LogTemp,Display,TEXT("PARIS_UX_HUD_READY minimap=%dx%d metric_bounds=0,-25000,10000,-15000 legacy_widget_removed=1"),MinimapTexture->GetSizeX(),MinimapTexture->GetSizeY()); }
        checkf(FPaths::FileExists(FPaths::Combine(UIDir,TEXT("Cinzel.ttf"))),TEXT("Packaged Cinzel font required"));
        UE_LOG(LogTemp,Display,TEXT("PARIS_HUD_CONCEPT_READY style=ivory_brass_float_v1 font=Cinzel circular_map=1 authoritative_resources=1"));
    }
    // Canvas requires a UFont even when Slate provides the composite; hold it across GC.
    static TStrongObjectPtr<UFont> Typeface([&]()
    {
        UFont* Font=NewObject<UFont>();Font->FontCacheType=EFontCacheType::Runtime;
        Font->GetMutableInternalCompositeFont()=FCompositeFont(FName(TEXT("Regular")),
            FPaths::Combine(UIDir,TEXT("Cinzel.ttf")),EFontHinting::Default,EFontLoadingPolicy::LazyLoad);
        return Font;
    }());
    const float S=FMath::Min(Canvas->SizeX/1920.f,Canvas->SizeY/1080.f);
    const float OX=(Canvas->SizeX-1920*S)*.5f,OY=(Canvas->SizeY-1080*S)*.5f;
    const FLinearColor Ivory(.95f,.91f,.75f,1),Brass(.77f,.60f,.30f,1),Quiet(.67f,.66f,.52f,1),
        Ally(.56f,.65f,.40f,1),Danger(.92f,.24f,.16f,1),Ink(.004f,.006f,.006f,.80f);
    auto Pt=[&](double X,double Y){return FVector2D(OX+X*S,OY+Y*S);};
    auto Rect=[&](double X,double Y,double W,double H,FLinearColor C){DrawRect(C,OX+X*S,OY+Y*S,W*S,H*S);};
    auto Line=[&](double X,double Y,double XX,double YY,FLinearColor C,float T=1.f)
    {
        DrawLine(OX+X*S,OY+Y*S,OX+XX*S,OY+YY*S,FLinearColor(0,0,0,.65),T*S+1.5*S);
        DrawLine(OX+X*S,OY+Y*S,OX+XX*S,OY+YY*S,C,T*S);
    };
    auto Text=[&](const FString& V,float X,float Y,float Size,FLinearColor C,bool Center=false,int32 Tracking=0)
    {
        FSlateFontInfo Info(Typeface.Get(),Size);Info.LetterSpacing=Tracking;
        FCanvasTextItem Item(Pt(X,Y),FText::FromString(V),Info,C);
        Item.Scale=FVector2D(S,S);Item.bCentreX=Center;
        Item.EnableShadow(FLinearColor(0,0,0,.95),FVector2D(1.2*S,1.8*S));
        Canvas->DrawItem(Item);
        checkf(Item.DrawnSize.X>0 && Item.DrawnSize.Y>0,TEXT("HUD glyph draw required"));
        static bool FirstDrawLogged=false;
        if(!FirstDrawLogged)
        {FirstDrawLogged=true;UE_LOG(LogTemp,Display,TEXT("PARIS_HUD_CINZEL_DRAW runtime_ufont=1 width=%.3f height=%.3f"),Item.DrawnSize.X,Item.DrawnSize.Y);}
    };
    auto Tri=[&](FVector2D A,FVector2D B,FVector2D C,FLinearColor Color)
    {
        FCanvasTriangleItem Item(Pt(A.X,A.Y),Pt(B.X,B.Y),Pt(C.X,C.Y),GWhiteTexture);
        Item.SetColor(Color);Item.BlendMode=SE_BLEND_Translucent;Canvas->DrawItem(Item);
    };
    auto Halo=[&](double X,double Y,double RX,double RY,float Alpha)
    {
        TArray<FCanvasUVTri> Fan;Fan.Reserve(48);
        for(int32 I=0;I<48;++I)
        {
            const double A=2*PI*I/48,B=2*PI*(I+1)/48;FCanvasUVTri T;
            T.V0_Pos=Pt(X,Y);T.V1_Pos=Pt(X+RX*FMath::Cos(A),Y+RY*FMath::Sin(A));T.V2_Pos=Pt(X+RX*FMath::Cos(B),Y+RY*FMath::Sin(B));
            T.V0_UV=T.V1_UV=T.V2_UV=FVector2D::ZeroVector;
            T.V0_Color=FLinearColor(0,0,0,Alpha);T.V1_Color=T.V2_Color=FLinearColor(0,0,0,0);Fan.Add(T);
        }
        FCanvasTriangleItem Item(Fan,GWhiteTexture);Item.BlendMode=SE_BLEND_Translucent;Canvas->DrawItem(Item);
    };
    auto Circle=[&](double X,double Y,double R,FLinearColor C,float Width=1.f)
    {
        const int32 Segments=FMath::Clamp(FMath::CeilToInt(R*1.6),24,160);
        const double Inner=FMath::Max(0.,R-Width*.5),Outer=R+Width*.5;
        TArray<FCanvasUVTri> Mesh;Mesh.Reserve(Segments*6);
        auto Band=[&](double R1,double R2,float Alpha1,float Alpha2)
        {
            for(int32 I=0;I<Segments;++I)
            {
                const double A=2*PI*I/Segments,B=2*PI*(I+1)/Segments;
                const auto P1=Pt(X+R1*FMath::Cos(A),Y+R1*FMath::Sin(A)),P2=Pt(X+R2*FMath::Cos(A),Y+R2*FMath::Sin(A));
                const auto P3=Pt(X+R2*FMath::Cos(B),Y+R2*FMath::Sin(B)),P4=Pt(X+R1*FMath::Cos(B),Y+R1*FMath::Sin(B));
                FLinearColor C1=C,C2=C;C1.A*=Alpha1;C2.A*=Alpha2;
                FCanvasUVTri T;T.V0_UV=T.V1_UV=T.V2_UV=FVector2D::ZeroVector;
                T.V0_Pos=P1;T.V1_Pos=P2;T.V2_Pos=P3;T.V0_Color=C1;T.V1_Color=T.V2_Color=C2;Mesh.Add(T);
                T.V0_Pos=P1;T.V1_Pos=P3;T.V2_Pos=P4;T.V0_Color=T.V2_Color=C1;T.V1_Color=C2;Mesh.Add(T);
            }
        };
        Band(FMath::Max(0.,Inner-.85),Inner,0,1);Band(Inner,Outer,1,1);Band(Outer,Outer+.85,1,0);
        FCanvasTriangleItem Item(Mesh,GWhiteTexture);Item.BlendMode=SE_BLEND_Translucent;Canvas->DrawItem(Item);
    };
    auto Diamond=[&](double X,double Y,double R,FLinearColor C)
    {Line(X,Y-R,X+R,Y,C,1.3);Line(X+R,Y,X,Y+R,C,1.3);Line(X,Y+R,X-R,Y,C,1.3);Line(X-R,Y,X,Y-R,C,1.3);};
    auto Key=[&](const FString& Name,float X,float Y,float W)
    {
        Rect(X,Y,W,33,FLinearColor(0,0,0,.28));
        Line(X,Y,X+W,Y,Ivory);Line(X+W,Y,X+W,Y+33,Ivory);Line(X+W,Y+33,X,Y+33,Ivory);Line(X,Y+33,X,Y,Ivory);
        Text(Name,X+W*.5f,Y+4,16,Ivory,true);
    };

    // The approved composition floats over the real world; no generated scene or cards.
    Halo(250,89,270,76,.36);
    Diamond(76,84,30,Brass);
    if(M->Phase==TEXT("Won")) {Line(64,85,74,94,Ivory,4);Line(74,94,90,73,Ivory,4);}
    else {Line(76,72,76,87,Ivory,2);Rect(74.5,94,3,3,Ivory);}
    Text(TEXT("PARIS  /  G1"),130,41,13,Brass,false,190);
    FString Title=TEXT("ASSEMBLING SQUAD"),Detail=TEXT("PREPARING EQUIPMENT");
    if(M->Phase==TEXT("Ready")){Title=TEXT("CROSS THE RIVER");Detail=TEXT("CROSS BRIDGE C WITH YOUR SQUAD");}
    else if(M->Phase==TEXT("Crossing")){Title=TEXT("CROSS THE RIVER");Detail=TEXT("REACH THE FAR BANK");}
    else if(M->Phase==TEXT("Clearing")){Title=TEXT("SECURE THE BRIDGEHEAD");Detail=FString::Printf(TEXT("%d / 3 GUARDS ELIMINATED"),3-M->LivingDefenders);}
    else if(M->Phase==TEXT("Occupying")){Title=TEXT("OCCUPY THE BRIDGEHEAD");Detail=TEXT("3 / 3 GUARDS ELIMINATED");}
    else if(M->Phase==TEXT("Won")){Title=TEXT("BRIDGEHEAD SECURED");Detail=TEXT("3 / 3 GUARDS ELIMINATED");}
    else if(M->Phase==TEXT("Lost")){Title=TEXT("MISSION LOST");Detail=TEXT("F9 LOAD  /  F6 RESTART");}
    else if(M->Phase==TEXT("Error")){Title=TEXT("MISSION STOPPED");Detail=TEXT("SEE RUN LOG");}
    Text(Title,130,67,21,M->Phase==TEXT("Lost")?Danger:Ivory,false,45);
    Text(Detail,130,102,12,Quiet,false,130);

    // Native triangle fan is the circular clip of the unchanged metric survey.
    const double CX=1742,CY=182,R=136;
    Halo(CX,CY,R+16,R+16,.42);
    if(MinimapTexture && MinimapTexture->GetResource())
    {
        TArray<FCanvasUVTri> Fan;Fan.Reserve(128);
        for(int32 I=0;I<128;++I)
        {
            const double A=2*PI*I/128,B=2*PI*(I+1)/128;FCanvasUVTri T;
            T.V0_Pos=Pt(CX,CY);T.V1_Pos=Pt(CX+R*FMath::Cos(A),CY+R*FMath::Sin(A));T.V2_Pos=Pt(CX+R*FMath::Cos(B),CY+R*FMath::Sin(B));
            T.V0_UV=FVector2D(.5,.5);T.V1_UV=FVector2D(.5+.5*FMath::Cos(A),.5+.5*FMath::Sin(A));T.V2_UV=FVector2D(.5+.5*FMath::Cos(B),.5+.5*FMath::Sin(B));
            T.V0_Color=T.V1_Color=T.V2_Color=FLinearColor(.58f,.54f,.39f,.94f);Fan.Add(T);
        }
        FCanvasTriangleItem Item(Fan,MinimapTexture->GetResource());Item.BlendMode=SE_BLEND_Translucent;Canvas->DrawItem(Item);
    }
    Circle(CX,CY,R+2,Brass,1.5);Circle(CX,CY,R-2,FLinearColor(.8f,.75f,.56f,.50f),.65);
    Line(CX,CY-R-8,CX,CY-R+7,Ivory);Text(TEXT("N"),CX,CY-R+9,13,Ivory,true);
    Text(TEXT("G1"),CX,CY+R+13,15,Ivory,true,60);
    Line(CX-91,CY+R+26,CX-28,CY+R+26,Brass);Line(CX+28,CY+R+26,CX+91,CY+R+26,Brass);
    auto MapPoint=[&](FVector V){return FVector2D(CX-R+V.X/10000*(2*R),CY-R+(-15000-V.Y)/10000*(2*R));};
    auto InMap=[&](FVector2D P,double Margin=8.0){return FVector2D::DistSquared(P,FVector2D(CX,CY))<=FMath::Square(R-Margin);};
    auto Dot=[&](FVector V,FLinearColor C,float Size){const auto P=MapPoint(V);if(InMap(P)) {Rect(P.X-Size-1,P.Y-Size-1,2*Size+2,2*Size+2,Ink);Rect(P.X-Size,P.Y-Size,2*Size,2*Size,C);}};
    for(TActorIterator<ACharacter> I(GetWorld());I;++I)
        if((I->ActorHasTag(TEXT("G1_Ally1")) || I->ActorHasTag(TEXT("G1_Ally2"))) && !Flag(*I,TEXT("IsDead"))) Dot(I->GetActorLocation(),Ally,3);
    if(Player)
    {
        const auto P=MapPoint(Player->GetActorLocation());const double Angle=FMath::DegreesToRadians(PlayerOwner->GetControlRotation().Yaw);
        if(InMap(P,14))
        {
            const FVector2D F(FMath::Cos(Angle),-FMath::Sin(Angle)),Side(-F.Y,F.X);
            const auto A=P+F*10,B=P-F*6+Side*6,C=P-F*6-Side*6;
            Tri(A,B,C,Ivory);Line(B.X,B.Y,C.X,C.Y,Ink,1);
        }
        if(GetWorld()->GetTimeSeconds()>=NextMarkerRefresh)
        {
            NextMarkerRefresh=GetWorld()->GetTimeSeconds()+.2;CachedEnemyLocations.Reset();
            FVector Eye;FRotator View;PlayerOwner->GetPlayerViewPoint(Eye,View);const FVector Forward=View.Vector();
            for(TActorIterator<ACharacter> I(GetWorld());I;++I)
                if((I->ActorHasTag(TEXT("G1_German1")) || I->ActorHasTag(TEXT("G1_German2")) || I->ActorHasTag(TEXT("G1_German3"))) && !Flag(*I,TEXT("IsDead")))
                {
                    const FVector Delta=I->GetActorLocation()-Eye;
                    if(Delta.SizeSquared()<FMath::Square(10000.0) && FVector::DotProduct(Forward,Delta.GetSafeNormal())>=.70710678 && PlayerOwner->LineOfSightTo(*I)) CachedEnemyLocations.Add(I->GetActorLocation());
                }
        }
    }
    for(const auto& V:CachedEnemyLocations) Dot(V,Danger,2.5);
    const auto Goal=MapPoint(M->Phase==TEXT("Crossing")?M->FarBankFeet:M->BridgeheadFeet);
    if(InMap(Goal,12)){Circle(Goal.X,Goal.Y,8,Brass,1.5);Diamond(Goal.X,Goal.Y,4,Brass);}

    if(Player)
    {
        const double HP=Number(Player,TEXT("Health")),Loaded=Number(Player,TEXT("LoadedAmmo")),Reserve=Number(Player,TEXT("ReserveAmmo")),Capacity=Number(Player,TEXT("Capacity"));
        Halo(218,989,226,89,.34);Halo(1743,977,180,107,.36);
        const auto HealthColor=HP<=25?Danger:Ivory;
        Rect(55,946,10,31,HealthColor);Rect(44.5,956.5,31,10,HealthColor);
        Text(FString::Printf(TEXT("%.0f"),HP),92,931,31,HealthColor);
        const double Fraction=FMath::Clamp(HP/100.0,0.0,1.0);
        for(int32 I=0;I<6;++I)
        {
            const double X=191+I*34;Rect(X,956,28,9,FLinearColor(.20f,.20f,.16f,.75));
            Rect(X,956,28*FMath::Clamp(Fraction*6-I,0.0,1.0),9,HealthColor);
        }
        auto Soldier=[&](float X,bool Alive)
        {
            const auto C=Alive?Ally:FLinearColor(.28f,.29f,.25f,.8f);
            for(int32 I=0;I<12;++I){const double A=2*PI*I/12,B=2*PI*(I+1)/12;Tri(FVector2D(X,1007),FVector2D(X+3*FMath::Cos(A),1007+3*FMath::Sin(A)),FVector2D(X+3*FMath::Cos(B),1007+3*FMath::Sin(B)),C);}
            Tri(FVector2D(X-5,1014),FVector2D(X+5,1014),FVector2D(X+3,1027),C);
            Tri(FVector2D(X-5,1014),FVector2D(X+3,1027),FVector2D(X-3,1027),C);
            Tri(FVector2D(X-5,1014),FVector2D(X-7,1025),FVector2D(X-4,1025),C);
            Tri(FVector2D(X+5,1014),FVector2D(X+4,1025),FVector2D(X+7,1025),C);
            Tri(FVector2D(X-3,1026),FVector2D(X,1026),FVector2D(X-4,1038),C);Rect(X-5,1036,3,2,C);
            Tri(FVector2D(X,1026),FVector2D(X+3,1026),FVector2D(X+4,1038),C);Rect(X+2,1036,3,2,C);
        };
        Soldier(55,M->LivingAllies>=1);Soldier(82,M->LivingAllies>=2);
        Text(FString::Printf(TEXT("SQUAD %d / 2"),M->LivingAllies),115,1015,14,Ivory,false,85);

        Text(TEXT("M1 GARAND"),1623,888,13,Ivory,false,60);
        // Original vector silhouette, aligned with the actual rifle identity.
        const FVector2D A(1751,906),B(1784,896),C(1813,896),D(1816,902),E(1788,902),F(1765,914);
        Tri(A,B,F,Quiet);Tri(B,E,F,Quiet);Tri(B,C,E,Quiet);Tri(C,D,E,Quiet);
        Rect(1810,897,57,3,Quiet);Rect(1860,893,3,5,Quiet);Line(1800,903,1798,909,Quiet,1.3);Line(1798,909,1806,909,Quiet,1.3);
        Text(FString::Printf(TEXT("%02.0f"),Loaded),1623,922,50,Loaded<=2?Brass:Ivory);
        Line(1731,943,1721,982,Quiet,1.2);Text(FString::Printf(TEXT("%02.0f"),Reserve),1756,948,27,Quiet);
        Text(TEXT("LOADED"),1626,997,10,Quiet,false,90);Text(TEXT("RESERVE"),1755,997,10,Quiet,false,90);
        const int32 Cap=FMath::Clamp(int32(Capacity),1,16);const double Slot=224.0/Cap;
        for(int32 I=0;I<Cap;++I) Rect(1626+I*Slot,1024,FMath::Min(14.,Slot-5),17,I<Loaded?Ivory:FLinearColor(.26f,.26f,.22f,.8f));
        if(Name(Player,TEXT("ActionState"))==TEXT("Reloading")) Text(TEXT("RELOADING"),1742,852,13,Brass,true,100);
        else if(Loaded<=0) Text(TEXT("R  RELOAD"),1742,852,13,Brass,true,100);
        if(M->AllowsPlay())
        {Line(953,540,957,540,FLinearColor(.95,.91,.75,.6));Line(963,540,967,540,FLinearColor(.95,.91,.75,.6));}
    }

    if(M->CheckpointPromptVisible)
    {
        Halo(960,822,251,105,.48);
        Circle(960,766,25,Brass,1.5);Line(867,766,927,766,Brass);Line(993,766,1053,766,Brass);
        Line(950,755,967,755,Ivory,1.8);Line(967,755,971,759,Ivory,1.8);Line(971,759,971,778,Ivory,1.8);
        Line(971,778,950,778,Ivory,1.8);Line(950,778,950,755,Ivory,1.8);
        Rect(956,756,9,7,Ivory);Line(955,768,967,768,Ivory);Line(955,768,955,776,Ivory);Line(967,768,967,776,Ivory);
        Text(TEXT("SAVE CHECKPOINT?"),960,804,20,Ivory,true,40);
        Key(TEXT("E"),805,851,32);Text(TEXT("SAVE"),853,856,15,Ivory,false,60);
        Key(TEXT("ESC"),986,851,49);Text(TEXT("LATER"),1052,856,15,Ivory,false,60);
    }
    if(M->Phase==TEXT("Ready"))
    {
        Halo(960,774,240,80,.34);
        Text(TEXT("G1 BRIDGEHEAD"),960,740,19,Ivory,true,100);
        Key(TEXT("ENTER"),811,792,80);Text(TEXT("BEGIN MISSION"),910,797,15,Ivory,false,50);
    }
    // Feedback is ephemeral and belongs to the current world; no stale tutorial bar.
    static TWeakObjectPtr<AParisBridgeMission> FeedbackWorld;
    static FString LastFeedback;static double FeedbackAt=0;
    const double Now=GetWorld()->GetTimeSeconds();
    if(FeedbackWorld.Get()!=M){FeedbackWorld=M;LastFeedback.Empty();FeedbackAt=Now;}
    if(LastFeedback!=M->Feedback){LastFeedback=M->Feedback;FeedbackAt=Now;}
    const bool ProneNotice=Player && Number(Player,TEXT("DesiredPosture"))==2 && LastFeedback.Contains(TEXT("Prone"));
    if(!LastFeedback.IsEmpty() && M->Phase!=TEXT("Ready") && (Now-FeedbackAt<5 || ProneNotice || M->Phase==TEXT("Error") || M->Phase==TEXT("Lost")))
    {
        const bool Routine=LastFeedback.StartsWith(TEXT("G1 secured")) || LastFeedback.StartsWith(TEXT("Cross"));
        if(!Routine) {Halo(960,916,370,29,.30);Text(LastFeedback.Left(90),960,906,12,M->Phase==TEXT("Error")?Danger:Quiet,true);}
    }
    if(M->CheckpointUnlocked() && !M->InsideCheckpoint())
    {
        FVector2D Screen;
        if(PlayerOwner->ProjectWorldLocationToScreen(M->BridgeheadFeet+FVector(0,0,100),Screen) && Screen.X>100*S && Screen.X<Canvas->SizeX-100*S && Screen.Y>80*S && Screen.Y<Canvas->SizeY-130*S)
        {const float X=(Screen.X-OX)/S,Y=(Screen.Y-OY)/S;Diamond(X,Y,7,Brass);Text(TEXT("CHECKPOINT"),X,Y+12,12,Brass,true,60);}
    }
}
