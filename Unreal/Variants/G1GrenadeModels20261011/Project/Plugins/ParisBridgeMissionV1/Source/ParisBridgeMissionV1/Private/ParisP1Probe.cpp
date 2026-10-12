// Finite opt-in diagnostics: ordinary engine inputs, no pose/resource/AI writes.
#include "ParisTeamP1.h"
#include "ParisBridgeMission.h"
#include "ParisCombatUI.h"
#include "ParisGameplayAV.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Animation/BlendSpace.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Dom/JsonObject.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "InputKeyEventArgs.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"
#include "HAL/FileManager.h"
#include "Serialization/JsonSerializer.h"
#include "UObject/UnrealType.h"
#include "UnrealClient.h"

namespace ParisP1Probe {
namespace {
FString Out,Step=TEXT("ready"),Generation;FDelegateHandle Handle;double Begin=0,Since=0;int32 Count=0;bool Finished=false;
TArray<TSharedPtr<FJsonValue>> Checks;TSharedPtr<FJsonObject> Result=MakeShared<FJsonObject>();
double Num(const UObject* O,const TCHAR* N) {const auto* P=O?FindFProperty<FNumericProperty>(O->GetClass(),N):nullptr;if(!P)return -9999;const void* V=P->ContainerPtrToValuePtr<void>(O);return P->IsFloatingPoint()?P->GetFloatingPointPropertyValue(V):double(P->GetSignedIntPropertyValue(V));}
void Tap(APlayerController* PC,FKey K){PC->InputKey(FInputKeyEventArgs::CreateSimulated(K,IE_Pressed,1));PC->InputKey(FInputKeyEventArgs::CreateSimulated(K,IE_Released,0));if((K==EKeys::F6||K==EKeys::F9)&&!ParisCombatUI::Confirmation(PC).IsEmpty()){PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::Left,IE_Pressed,1));PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::Left,IE_Released,0));PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::Enter,IE_Pressed,1));PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::Enter,IE_Released,0));}}
void Stage(const TCHAR* S){Step=S;Since=FPlatformTime::Seconds();}
void Finish(const FString& Status) {
 if(Finished)return;Finished=true;Result->SetStringField(TEXT("status"),Status);Result->SetStringField(TEXT("scope"),TEXT("Finite native engine input and actual loaded asset inventory; no human acceptance or complete ADS/en-bloc presentation claim."));Result->SetArrayField(TEXT("checks"),Checks);Result->SetNumberField(TEXT("wall_seconds"),FPlatformTime::Seconds()-Begin);
 FString S;auto Writer=TJsonWriterFactory<>::Create(&S);FJsonSerializer::Serialize(Result.ToSharedRef(),Writer);FFileHelper::SaveStringToFile(S,*(Out/TEXT("RESULT.json")));FPlatformMisc::RequestExit(false);
}
bool Check(bool B,const FString& Label){auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("name"),Label);O->SetBoolField(TEXT("pass"),B);Checks.Add(MakeShared<FJsonValueObject>(O));if(!B)Finish(TEXT("failed_")+Label);return B;}
void Inventory(UWorld* W,ACharacter* P,const TCHAR* Label) {
 auto R=MakeShared<FJsonObject>();TArray<TSharedPtr<FJsonValue>> Objects;
 for(TFieldIterator<FProperty> I(P->GetClass());I;++I) {
  if(!I->GetName().Contains(TEXT("Reload"))&&!I->GetName().Contains(TEXT("Aim"))&&!I->GetName().Contains(TEXT("Pose")))continue;
  auto Row=MakeShared<FJsonObject>();Row->SetStringField(TEXT("field"),I->GetName());FString Value;I->ExportText_InContainer(0,Value,P,P,P,PPF_None);Row->SetStringField(TEXT("value"),Value);Objects.Add(MakeShared<FJsonValueObject>(Row));
 }
 R->SetArrayField(TEXT("properties"),Objects);TArray<TSharedPtr<FJsonValue>> Meshes;
 for(TActorIterator<AActor> I(W);I;++I) {
  if(*I!=P&&I->GetOwner()!=P&&!I->GetClass()->GetName().Contains(TEXT("FPUpperBody")))continue;
  TArray<USkeletalMeshComponent*> Components;I->GetComponents(Components);
  for(auto* C:Components) {auto Row=MakeShared<FJsonObject>();Row->SetStringField(TEXT("component"),C->GetPathName());Row->SetStringField(TEXT("mesh"),C->GetSkeletalMeshAsset()?C->GetSkeletalMeshAsset()->GetPathName():TEXT("None"));Row->SetStringField(TEXT("anim_class"),C->GetAnimClass()?C->GetAnimClass()->GetPathName():TEXT("None"));Row->SetNumberField(TEXT("rate"),C->GlobalAnimRateScale);if(auto* Single=C->GetSingleNodeInstance()){Row->SetStringField(TEXT("clip"),Single->GetCurrentAsset()?Single->GetCurrentAsset()->GetPathName():TEXT("None"));Row->SetNumberField(TEXT("length"),Single->GetLength());Row->SetNumberField(TEXT("position"),Single->GetCurrentTime());}Meshes.Add(MakeShared<FJsonValueObject>(Row));}
 }
 R->SetArrayField(TEXT("skeletal_components"),Meshes);
 if(auto* BS=LoadObject<UBlendSpace>(nullptr,TEXT("/Game/ParisCombat/Animation/DirectionalDraft/BS_PC_Allied_Stride_v1.BS_PC_Allied_Stride_v1"))) {
  auto B=MakeShared<FJsonObject>();B->SetStringField(TEXT("asset"),BS->GetPathName());B->SetNumberField(TEXT("axis_x_max"),BS->GetBlendParameter(0).Max);B->SetNumberField(TEXT("axis_y_max"),BS->GetBlendParameter(1).Max);TArray<TSharedPtr<FJsonValue>> Samples;
  for(const auto& S:BS->GetBlendSamples()){auto Row=MakeShared<FJsonObject>();Row->SetStringField(TEXT("clip"),S.Animation?S.Animation->GetPathName():TEXT("None"));Row->SetStringField(TEXT("velocity_sample"),S.SampleValue.ToString());Row->SetNumberField(TEXT("calibrated_rate"),S.RateScale);Samples.Add(MakeShared<FJsonValueObject>(Row));}B->SetArrayField(TEXT("samples"),Samples);R->SetObjectField(TEXT("retained_stride_blendspace"),B);
 }
 auto* WeaponProperty=FindFProperty<FObjectPropertyBase>(P->GetClass(),TEXT("WeaponAppearance"));
 auto* Gun=WeaponProperty?Cast<AActor>(WeaponProperty->GetObjectPropertyValue_InContainer(P)):nullptr;
 if(Gun) {
  R->SetStringField(TEXT("authoritative_gun_class"),Gun->GetClass()->GetPathName());
  TArray<UStaticMeshComponent*> Components;Gun->GetComponents(Components);TArray<TSharedPtr<FJsonValue>> Parts;
  for(auto* C:Components){auto Row=MakeShared<FJsonObject>();Row->SetStringField(TEXT("component"),C->GetName());Row->SetStringField(TEXT("mesh"),C->GetStaticMesh()?C->GetStaticMesh()->GetPathName():TEXT("None"));Parts.Add(MakeShared<FJsonValueObject>(Row));}R->SetArrayField(TEXT("gun_static_components"),Parts);
  TArray<TSharedPtr<FJsonValue>> Fields;
  for(TFieldIterator<FProperty> I(Gun->GetClass());I;++I)if(I->GetName().Contains(TEXT("Reload"))||I->GetName().Contains(TEXT("Clip"))||I->GetName().Contains(TEXT("Bolt"))||I->GetName().Contains(TEXT("Anim"))) {auto Row=MakeShared<FJsonObject>();Row->SetStringField(TEXT("field"),I->GetName());FString Value;I->ExportText_InContainer(0,Value,Gun,Gun,Gun,PPF_None);Row->SetStringField(TEXT("value"),Value);Fields.Add(MakeShared<FJsonValueObject>(Row));}R->SetArrayField(TEXT("gun_mechanism_properties"),Fields);
 }
 Result->SetObjectField(Label,R);
}
void Tick(UWorld* W,ELevelTick,float) {
 if(Finished||!W||!W->IsGameWorld())return;
 if(FPlatformTime::Seconds()-Begin>100){Finish(TEXT("failed_deadline"));return;}
 auto* M=AParisBridgeMission::Find(W);auto* PC=UGameplayStatics::GetPlayerController(W,0);auto* P=PC?Cast<ACharacter>(PC->GetPawn()):nullptr;if(!M||!P)return;
 if(M->Phase==TEXT("Error")){Result->SetStringField(TEXT("error"),M->Feedback);Finish(TEXT("failed_mission_preparation"));return;}
 const double Age=FPlatformTime::Seconds()-Since;
 if(Step==TEXT("ready")) {
  if(M->Phase!=TEXT("Ready")||M->ReadySeconds<1.5)return;
  Result->SetStringField(TEXT("initial"),M->ReadMissionState());Inventory(W,P,TEXT("ready_assets"));
  if(!Check(Num(P,TEXT("LoadedAmmo"))==8&&Num(P,TEXT("ReserveAmmo"))==10&&Num(P,TEXT("ShotSequence"))==0,TEXT("fresh_8_10_total18")))return;
  const FVector Origin=P->GetActorLocation();const auto Center=ParisTeamP1::RadarPoint(Origin,Origin,1742,182,136);
  if(!Check(Center==FVector2D(1742,182),TEXT("player_centered")))return;
  for(FVector Offset:{FVector(100,0,0),FVector(-100,0,0),FVector(0,100,0),FVector(0,-100,0)}) {
   const auto Pt=ParisTeamP1::RadarPoint(Origin+Offset,Origin,1742,182,136);
   if(!Check(FVector2D::Distance(Pt-Center,FVector2D(Offset.X,-Offset.Y)*(136./2500))<1e-8,TEXT("metric_north_up_")+Offset.ToString()))return;
   const auto Scrolled=ParisTeamP1::RadarPoint(Origin,Origin+Offset,1742,182,136);
   if(!Check(FVector2D::Distance(Scrolled-Center,Center-Pt)<1e-8,TEXT("background_scroll_")+Offset.ToString()))return;
  }
  const auto Clipped=ParisTeamP1::ClipSurvey({FVector2D(-1000,-24000),FVector2D(12000,-24000),FVector2D(5000,-14000)});
  bool Inside=Clipped.Num()>=3;for(auto V:Clipped){const auto UV=ParisTeamP1::SurveyUV(FVector(V,0));Inside&=UV.X>=0&&UV.X<=1&&UV.Y>=0&&UV.Y<=1;}
  if(!Check(Inside&&ParisTeamP1::ClipSurvey({FVector2D(-3000,-20000),FVector2D(-2000,-21000),FVector2D(-1000,-19000)}).IsEmpty(),TEXT("unknown_bounds_clipped_no_wrap")))return;
  Tap(PC,EKeys::Enter);PC->SetControlRotation(FRotator(70,0,0));Stage(TEXT("shots"));return;
 }
 if(Step==TEXT("shots")&&Age>.8) {
  if(Count>0&&!Check(Num(P,TEXT("LoadedAmmo"))==8-Count&&Num(P,TEXT("ShotSequence"))==Count&&Num(P,TEXT("ReserveAmmo"))==10,TEXT("shot_")+FString::FromInt(Count)+TEXT("_original_transaction")))return;
  if(Count<8){Tap(PC,EKeys::LeftMouseButton);++Count;Stage(TEXT("shots"));return;}
  Tap(PC,EKeys::LeftMouseButton);Stage(TEXT("empty"));return;
 }
 if(Step==TEXT("empty")&&Age>.8) {
  if(!Check(Num(P,TEXT("LoadedAmmo"))==0&&Num(P,TEXT("ReserveAmmo"))==10&&Num(P,TEXT("ShotSequence"))==8,TEXT("ninth_empty_attempt_no_consumption")))return;
  PC->SetControlRotation(FRotator::ZeroRotator);Tap(PC,EKeys::R);Stage(TEXT("reload"));return;
 }
 if(Step==TEXT("reload")&&Age>1) {Inventory(W,P,TEXT("reload_assets"));FScreenshotRequest::RequestScreenshot(Out/TEXT("reload.png"),false,false);Stage(TEXT("reload_settle"));return;}
 if(Step==TEXT("reload_settle")&&Age>9) {
  if(!Check(Num(P,TEXT("LoadedAmmo"))==8&&Num(P,TEXT("ReserveAmmo"))==2&&Num(P,TEXT("ShotSequence"))==8&&P->GetMesh()->GlobalAnimRateScale==1,TEXT("original_reload_total18_rate1")))return;
  Result->SetStringField(TEXT("after_reload"),M->ReadMissionState());FScreenshotRequest::RequestScreenshot(Out/TEXT("hud.png"),false,false);Generation=M->RunGeneration;Stage(TEXT("restart_delay"));return;
 }
 if(Step==TEXT("restart_delay")&&Age>.5){Tap(PC,EKeys::F6);Stage(TEXT("restart"));return;}
 if(Step==TEXT("restart")) {
  if(M->RunGeneration==Generation||M->Phase!=TEXT("Ready")||M->ReadySeconds<1)return;
  if(!Check(Num(P,TEXT("LoadedAmmo"))==8&&Num(P,TEXT("ReserveAmmo"))==10&&Num(P,TEXT("ShotSequence"))==0&&M->LivingDefenders==3,TEXT("fresh_restart_configured_loadout")))return;
  Result->SetStringField(TEXT("restart"),M->ReadMissionState());Stage(TEXT("finish"));return;
 }
 if(Step==TEXT("finish")&&Age>.5)Finish(TEXT("pass_p1_ammo_radar_inventory"));
}
}
void Initialize(){if(!FParse::Value(FCommandLine::Get(),TEXT("ParisP1Out="),Out))return;IFileManager::Get().MakeDirectory(*Out,true);Begin=FPlatformTime::Seconds();Handle=FWorldDelegates::OnWorldPostActorTick.AddStatic(&Tick);}
void Shutdown(){if(Handle.IsValid())FWorldDelegates::OnWorldPostActorTick.Remove(Handle);}
}
