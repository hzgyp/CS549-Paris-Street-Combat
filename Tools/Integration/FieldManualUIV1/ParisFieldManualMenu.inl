bool DrawMenu(AParisBridgeHUD* H,AParisBridgeMission* M){
 auto* PC=Cast<AParisBridgePlayerController>(H->PlayerOwner);if(!IsOpen(PC))return false;
 auto& U=State(PC);FPaint P(H);
 P.Box(0,0,1920,1080,FLinearColor(.003,.008,.005,.58));
 P.Box(162,90,1596,896,FLinearColor(.014,.025,.021,.94));
 P.Outline(162,90,1596,896,FLinearColor(.42,.43,.32,.65));P.Corners(172,100,1576,876);
 P.Title(TEXT("PARIS STREET COMBAT"),216,132,42);P.Label(TEXT("G1 BRIDGEHEAD  /  GAME PAUSED"),218,195,16,Brass);
 P.Line(216,230,1702,230,FLinearColor(.40,.42,.31,.7));
 for(int32 I=0;I<4;++I)P.Navigation(Tabs[I],NavX[I],NavY,NavW[I],U.Page==I);
 P.Line(610,260,610,902,FLinearColor(.40,.42,.31,.7));
 const FString Names[]={M->Phase==TEXT("Ready")?TEXT("BEGIN MISSION"):TEXT("RETURN TO GAME"),TEXT("LOAD CHECKPOINT"),TEXT("RESTART MISSION"),TEXT("CONTROLS / HELP"),TEXT("EXIT GAME")};
 for(int32 I=0;I<5;++I){const double Y=SideY+I*SideStep;const bool Enabled=I!=1||U.CanLoad;const auto C=Enabled?(U.Action==I?Brass:Ivory):Muted;
  if(U.Action==I){P.Line(SideX-13,Y+6,SideX-13,Y+57,Brass,3);P.Box(SideX,Y,SideW,SideH,FLinearColor(.11,.13,.09,.32));}
  P.Icon(I,SideX+17,Y+30,C);P.Title(Names[I],SideX+58,Y+17,22,C);P.Line(SideX+57,Y+69,SideX+SideW,Y+69,FLinearColor(.3,.35,.28,.35));
  if(I==1)P.Text(U.CanLoad?TEXT("Checkpoint available"):TEXT("No valid checkpoint"),SideX+58,Y+48,16,U.CanLoad?Green:Muted);
 }
 P.Key(TEXT("ESC"),218,930,48);P.Label(TEXT("RETURN"),280,940,16,Brass);
 P.Line(660,916,1702,916,FLinearColor(.40,.42,.31,.7));
 if(U.Page==2){P.Key(TEXT("1 - 5"),660,934,57);P.Label(TEXT("HELP CATEGORY"),728,941,14);}
 else {P.Icon(U.Page==0?17:U.Page==1?7:16,682,948,Muted);P.Label(TEXT("FIELD MANUAL"),715,941,14);}
 P.Key(TEXT("LEFT / RIGHT"),935,934,140);P.Label(TEXT("PAGE"),1087,941,14);
 P.Key(TEXT("ARROWS / MOUSE"),1162,934,172);P.Label(TEXT("SELECT"),1346,941,14);
 P.Key(TEXT("ENTER"),1460,934,78);P.Label(TEXT("ACTIVATE"),1550,941,14);
 const TCHAR* Headings[]={TEXT("MISSION BRIEFING"),TEXT("PLAYER & SQUAD"),TEXT("CONTROLS"),TEXT("SETTINGS")};
 const TCHAR* Subheads[]={TEXT("G1 bridgehead / current objective"),TEXT("Personnel, resources & equipment"),TEXT("Movement, weapons & field actions"),TEXT("Display & guidance")};
 P.Icon(U.Page==0?17:U.Page==1?7:U.Page==2?3:16,683,303,Brass);
 P.Label(TEXT("FIELD MANUAL"),721,261,14,Muted);P.Title(Headings[U.Page],721,284,43);P.Text(Subheads[U.Page],722,341,22,Muted);
 if(U.Page==0){
  const int32 Cleared=FMath::Clamp(3-M->LivingDefenders,0,3);const bool Secured=M->CheckpointUnlocked();
  P.Label(TEXT("PRIMARY OBJECTIVE"),660,402,17,Brass);P.Title(Secured?TEXT("G1 BRIDGEHEAD SECURED"):TEXT("ELIMINATE THE G1 GUARDS"),660,434,30);
  for(int32 I=0;I<3;++I){P.Circle(684+I*67,512,21,I<Cleared?Brass:Muted);P.Write(FString::FromInt(I+1),684+I*67,496,24,I<Cleared?Brass:Muted,2,0,true);}
  P.Text(FString::Printf(TEXT("%d / 3 guards eliminated"),Cleared),909,495,27,Secured?Green:Ivory);
  P.Bar(660,555,1042,Cleared/3.,Brass);P.Line(660,593,1702,593,FLinearColor(.3,.35,.28,.6));
  P.Icon(17,681,644,Brass);P.Label(TEXT("ROUTE GUIDANCE"),721,611,17,Brass);P.Text(TEXT("Cross the bridge with your squad to reach G1."),721,643,24);
  P.Text(TEXT("Only complete enemy elimination finishes this objective."),721,678,20,Muted);
  P.Line(660,725,1702,725,FLinearColor(.3,.35,.28,.6));P.Icon(Secured?15:18,681,775,Secured?Green:Muted);
  P.Label(TEXT("CHECKPOINT"),721,744,17,Brass);P.Text(Secured?TEXT("Unlocked: enter the gold circle and press E to save."):TEXT("Locked: eliminate all three registered G1 guards."),721,776,23);
  APawn* Player=PC->GetPawn().Get();if(Player)P.Text(FString::Printf(TEXT("G1 checkpoint distance: %.1f m"),FVector::Dist2D(Player->GetActorLocation(),M->BridgeheadFeet)/100),721,812,20,Muted);
  P.Text(TEXT("Clearing G1 does not remove armed mines or live grenades."),660,872,20,Brass);
 }else if(U.Page==1){
  const TCHAR* IDs[]={TEXT("Player"),TEXT("Ally1"),TEXT("Ally2")};APawn* Player=PC->GetPawn().Get();
  for(int32 I=0;I<3;++I){auto* C=Actor(PC->GetWorld(),IDs[I]);const double Y=407+I*151;
   P.Circle(688,Y+40,25,Brass);P.Write(FString::FromInt(I+1),688,Y+23,27,Brass,2,0,true);
   P.Title(I==0?TEXT("PLAYER"):FString::Printf(TEXT("ALLIED %d"),I),733,Y+2,29);P.Label(I==0?TEXT("M1 GARAND"):TEXT("SQUAD MEMBER"),735,Y+43,15,Muted);
   if(!C){P.Text(TEXT("Unavailable"),1050,Y+40,23,Muted);continue;}const bool Gone=Dead(C);const auto CHealth=Gone?Red:Green;
   P.Text(FString::Printf(TEXT("%.0f HEALTH  /  %s"),Num(C,TEXT("Health")),Gone?TEXT("DEAD"):TEXT("ALIVE")),734,Y+76,20,CHealth);P.Bar(734,Y+109,262,Num(C,TEXT("Health"))/100,CHealth);
   P.Label(I==0?TEXT("POSTURE"):TEXT("DISTANCE"),1050,Y+9,15);P.Text(I==0?Posture(C):FString::Printf(TEXT("%.1f m"),Player?FVector::Dist2D(Player->GetActorLocation(),C->GetActorLocation())/100:0),1050,Y+39,22);
   P.Label(TEXT("ACTION"),1270,Y+9,15);P.Text(ActionState(C),1270,Y+39,21);
   P.Label(TEXT("AMMUNITION"),1487,Y+9,15);P.Write(FString::Printf(TEXT("%.0f / %.0f"),Num(C,TEXT("LoadedAmmo")),Num(C,TEXT("ReserveAmmo"))),1487,Y+37,29,Ivory,2);P.Text(TEXT("loaded / reserve"),1487,Y+79,16,Muted);
   P.Line(660,Y+136,1702,Y+136,FLinearColor(.3,.35,.28,.6));
  }
  auto& E=ParisTacticalEquipment::Session(PC->GetWorld());P.Label(TEXT("YOUR EQUIPMENT"),660,872,17,Brass);P.Icon(12,1013,879,Brass);P.Text(FString::Printf(TEXT("G   FRAG  %d"),E.Frag),1047,863,23);P.Icon(13,1320,879,Brass);P.Text(FString::Printf(TEXT("Q   SMOKE  %d"),E.Smoke),1354,863,23);
 }else if(U.Page==2){
  for(int32 I=0;I<5;++I)P.Navigation(Groups[I],GroupX+I*GroupStep,GroupY,GroupW,U.Help==I);
  P.Line(660,417,1702,417,FLinearColor(.40,.42,.31,.7));
  const auto& Rows=Help[U.Help];const bool Movement=U.Help==0;
  if(Movement){P.Label(TEXT("MOVEMENT"),660,491,16,Brass);P.Text(TEXT("Get around"),660,524,17,Muted);P.Text(TEXT("the battlefield"),660,547,17,Muted);P.Line(802,432,802,680,FLinearColor(.3,.35,.28,.6));P.Line(660,698,1702,698,FLinearColor(.40,.42,.31,.7));P.Label(TEXT("STANCE"),660,780,16,Brass);P.Text(TEXT("Adapt to"),660,813,17,Muted);P.Text(TEXT("the ground"),660,836,17,Muted);P.Line(802,712,802,894,FLinearColor(.3,.35,.28,.6));}
  for(int32 I=0;I<Rows.Num();++I){const double Y=430+I*63+(Movement&&I>=4?25:0);const double TX=Movement?895:758,IX=Movement?847:705;
   int32 Sym=Movement?5+I:U.Help==1?(I==0?6:1):U.Help==2?(I==0?12:I==1?13:4):U.Help==3?(I==0?14:I==1?16:4):(I==0?15:I==1?1:I==2?2:I==3?3:7);
   P.Icon(Sym,IX,Y+24);P.Write(Rows[I].Name,TX,Y+1,25,Ivory,2);P.Text(Rows[I].Detail,TX,Y+32,19,Muted);
   const FString Binding(Rows[I].Key);if(Binding==TEXT("W A S D")){const TCHAR* K[]={TEXT("W"),TEXT("A"),TEXT("S"),TEXT("D")};for(int32 J=0;J<4;++J)P.Key(K[J],1490+J*49,Y+10,39);}
   else {const double Width=FMath::Max(42.,Binding.Len()*12.+24);P.Key(Binding,1682-Width,Y+10,Width);}
   P.Line(Movement?823:660,Y+61,1702,Y+61,FLinearColor(.3,.35,.28,.6));
  }
  const double Note=430+Rows.Num()*63+37;
  if(U.Help==1)P.Text(TEXT("Use the existing reticle; full aim-down-sights is not implemented."),660,Note,20,Muted);
  if(U.Help==2){P.Text(TEXT("Frag blasts can hurt you and your allies. Smoke does not stop bullets."),660,Note,20,Brass);P.Text(TEXT("Grenades are finite. A released frag uses a 3.5-second fuse."),660,Note+39,20,Muted);}
  if(U.Help==3)P.Text(TEXT("A discovered mine must be visible. Walls and smoke block interaction."),660,Note,20,Brass);
 }else{
  P.Label(TEXT("OPERATION HINTS"),660,386,17,Brass);P.Button(Detailed?TEXT("DETAILED"):TEXT("COMPACT"),660,420,300,false);
  P.Text(TEXT("Detailed adds first-use guidance; context actions always remain visible."),1000,434,19,Muted);
  P.Line(660,508,1702,508,FLinearColor(.3,.35,.28,.6));P.Label(TEXT("HUD SIZE"),660,528,17,Brass);
  const TCHAR* Labels[]={TEXT("COMPACT 85%"),TEXT("MEDIUM 92.5%"),TEXT("STANDARD 100%")};P.Button(Labels[ScaleIndex],660,560,300,false);
  P.Text(TEXT("Changes the combat HUD; menu text stays readable."),1000,574,20,Muted);
  P.Line(660,655,1702,655,FLinearColor(.3,.35,.28,.6));P.Icon(16,680,714,Brass);P.Text(TEXT("Preferences apply for this session and do not alter your checkpoint."),721,703,20,Muted);
 }
 if(!U.Toast.IsEmpty())P.Text(U.Toast,660,887,19,Brass);
 if(!U.Confirm.IsEmpty()){
  P.Box(0,0,1920,1080,FLinearColor(0,0,0,.68));P.Box(610,375,700,350,Panel);P.Outline(610,375,700,350,Muted);P.Corners(620,385,680,330);
  P.Label(TEXT("CONFIRM ACTION"),670,403,15,Brass);P.Title(U.Confirm==TEXT("Load")?TEXT("LOAD CHECKPOINT?"):U.Confirm==TEXT("Restart")?TEXT("RESTART MISSION?"):TEXT("EXIT GAME?"),670,439,30);
  P.Text(TEXT("Progress since the last checkpoint will be lost."),670,513,22,Muted);P.Button(TEXT("CONFIRM"),705,617,240,U.ModalChoice==0);P.Button(TEXT("CANCEL"),975,617,240,U.ModalChoice==1);
 }
 return true;
}
