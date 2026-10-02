#include "ParisBlueprintAuthoring.h"

#include "Blueprint/WidgetTree.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/TextBlock.h"
#include "Kismet2/BlueprintEditorUtils.h"
#include "Misc/PackageName.h"
#include "WidgetBlueprint.h"

bool UParisBlueprintAuthoring::CreateStatusWidgetTemplate(UBlueprint* Blueprint)
{
    auto* Widget = Cast<UWidgetBlueprint>(Blueprint);
    if (!Widget || !Widget->GetOutermost()->GetName().StartsWith(TEXT("/Game/ParisCombat/UI/CityGameplayV1/"))
        || FPackageName::DoesPackageExist(Widget->GetOutermost()->GetName()))
        return false;
    UWidgetTree* Tree = Widget->WidgetTree;
    if (!Tree) return false;
    auto* Canvas = Cast<UCanvasPanel>(Tree->RootWidget);
    if (Tree->RootWidget && (!Canvas || Canvas->GetChildrenCount() != 0)) return false;
    if (Tree->FindWidget(TEXT("StatusText")) || Tree->FindWidget(TEXT("AimMark"))) return false;
    Widget->Modify(); Tree->Modify();
    if (!Canvas) Canvas = Tree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass(), TEXT("ParisStatusCanvas"));
    Tree->RootWidget = Canvas;
    Canvas->SetVisibility(ESlateVisibility::HitTestInvisible);

    auto* Status = Tree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), TEXT("StatusText"));
    Status->bIsVariable = true;
    Status->SetText(FText::FromString(TEXT("Waiting for player")));
    FSlateFontInfo StatusFont = Status->GetFont(); StatusFont.Size = 20; Status->SetFont(StatusFont);
    Status->SetShadowOffset(FVector2D(1,1));
    Status->SetShadowColorAndOpacity(FLinearColor(0,0,0,1));
    auto* StatusSlot = Canvas->AddChildToCanvas(Status);
    StatusSlot->SetAnchors(FAnchors(0,1));
    StatusSlot->SetAlignment(FVector2D(0,1));
    StatusSlot->SetPosition(FVector2D(20,-20));
    StatusSlot->SetAutoSize(true);

    auto* Aim = Tree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), TEXT("AimMark"));
    Aim->SetText(FText::FromString(TEXT("+")));
    auto* AimSlot = Canvas->AddChildToCanvas(Aim);
    AimSlot->SetAnchors(FAnchors(.5,.5));
    AimSlot->SetAlignment(FVector2D(.5,.5));
    AimSlot->SetPosition(FVector2D::ZeroVector);
    AimSlot->SetAutoSize(true);
    FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Widget);
    return true;
}
