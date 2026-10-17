#pragma once

#include "CoreMinimal.h"
#include "ReferenceSkeleton.h"

// This pair only: retained continuous-arms/US rig and the 6.2cm smoke body.
// Authored from the retained skin + native poses; never a rifle/frag pose reset.
namespace ParisSmokeGripContact {
inline const TCHAR* Fingers[4]={TEXT("index"),TEXT("middle"),TEXT("ring"),TEXT("pinky")};
inline constexpr double SkinEnvelopeCm[4]={1.35,1.25,1.20,1.10};
inline constexpr double DistalLengthCm[4]={3.006,3.058,2.743,2.535};
inline FName Bone(int32 Finger,int32 Segment){return FName(*FString::Printf(TEXT("%s_0%d_l"),Fingers[Finger],Segment));}
struct FFrame {
    FVector Plane,Up,Facing,Side,Center;
    double Radius[4];
    FVector ToLocal(const FVector& P) const {const FVector D=P-Plane;return FVector(Dot(D,Facing),Dot(D,Side),Dot(D,Up));}
    FVector ToVector(const FVector& D) const {return Facing*D.X+Side*D.Y+Up*D.Z;}
    static double Dot(const FVector& A,const FVector& B){return FVector::DotProduct(A,B);}
};
inline bool Frame(TFunctionRef<FVector(FName)> Point,FFrame& F){
    F.Plane=FVector::ZeroVector;for(int32 I=0;I<4;++I)F.Plane+=Point(Bone(I,1))*.25;
    F.Up=(Point(Bone(0,1))-Point(Bone(3,1))).GetSafeNormal();
    F.Facing=FVector::CrossProduct(Point(Bone(1,1))-Point(TEXT("hand_l")),F.Up).GetSafeNormal();
    if(FVector::DotProduct(F.Facing,(Point(Bone(1,3))+Point(Bone(2,3)))*.5-Point(Bone(1,1)))<0)F.Facing=-F.Facing;
    F.Side=FVector::CrossProduct(F.Up,F.Facing).GetSafeNormal();F.Facing=FVector::CrossProduct(F.Side,F.Up).GetSafeNormal();
    if(F.Up.IsNearlyZero()||F.Side.IsNearlyZero()||F.Facing.IsNearlyZero())return false;
    double CenterX=0;
    for(int32 I=0;I<4;++I){
        const double Longest=FMath::Max3(FVector::Distance(Point(Bone(I,1)),Point(Bone(I,2))),FVector::Distance(Point(Bone(I,2)),Point(Bone(I,3))),DistalLengthCm[I]);
        // Circle chords need clearance at their middle, as well as the joints.
        F.Radius[I]=FMath::Sqrt(FMath::Square(3.10+SkinEnvelopeCm[I]+.04)+FMath::Square(Longest*.5));
        CenterX=FMath::Max(CenterX,F.ToLocal(Point(Bone(I,1))).X+F.Radius[I]);
    }
    F.Center=F.Plane+F.Facing*CenterX;return true;
}
inline bool Advance(const FVector& Start,const FVector& Center,double Radius,double Length,double DZ,FVector& End,bool Opposed=false){
    const FVector2D D(Center.X-Start.X,Center.Y-Start.Y);const double Distance=D.Size();
    if(Distance<.001||Length<=FMath::Abs(DZ))return false;
    const double Chord2=Length*Length-DZ*DZ;
    const double Along=(Chord2-Radius*Radius+Distance*Distance)/(2*Distance);
    const double Height2=Chord2-Along*Along;if(Height2<-.001)return false;
    const FVector2D Unit=D/Distance,Base=FVector2D(Start.X,Start.Y)+Unit*Along;
    const FVector2D Side(-Unit.Y,Unit.X),Offset=Side*FMath::Sqrt(FMath::Max(0.,Height2));
    const FVector2D A=Base+Offset,B=Base-Offset,R(Start.X-Center.X,Start.Y-Center.Y);
    auto Angle=[&](const FVector2D& P){const FVector2D Q=P-FVector2D(Center.X,Center.Y);return FMath::Atan2(R.X*Q.Y-R.Y*Q.X,FVector2D::DotProduct(R,Q));};
    const FVector2D P=Opposed?(Angle(A)<Angle(B)?A:B):(Angle(A)>Angle(B)?A:B);End=FVector(P.X,P.Y,Start.Z+DZ);return true;
}
inline bool Apply(const FReferenceSkeleton& Ref,TArray<FTransform>& Local){
    if(Local.Num()!=Ref.GetNum())return false;
    TArray<FTransform> Before;Before.SetNum(Local.Num());
    for(int32 I=0;I<Local.Num();++I){const int32 P=Ref.GetParentIndex(I);Before[I]=P>=0?Local[I]*Before[P]:Local[I];}
    int32 Indices[4][3];
    for(int32 I=0;I<4;++I)for(int32 J=0;J<3;++J){Indices[I][J]=Ref.FindBoneIndex(Bone(I,J+1));if(Indices[I][J]<0)return false;}
    if(Ref.FindBoneIndex(TEXT("hand_l"))<0)return false;
    FFrame F;if(!Frame([&](FName N){return Before[Ref.FindBoneIndex(N)].GetLocation();},F))return false;
    FVector Goals[4][4];const FVector Center=F.ToLocal(F.Center);
    for(int32 I=0;I<4;++I){
        Goals[I][0]=F.ToLocal(Before[Indices[I][0]].GetLocation());
        for(int32 J=0;J<3;++J){
            const int32 B=Indices[I][J];double Length,DZ;
            if(J<2){const FVector Delta=Before[Indices[I][J+1]].GetLocation()-Before[B].GetLocation();Length=Delta.Size();DZ=FVector::DotProduct(Delta,F.Up);}
            else {Length=DistalLengthCm[I];DZ=FVector::DotProduct(Before[B].TransformVector(FVector(Length,0,0)),F.Up);}
            // Validate every target before changing any local rotation.
            if(!Advance(Goals[I][J],Center,F.Radius[I],Length,DZ,Goals[I][J+1]))return false;
        }
    }
    // This continuous-arms rig/prop only: measured parent-local thumb grip.
    // Preserve the native web contour; distribute opposition through the chain.
    // Fixed grip axes avoid adding a fit delta to changing wind-up finger poses.
    // Caller retains the existing equipped/action blend and release ownership.
    const int32 Thumb[3]={Ref.FindBoneIndex(TEXT("thumb_01_l")),Ref.FindBoneIndex(TEXT("thumb_02_l")),Ref.FindBoneIndex(TEXT("thumb_03_l"))};
    if(Thumb[0]<0||Thumb[1]<0||Thumb[2]<0)return false;
    const FQuat ThumbGrip[3]={
        FQuat(-0.6044151231186797,0.4249900936137382,0.06784492670786649,0.6704199021476179),
        FQuat(-0.009039066183466704,0.364203470930253,-0.07882686365665754,0.9279334311312111),
        FQuat(-0.05887515444621703,0.03102271376300537,-0.3167665252592111,0.9461660931860317)
    };
    for(int32 I=0;I<4;++I){
        FTransform Parent=Before[Ref.GetParentIndex(Indices[I][0])];
        for(int32 J=0;J<3;++J){
            const int32 B=Indices[I][J];FTransform C=Local[B]*Parent;
            const FVector Old=C.TransformVector(J<2?Local[Indices[I][J+1]].GetTranslation():FVector(DistalLengthCm[I],0,0));
            const FVector Goal=F.ToVector(Goals[I][J+1]-Goals[I][J]);
            C.SetRotation((FQuat::FindBetweenNormals(Old.GetSafeNormal(),Goal.GetSafeNormal())*C.GetRotation()).GetNormalized());
            Local[B].SetRotation(C.GetRelativeTransform(Parent).GetRotation());Parent=Local[B]*Parent;
        }
    }
    // Rotations only: retain original translations/scales and all four fingers.
    for(int32 J=0;J<3;++J)Local[Thumb[J]].SetRotation(ThumbGrip[J].GetNormalized());
    return true;
}
} // namespace ParisSmokeGripContact
