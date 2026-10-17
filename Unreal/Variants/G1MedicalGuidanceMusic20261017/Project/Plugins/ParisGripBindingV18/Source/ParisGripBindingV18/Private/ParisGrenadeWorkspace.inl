// Grenade-specific display reach. Native torso/clavicle and arm twist locals
// stay together; only the left arm reaches its camera-space presentation goal.
static bool GrenadeReach(const FReferenceSkeleton& Ref,TArray<FTransform>& Local,const FVector& Goal){
    TArray<FTransform> Original;Original.SetNum(Local.Num());
    for(int32 I=0;I<Local.Num();++I){const int32 Parent=Ref.GetParentIndex(I);Original[I]=Parent>=0?Local[I]*Original[Parent]:Local[I];}
    const int32 U=Ref.FindBoneIndex(TEXT("upperarm_l")),L=Ref.FindBoneIndex(TEXT("lowerarm_l")),H=Ref.FindBoneIndex(TEXT("hand_l"));
    if(U<0||L<0||H<0)return false;
    FTransform Upper=Original[U],Lower=Original[L],Hand=Original[H];
    const double A=FVector::Distance(Upper.GetLocation(),Lower.GetLocation()),B=FVector::Distance(Lower.GetLocation(),Hand.GetLocation());
    const FVector Delta=Goal-Upper.GetLocation();
    const FVector Reach=Upper.GetLocation()+Delta.GetSafeNormal()*FMath::Clamp(Delta.Size(),FMath::Abs(A-B)+.01,A+B-.01);
    AnimationCore::SolveTwoBoneIK(Upper,Lower,Hand,Original[L].GetLocation(),Reach,A,B,false,1.,1.);
    // Carry the native wrist with the solved forearm. Preserving the old
    // world wrist rotation after changing forearm direction folds the hand
    // backwards and puts the grenade behind its palm.
    Hand.SetRotation((Lower.GetRotation()*Local[H].GetRotation()).GetNormalized());
    Local[U]=Upper.GetRelativeTransform(Original[Ref.GetParentIndex(U)]);
    Local[L]=Lower.GetRelativeTransform(Upper);
    Local[H]=Hand.GetRelativeTransform(Lower);
    return true;
}
