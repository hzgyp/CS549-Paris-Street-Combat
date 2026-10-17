#pragma once
#include <cstdint>
#include <cmath>
// Engine-independent rules shared by production and standalone adversarial checks.
namespace ParisMedicalPolicy {
constexpr int Capacity=2,Healing=50,SourceCount=4;
constexpr double Seconds=3.;
enum class Claim : int { Waiting,Available,Claimed,Miss,Retired };
inline std::uint32_t Hash(const char* Text,std::uint32_t Seed=2166136261u){
 for(;*Text;++Text){Seed^=static_cast<unsigned char>(*Text);Seed*=16777619u;}return Seed?Seed:1u;
}
inline bool Eligible(std::uint32_t Seed,int Index){
 if(Index==0||Index==3)return true;
 auto H=Hash(Index==1?"German2":"German3",Seed);
 H^=H>>16;H*=0x7feb352du;H^=H>>15;H*=0x846ca68bu;H^=H>>16;
 return H%100u<25u;
}
inline bool Conserved(int Held,int Used,int Claimed){return Held>=0&&Held<=Capacity&&Used>=0&&Used<=SourceCount&&Claimed>=0&&Claimed<=SourceCount&&Held+Used==Claimed;}
inline bool CanStart(bool Alive,bool Idle,bool Grounded,bool Stationary,int Held,double HP,double Max){
 return Alive&&Idle&&Grounded&&Stationary&&Held>0&&Held<=Capacity&&std::isfinite(HP)&&std::isfinite(Max)&&HP>0&&HP<Max;
}
inline bool CanCommit(bool Valid,double Elapsed,double HP,double StartedHP){return Valid&&std::isfinite(Elapsed)&&std::isfinite(HP)&&std::isfinite(StartedHP)&&Elapsed>=Seconds&&HP==StartedHP&&HP>0;}
inline double Healed(double HP,double Max){return std::fmin(Max,HP+Healing);}
inline bool ValidClaim(Claim State,bool HasKit,bool Dead,bool Legacy,bool IsSupply,bool Combat){
 if(State==Claim::Retired)return Legacy&&(IsSupply||Dead);
 if(IsSupply)return State==Claim::Claimed?Combat:State==(Combat?Claim::Available:Claim::Waiting);
 if(!Dead)return State==Claim::Waiting;
 if(!HasKit)return State==Claim::Miss;
 return State==Claim::Available||State==Claim::Claimed;
}
}
