// One lower-right equipment display. Uses the existing gameplay session read-only.
void DrawEquipmentPanel(AParisBridgeHUD* H,AParisBridgePlayerController* PC,const ParisTacticalEquipment::FEquipmentSession& E){
 APawn* Pawn=PC->GetPawn();if(!Pawn)return;FPaint P(H,true);
 int32 W=0,Height=0;PC->GetViewportSize(W,Height);const double Base=FMath::Min(W/1920.,Height/1080.);
 // Anchor to the safe lower-right edge when HUD scale changes; growing the
 // display extends left/up instead of clipping its counts off the viewport.
 P.X=(W-1920*Base)*.5+1872*Base-1872*P.S;
 P.Y=(Height-1080*Base)*.5+1064*Base-1064*P.S;
 P.Box(1492,812,380,236,FLinearColor(.009,.015,.012,.38));
 const bool Rifle=E.SelectedSlot==0;const auto RifleColor=Rifle?Ivory:Muted;
 P.Line(1508,852,1856,852,Rifle?Brass:Muted,Rifle?2:1);
 P.Text(TEXT("M1 GARAND"),1510,820,18,RifleColor);
 P.Stroke(1784,825,{{0,7},{21,0},{46,0},{47,5},{25,5},{7,17},{0,7}},RifleColor,2);
 P.Line(1829,826,1854,826,RifleColor,3);P.Line(1820,832,1819,837,RifleColor,2);
 const int32 Loaded=FMath::Max(0,int32(Num(Pawn,TEXT("LoadedAmmo"))));
 const int32 Reserve=FMath::Max(0,int32(Num(Pawn,TEXT("ReserveAmmo"))));
 P.Text(FString::Printf(TEXT("%02d"),Loaded),1510,860,48,Loaded<=2?Brass:RifleColor);
 P.Line(1638,873,1627,905,Muted,1.2);
 P.Text(FString::Printf(TEXT("%02d"),Reserve),1660,876,30,RifleColor);
 P.Text(TEXT("LOADED"),1512,918,12,Muted);P.Text(TEXT("RESERVE"),1662,918,12,Muted);
 const int32 Capacity=FMath::Clamp(int32(Num(Pawn,TEXT("Capacity"))),1,16);const double Slot=224./Capacity;
 for(int32 I=0;I<Capacity;++I)P.Box(1512+I*Slot,942,FMath::Min(14.,Slot-5),9,I<Loaded?RifleColor:Fill);
 if(ActionState(Pawn)==TEXT("Reloading"))P.Text(TEXT("RELOADING"),1740,889,13,Brass);
 else if(Rifle&&Loaded==0)P.Text(TEXT("R  RELOAD"),1740,889,13,Brass);
 for(int32 SlotIndex=1;SlotIndex<=2;++SlotIndex){
  const double X=1508+(SlotIndex-1)*192;const bool Active=E.SelectedSlot==SlotIndex;
  const int32 Count=SlotIndex==1?E.Frag:E.Smoke;const auto Color=Count>0?(Active?Ivory:Muted):Muted;
  if(Active)P.Box(X-4,972,164,72,FLinearColor(.12,.15,.10,.65));
  P.Icon(SlotIndex==1?12:13,X+18,1010,Color);
  P.Text(SlotIndex==1?TEXT("FRAG"):TEXT("SMOKE"),X+42,979,17,Color);
  P.Text(FString::FromInt(Count),X+120,1005,27,Color);
  P.Line(X,1044,X+156,1044,Active?Brass:Muted,Active?3:1);
 }
 P.Text(TEXT("MOUSE WHEEL TO SWITCH"),1510,1052,13,Muted);
 auto* Mission=AParisBridgeMission::Find(PC);if(ParisTutorial::Enabled()&&Mission&&ParisTutorial::CombatStarted(Mission)){P.Box(1492,770,380,34,FLinearColor(.009,.015,.012,.38));P.Text(FString::Printf(TEXT("MEDICAL KITS %d/2  |  HOLD H"),ParisMedicalKits::Count(PC->GetWorld())),1510,777,16,Muted);}
}
