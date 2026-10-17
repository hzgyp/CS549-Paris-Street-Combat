// Compatible existing reload retargeted into the accepted FP arm workspace.
bool AParisFPUpperBodyV19Actor::AdaptReloadWorkspace(const FReferenceSkeleton& Ref,TArray<FTransform>& Target){
    if(ReadyWorkspace.Num()!=Target.Num()){BindingError=TEXT("Accepted Ready workspace unavailable");return false;}
    TArray<FTransform> Original;Original.SetNum(Target.Num());
    for(int32 I=0;I<Target.Num();++I){const int32 Parent=Ref.GetParentIndex(I);Original[I]=Parent>=0?Target[I]*Original[Parent]:Target[I];}
    TArray<FTransform> Result=ReadyWorkspace;
    TMap<int32,FTransform> Solved;
    for(const TCHAR* Side:{TEXT("l"),TEXT("r")}){
        const int32 U=Ref.FindBoneIndex(FName(*(FString(TEXT("upperarm_"))+Side))),L=Ref.FindBoneIndex(FName(*(FString(TEXT("lowerarm_"))+Side))),H=Ref.FindBoneIndex(FName(*(FString(TEXT("hand_"))+Side)));
        if(U==INDEX_NONE||L==INDEX_NONE||H==INDEX_NONE){BindingError=TEXT("Original arm chain absent");return false;}
        const double A=FVector::Distance(ReadyWorkspace[U].GetLocation(),ReadyWorkspace[L].GetLocation()),B=FVector::Distance(ReadyWorkspace[L].GetLocation(),ReadyWorkspace[H].GetLocation());
        FTransform Upper=ReadyWorkspace[U],Lower=ReadyWorkspace[L],Hand=ReadyWorkspace[H];const FVector Delta=Original[H].GetLocation()-Upper.GetLocation();const double Length=Delta.Size();
        const FVector Goal=Upper.GetLocation()+Delta.GetSafeNormal()*FMath::Clamp(Length,FMath::Abs(A-B)+.01,A+B-.01);
        AnimationCore::SolveTwoBoneIK(Upper,Lower,Hand,Original[L].GetLocation(),Goal,A,B,false,1.,1.);Hand.SetRotation(Original[H].GetRotation());
        Solved.Add(U,Upper);Solved.Add(L,Lower);Solved.Add(H,Hand);
    }
    // Keep torso/clavicle roots in the accepted display frame. Arm descendants use native action locals.
    TSet<int32> ArmDescendants;
    for(int32 I=0;I<Target.Num();++I){int32 Parent=I;while(Parent>=0){const auto Name=Ref.GetBoneName(Parent);if(Name==TEXT("upperarm_l")||Name==TEXT("upperarm_r")){ArmDescendants.Add(I);break;}Parent=Ref.GetParentIndex(Parent);}}
    for(int32 I=0;I<Target.Num();++I){const int32 Parent=Ref.GetParentIndex(I);if(const auto* T=Solved.Find(I))Result[I]=*T;else if(ArmDescendants.Contains(I))Result[I]=Parent>=0?Target[I]*Result[Parent]:Target[I];}
    for(int32 I=0;I<Target.Num();++I){const int32 Parent=Ref.GetParentIndex(I);Target[I]=Parent>=0?Result[I].GetRelativeTransform(Result[Parent]):Result[I];}
    return true;
}
