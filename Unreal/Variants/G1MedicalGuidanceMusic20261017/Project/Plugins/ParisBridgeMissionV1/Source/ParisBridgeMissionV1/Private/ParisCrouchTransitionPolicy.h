#pragma once
#include <algorithm>
#include <cmath>

namespace ParisCrouchTransitionPolicy {
// Camera easing spans the full unmodified clip, with zero endpoint velocity.
inline double CameraAlpha(double Age,double Duration) {
    if(!std::isfinite(Age)||!std::isfinite(Duration)||Duration<=0.)return 0.;
    const double T=std::clamp(Age/Duration,0.,1.);
    return T*T*(3.-2.*T);
}
enum class Endpoint { Wait, CommitCrouch, Complete, Timeout };
inline Endpoint Decide(bool Entering,bool Committing,bool AtNativeEndpoint,
                       double Age,double Duration,double Elapsed) {
    if(!std::isfinite(Duration)||Duration<=0.||Elapsed>Duration+1.)return Endpoint::Timeout;
    if(Age<Duration)return Endpoint::Wait;
    if(Entering&&!Committing)return Endpoint::CommitCrouch;
    return AtNativeEndpoint?Endpoint::Complete:Endpoint::Wait;
}
}
