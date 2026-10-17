// Read-only presentation derived from the original finite medicine/snapshot state.
// No additional lesson gate, reward, saved flag, treatment or pickup transaction.
bool Guidance(UWorld* W,FGuidance& Out){
 Out=FGuidance();
 if(!W||!ParisTutorial::Enabled()||!LivePlay(W))return false;
 auto* M=AParisBridgeMission::Find(W);auto* P=UGameplayStatics::GetPlayerCharacter(W,0);
 if(!M||!ParisTutorial::CombatStarted(M)||!Alive(P))return false;
 auto& S=State(W);const double Now=W->GetTimeSeconds();
 auto* PC=UGameplayStatics::GetPlayerController(W,0);if(!PC)return false;
 FVector Eye;FRotator View;PC->GetPlayerViewPoint(Eye,View);
 bool EnemyDrop=false;double Nearest=FMath::Square(1800.);int Marker=-1;
 for(int I=0;I<4;++I){const auto& A=S.Sources[I];
  if(A.State!=Claim::Available||!A.Located||!A.Visual.IsValid())continue;
  if(I<3)EnemyDrop=true;
  const FVector At=A.Position+FVector(0,0,12);
  const double Distance=FVector::DistSquared(P->GetActorLocation(),At);
  if(Distance>Nearest||FVector::DotProduct(View.Vector(),(At-Eye).GetSafeNormal())<.10)continue;
  FCollisionQueryParams Q(SCENE_QUERY_STAT(ParisMedicalGuidance),true,P);
  for(const auto& V:S.Sources)if(V.Visual.IsValid())Q.AddIgnoredActor(V.Visual.Get());
  if(I<3)if(auto* Enemy=Actor(W,Ids[I]))Q.AddIgnoredActor(Enemy);
  FHitResult Hit;if(ParisTacticalEquipment::Occluded(W,Eye,At)||W->LineTraceSingleByChannel(Hit,Eye,At,ECC_Visibility,Q))continue;
  Marker=I;Nearest=Distance;
 }
 if(Marker>=0){Out.HasPouch=true;Out.PouchLocation=S.Sources[Marker].Position+FVector(0,0,65);Out.PickupReady=S.Held<ParisMedicalPolicy::Capacity&&Target(W,S)==Marker;}
 if(S.Treating){
  Out.Heading=TEXT("FIELD TREATMENT");Out.Action=Hint(W);
  Out.Detail=TEXT("Keep H held. Moving, firing or taking damage cancels treatment.");
  Out.TreatmentProgress=Progress(W);return true;
 }
 const bool Feedback=S.NoticeUntil>Now&&!S.Notice.IsEmpty()&&
  !S.Notice.StartsWith(TEXT("MEDICAL KIT DROPPED"))&&!S.Notice.StartsWith(TEXT("MEDICAL KIT +1"));
 if(Feedback){
  Out.Heading=TEXT("FIELD TREATMENT");Out.Action=S.Notice;
  Out.Detail=S.Notice==TEXT("TREATMENT COMPLETE")?
   TEXT("One kit used. Each kit restores up to 50 health."):
   S.Notice==TEXT("NO MEDICAL KITS")?TEXT("Look for kits on fallen guards and at limited supply points."):
   S.Notice==TEXT("MEDICAL KITS FULL")?TEXT("Carry up to 2. Use one after taking damage to make room."):
   S.Notice==TEXT("HEALTH ALREADY FULL")?TEXT("Keep your kit for later. Full health does not spend it."):
   TEXT("Treatment uses a kit only when it finishes successfully.");
  return true;
 }
 // Mission completion retires unfinished teaching, without disabling ordinary medicine.
 if(M->Phase==TEXT("Won"))return Out.HasPouch;
 if(S.Used==0&&S.Held>0){
  Out.Heading=S.NoticeUntil>Now&&S.Notice.StartsWith(TEXT("MEDICAL KIT +1"))?TEXT("MEDICAL KIT ACQUIRED"):TEXT("HOW TO TREAT YOURSELF");
  if(Num(P,TEXT("Health"))>=Num(P,TEXT("MaxHealth"))){
   Out.Action=TEXT("KIT STORED  |  HOLD H 3s WHEN INJURED");
   Out.Detail=TEXT("Full health does not spend a kit. Carry up to 2.");
  }else if(ParisTacticalEquipment::Session(W).SelectedSlot!=0){
   Out.Action=TEXT("WHEEL: SELECT RIFLE, THEN HOLD H 3s");
   Out.Detail=TEXT("Stay still on the ground. Each kit restores up to 50 health.");
  }else if(!P->GetCharacterMovement()->IsMovingOnGround()){
   Out.Action=TEXT("LAND AND STOP BEFORE TREATMENT");
   Out.Detail=TEXT("Then hold H for 3 seconds. Each kit restores up to 50 health.");
  }else{
   Out.Action=TEXT("STOP MOVING + HOLD H FOR 3 SECONDS");
   Out.Detail=TEXT("Restores up to 50 health. Release H or take damage to cancel.");
  }
  return true;
 }
 if(S.Used==0&&S.Held==0&&EnemyDrop){
  Out.Heading=TEXT("MEDICAL KIT DROPPED");
  Out.Action=TEXT("APPROACH THE POUCH, AIM + PRESS E");
  Out.Detail=TEXT("Kits are limited. Carry up to 2; each restores up to 50 health.");
 }
 return Out.HasPouch||!Out.Action.IsEmpty();
}
