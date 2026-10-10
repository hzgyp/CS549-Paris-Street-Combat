// Recording-only live diagnostics. Read-only engine timings/memory, no game state.
#include "ParisLiveStats.h"
#include "Debug/DebugDrawService.h"
#include "Engine/Canvas.h"
#include "Engine/Engine.h"
#include "Engine/Font.h"
#include "CanvasItem.h"
#include "EngineGlobals.h"
#include "HAL/PlatformMemory.h"
#include "HAL/PlatformTime.h"
#include "Misc/App.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "RHI.h"
#include "DynamicRHI.h"
#include "RHIStats.h"
#include "RenderTimer.h"

namespace ParisLiveStats {
namespace {
FDelegateHandle Handle;
double Frame=0,Game=0,Draw=0,Gpu=0,Rhi=0,LastSample=0;
FString Lines[6];
uint64 LastFrame=MAX_uint64;
bool Initialized=false;
void Render(UCanvas* Canvas,APlayerController*) {
 if(!Canvas||!Canvas->Canvas||!GEngine)return;
 if(LastFrame!=GFrameCounter){
  const double RawFrame=(FApp::GetCurrentTime()-FApp::GetLastTime())*1000.;
  const double RawGame=FPlatformTime::ToMilliseconds(GGameThreadTime);
  const double RawDraw=FPlatformTime::ToMilliseconds(GRenderThreadTime);
  const double RawGpu=FPlatformTime::ToMilliseconds(RHIGetGPUFrameCycles(0));
  const double RawRhi=FPlatformTime::ToMilliseconds(GRHIThreadTime);
  if(!Initialized){Frame=RawFrame;Game=RawGame;Draw=RawDraw;Gpu=RawGpu;Rhi=RawRhi;Initialized=true;}
  else{Frame=.9*Frame+.1*RawFrame;Game=.9*Game+.1*RawGame;Draw=.9*Draw+.1*RawDraw;Gpu=.9*Gpu+.1*RawGpu;Rhi=.9*Rhi+.1*RawRhi;}
  LastFrame=GFrameCounter;
 }
 const double Now=FPlatformTime::Seconds();
 if(Now-LastSample>=.25){
  const FPlatformMemoryStats Ram=FPlatformMemory::GetStats();
  FRHIMemoryStats Vram;RHIGetMemoryStats(Vram);
  Lines[0]=Frame>0?FString::Printf(TEXT("%.1f FPS  |  %.2f ms"),1000./Frame,Frame):TEXT("FPS / Frame: N/A");
  Lines[1]=FString::Printf(TEXT("CPU Game %.2f  Draw %.2f ms"),Game,Draw);
  Lines[2]=Gpu>0?FString::Printf(TEXT("GPU %.2f  |  RHI %.2f ms"),Gpu,Rhi):TEXT("GPU: N/A");
  Lines[3]=FString::Printf(TEXT("RAM process %.2f GB"),double(Ram.UsedPhysical)/1073741824.);
  Lines[4]=Vram.IsValid()?FString::Printf(TEXT("VRAM %.2f / %.2f GB"),double(Vram.UsedLocal)/1073741824.,double(Vram.BudgetLocal)/1073741824.):TEXT("VRAM / budget: N/A");
  Lines[5]=FString::Printf(TEXT("Draws %d  |  Prims %.0fk"),GNumDrawCallsRHI[0],double(GNumPrimitivesDrawnRHI[0])/1000.);
  LastSample=Now;
  UE_LOG(LogTemp,Display,TEXT("PARIS_LIVE_STATS frame=%llu fps=%.3f frame_ms=%.3f game_ms=%.3f draw_ms=%.3f gpu_ms=%.3f rhi_ms=%.3f ram_bytes=%llu vram_bytes=%llu vram_budget=%llu"),GFrameCounter,Frame>0?1000./Frame:0,Frame,Game,Draw,Gpu,Rhi,Ram.UsedPhysical,Vram.UsedLocal,Vram.BudgetLocal);
 }
 const float S=float(Canvas->SizeX)/1920.f;
 const float X=(Canvas->SizeX-720.f*S),Y=42.f*S,W=386.f*S,H=252.f*S;
 FCanvasTileItem Tile(FVector2D(X,Y),FVector2D(W,H),FLinearColor(.016,.022,.025,.89));
 Tile.BlendMode=SE_BLEND_Translucent;Canvas->Canvas->DrawItem(Tile);
 const float FontHeight=FMath::Max(1.f,GEngine->GetMediumFont()->GetMaxCharHeight());
 auto Text=[&](const FString& T,float Row,float Size,FLinearColor Color){
  FCanvasTextItem Item(FVector2D(X+16*S,Y+Row*S),FText::FromString(T),GEngine->GetMediumFont(),Color);
  Item.Scale=FVector2D(Size*S/FontHeight,Size*S/FontHeight);
  Item.EnableShadow(FLinearColor::Black);Canvas->Canvas->DrawItem(Item);
 };
 Text(TEXT("LIVE UE PERFORMANCE"),12,20,FLinearColor(.76,.84,.63));
 Text(Lines[0],41,27,FLinearColor(.92,.97,.81));
 for(int32 I=1;I<6;++I)Text(Lines[I],76+(I-1)*27,20,FLinearColor(.9,.92,.92));
 Text(TEXT("1080p High | RT off | uncapped"),220,16,FLinearColor(.63,.68,.70));
}
}
void Initialize(){if(!FParse::Param(FCommandLine::Get(),TEXT("ParisLiveStats")))return;Handle=UDebugDrawService::Register(TEXT("Game"),FDebugDrawDelegate::CreateStatic(&Render));}
void Shutdown(){if(Handle.IsValid())UDebugDrawService::Unregister(Handle);Handle.Reset();}
}
