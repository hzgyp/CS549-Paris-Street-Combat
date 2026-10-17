#include "SkeletalRenderPublic.h"
#include "Engine/StaticMesh.h"
#include "Camera/CameraActor.h"
#include "ParisTraversal.h"
#include "ParisBridgeMission.h"
#include "ParisFirstPersonApprovedActor.h"
#include "ParisActionBindings.h"
#include "ParisPlayerDeath.h"
#include "UObject/StructOnScope.h"
#include "Components/PoseableMeshComponent.h"
#include "ParisEquipmentState.h"
#include "ParisTacticalEquipment.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Camera/CameraComponent.h"
#include "Camera/PlayerCameraManager.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "AIController.h"
#include "BrainComponent.h"
#include "InputKeyEventArgs.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "UObject/UnrealType.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"
#include "HAL/FileManager.h"
#include "UnrealClient.h"
namespace ParisObserverTutorialAudit {
namespace {
FString PPMode,PPOut;bool PPPhotos=false;FDelegateHandle Handle;
double Num(const UObject* O,const TCHAR* K){auto* F=O?FindFProperty<FNumericProperty>(O->GetClass(),K):nullptr;if(!F)return -1;const auto* V=F->ContainerPtrToValuePtr<void>(O);return F->IsFloatingPoint()?F->GetFloatingPointPropertyValue(V):F->GetSignedIntPropertyValue(V);}
FName Name(const UObject* O,const TCHAR* K){auto* F=O?FindFProperty<FNameProperty>(O->GetClass(),K):nullptr;return F?F->GetPropertyValue_InContainer(O):NAME_None;}
UObject* Obj(const UObject* O,const TCHAR* K){auto* F=O?FindFProperty<FObjectPropertyBase>(O->GetClass(),K):nullptr;return F?F->GetObjectPropertyValue_InContainer(O):nullptr;}
void PPTap(APlayerController* PC,FKey K){PC->InputKey(FInputKeyEventArgs::CreateSimulated(K,IE_Pressed,1));PC->InputKey(FInputKeyEventArgs::CreateSimulated(K,IE_Released,0));}
void PPPhoto(const FString& Label){if(PPPhotos)FScreenshotRequest::RequestScreenshot(PPOut/(Label+TEXT(".png")),false,false);}
void PPHold(UWorld* W){for(TActorIterator<ACharacter> I(W);I;++I)if(auto* AI=Cast<AAIController>(I->GetController()))if(AI->GetBrainComponent()){AI->GetBrainComponent()->PauseLogic(TEXT("Declared isolated presentation audit"));I->GetCharacterMovement()->StopMovementImmediately();}}
void PPPlace(UWorld* W,ACharacter* P,AParisBridgePlayerController* PC){PPHold(W);P->SetActorLocation(FVector(1762.5,-20662.5,114.402+P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight()),false);P->SetActorRotation(FRotator::ZeroRotator);PC->SetControlRotation(FRotator::ZeroRotator);P->GetCharacterMovement()->StopMovementImmediately();}
}
#include "ParisObserverBindingsAudit.inl"
namespace {void Tick(UWorld* W,ELevelTick,float){OBTick(W);}}
void Initialize(){if(!FParse::Value(FCommandLine::Get(),TEXT("ParisProneProbe="),PPMode))return;check(PPMode==TEXT("binding_fp")||PPMode==TEXT("binding_tp")||PPMode==TEXT("binding_swap")||PPMode==TEXT("binding_lifecycle"));check(FParse::Value(FCommandLine::Get(),TEXT("ParisProneOut="),PPOut));PPPhotos=FParse::Param(FCommandLine::Get(),TEXT("ParisPronePictures"));IFileManager::Get().MakeDirectory(*PPOut,true);Handle=FWorldDelegates::OnWorldTickStart.AddStatic(&Tick);}
void Shutdown(){if(Handle.IsValid())FWorldDelegates::OnWorldTickStart.Remove(Handle);}
}
