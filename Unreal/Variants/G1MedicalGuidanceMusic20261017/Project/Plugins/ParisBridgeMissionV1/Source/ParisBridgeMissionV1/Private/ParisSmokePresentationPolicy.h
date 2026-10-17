#pragma once
// Engine-independent decisions shared by the VFX, pose admission and offline checks.
#include <algorithm>
#include <array>
#include <cmath>
namespace ParisSmokePresentation {
inline constexpr double CloudSeconds=18., PuffSeconds=3., OutletZ=8.15;
inline constexpr std::array<double,3> BodyCenter{.075,.00302845,1.1675};
inline constexpr std::array<double,3> BodyHalf{3.285,3.21302845,7.4175};
struct Key { float Time,Value; };
inline constexpr std::array<Key,4> Expansion{{{0,1},{.15f,2.5f},{.6f,6.5f},{1,9}}};
inline constexpr std::array<Key,5> Alpha{{{0,0},{.12f,.6f},{.55f,.5f},{.85f,.2f},{1,0}}};
struct Schedule { double Warmup,EmissionDuration; };
inline Schedule Remaining(double Life) {
    const double Warmup=std::clamp(CloudSeconds-Life,0.,PuffSeconds);
    return {Warmup,std::max(.000001,Life-PuffSeconds+Warmup)};
}
struct PoseNumbers {
    std::array<double,3> Position,Scale,Linear,Angular;
    std::array<double,4> Rotation;
};
inline double Squared(const std::array<double,3>& V) { return V[0]*V[0]+V[1]*V[1]+V[2]*V[2]; }
inline bool Valid(const PoseNumbers& P) {
    for(double V:P.Position) if(!std::isfinite(V)||std::abs(V)>=1000000.)return false;
    for(double V:P.Scale) if(!std::isfinite(V)||V<.05||V>5.)return false;
    for(double V:P.Linear) if(!std::isfinite(V))return false;
    for(double V:P.Angular) if(!std::isfinite(V))return false;
    if(Squared(P.Linear)>5000.*5000.||Squared(P.Angular)>720.*720.)return false;
    double Norm=0;for(double V:P.Rotation){if(!std::isfinite(V))return false;Norm+=V*V;}
    return std::abs(Norm-1.)<=.001;
}
}
