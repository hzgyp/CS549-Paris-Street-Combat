// Field-manual primitives; runtime text and line symbols, never a flattened UI image.
const double NavX[]={945,1085,1305,1480},NavW[]={125,200,160,185};
constexpr double NavY=145,NavH=55,SideX=218,SideY=296,SideStep=84,SideW=350,SideH=70;
constexpr double GroupX=660,GroupY=363,GroupStep=205,GroupW=195,GroupH=51;
UFont* FieldFont(int32 Kind){
 static TStrongObjectPtr<UFont> Title,Body,Bold;
 auto& Held=Kind==1?Title:Kind==2?Bold:Body;
 if(!Held.IsValid()){
  const FString File=FPaths::ConvertRelativePathToFull(FPaths::Combine(FPlatformProcess::BaseDir(),TEXT("../../UI"),Kind==1?TEXT("Cinzel.ttf"):Kind==2?TEXT("Roboto-BoldCondensed.ttf"):TEXT("Roboto-Regular.ttf")));
  checkf(FPaths::FileExists(File),TEXT("Field manual font required: %s"),*File);
  Held.Reset(NewObject<UFont>());Held->FontCacheType=EFontCacheType::Runtime;
  Held->GetMutableInternalCompositeFont()=FCompositeFont(FName(TEXT("Regular")),File,EFontHinting::Default,EFontLoadingPolicy::LazyLoad);
  UE_LOG(LogTemp,Display,TEXT("PARIS_FIELD_MANUAL_FONT kind=%d file=%s runtime_ufont=1"),Kind,*File);
 }
 return Held.Get();
}
struct FPaint {
 AParisBridgeHUD* H;double S,X,Y;
 FPaint(AParisBridgeHUD* In,bool HUD=false):H(In){int32 W=0,Height=0;H->GetOwningPlayerController()->GetViewportSize(W,Height);S=FMath::Min(W/1920.,Height/1080.)*(HUD?HudScale():1);X=(W-1920*S)*.5;Y=(Height-1080*S)*.5;}
 void Box(double A,double B,double W,double Height,FLinearColor C){H->DrawRect(C,X+A*S,Y+B*S,W*S,Height*S);}
 void Line(double A,double B,double C,double D,FLinearColor Color,double Width=1){H->DrawLine(X+A*S,Y+B*S,X+C*S,Y+D*S,Color,Width*S);}
 double Write(const FString& T,double A,double B,double Size,FLinearColor C,int32 Kind=0,int32 Tracking=0,bool Centre=false){
  if(T.IsEmpty())return 0;
  // Slate sizes are points (96/72 pixels); layout uses reference pixels.
  FSlateFontInfo Info(FieldFont(Kind),FMath::RoundToInt(Size*.75));Info.LetterSpacing=Tracking;
  FCanvasTextItem Item(FVector2D(X+A*S,Y+B*S),FText::FromString(T),Info,C);Item.Scale=FVector2D(S,S);Item.bCentreX=Centre;
  Item.EnableShadow(FLinearColor(0,0,0,.5),FVector2D(S,S));H->GetCombatCanvas()->DrawItem(Item);
  checkf(Item.DrawnSize.X>0&&Item.DrawnSize.Y>0,TEXT("Field manual glyph draw required"));
  static bool Logged=false;if(!Logged){Logged=true;UE_LOG(LogTemp,Display,TEXT("PARIS_FIELD_MANUAL_DRAW width=%.2f height=%.2f"),Item.DrawnSize.X,Item.DrawnSize.Y);}
  return Item.DrawnSize.X/S;
 }
 void Text(const FString& T,double A,double B,double Size,FLinearColor C=Ivory){Write(T,A,B,Size,C);}
 void Title(const FString& T,double A,double B,double Size,FLinearColor C=Ivory){Write(T,A,B,Size,C,1);}
 void Label(const FString& T,double A,double B,double Size=18,FLinearColor C=Muted){Write(T,A,B,Size,C,2,90);}
 void Outline(double A,double B,double W,double Height,FLinearColor C,double Width=1){Line(A,B,A+W,B,C,Width);Line(A+W,B,A+W,B+Height,C,Width);Line(A+W,B+Height,A,B+Height,C,Width);Line(A,B+Height,A,B,C,Width);}
 void Button(const FString& T,double A,double B,double W,bool Selected,bool Enabled=true){if(Selected)Box(A,B,W,52,FLinearColor(.12,.15,.10,.8));Outline(A,B,W,52,Selected?Brass:Muted);Write(T,A+W*.5,B+13,23,Enabled?Ivory:Muted,2,70,true);}
 void Bar(double A,double B,double W,double Ratio,FLinearColor C=Green){Line(A,B+3,A+W,B+3,Fill,6);Line(A,B+3,A+W*FMath::Clamp(Ratio,0.,1.),B+3,C,4);}
 void Key(const FString& T,double A,double B,double W=40){Box(A,B,W,34,FLinearColor(.006,.012,.009,.45));Outline(A,B,W,34,Brass);Write(T,A+W*.5,B+6,20,Ivory,2,40,true);}
 void Circle(double A,double B,double Radius,FLinearColor C,double Width=2){for(int32 I=0;I<32;++I){const double AA=2*PI*I/32,BB=2*PI*(I+1)/32;Line(A+Radius*FMath::Cos(AA),B+Radius*FMath::Sin(AA),A+Radius*FMath::Cos(BB),B+Radius*FMath::Sin(BB),C,Width);}}
 void Stroke(double A,double B,TArray<FVector2D> Points,FLinearColor C,double Width=2){for(int32 I=1;I<Points.Num();++I)Line(A+Points[I-1].X,B+Points[I-1].Y,A+Points[I].X,B+Points[I].Y,C,Width);}
 void Icon(int32 Kind,double A,double B,FLinearColor C=Ivory){
  if(Kind==0){Stroke(A,B,{{-10,-13},{12,0},{-10,13},{-10,-13}},C);}
  else if(Kind==1||Kind==2){Circle(A,B,13,C);Stroke(A,B,{{-19,-2},{-13,4},{-6,-2}},C);}
  else if(Kind==3){Stroke(A,B,{{-15,11},{-15,-10},{-7,-13},{0,-10},{8,-13},{15,-10},{15,11},{8,8},{0,11},{-7,8},{-15,11}},C);Line(A,B-10,A,B+11,C);}
  else if(Kind==4){Stroke(A,B,{{-8,-15},{11,-15},{11,15},{-8,15}},C);Stroke(A,B,{{-18,0},{2,0},{-4,-6},{2,0},{-4,6}},C);}
  else if(Kind==5){Line(A-14,B,A+14,B,C);Line(A,B-14,A,B+14,C);for(int32 D:{-1,1}){Stroke(A,B,{{double(D*9),-4},{double(D*14),0},{double(D*9),4}},C);Stroke(A,B,{{-4,double(D*9)},{0,double(D*14)},{4,double(D*9)}},C);}}
  else if(Kind==6){Circle(A,B,12,C);Line(A-18,B,A-5,B,C);Line(A+5,B,A+18,B,C);Line(A,B-18,A,B-5,C);Line(A,B+5,A,B+18,C);}
  else if(Kind>=7&&Kind<=11){
   if(Kind==11){Circle(A-14,B-2,3,C);Stroke(A,B,{{-10,1},{0,3},{12,1},{23,1}},C,3);Stroke(A,B,{{-1,3},{-11,10},{-23,8}},C,3);Stroke(A,B,{{3,3},{9,9},{18,9}},C,3);}
   else if(Kind==10){Circle(A+2,B-13,3,C);Stroke(A,B,{{0,-7},{-5,1},{7,4},{1,13},{13,13}},C,3);Stroke(A,B,{{-4,0},{-9,9},{-15,11}},C,3);Stroke(A,B,{{0,-5},{9,0},{16,-4}},C,3);}
   else if(Kind==8){Circle(A,B-17,3,C);Stroke(A,B,{{0,-10},{0,2},{8,14},{13,16}},C,3);Stroke(A,B,{{0,2},{-5,11},{-11,17}},C,3);Stroke(A,B,{{0,-6},{-7,2},{-9,8}},C,3);Stroke(A,B,{{0,-6},{7,0},{13,2}},C,3);}
   else {Circle(A+2,B-17,3,C);Stroke(A,B,{{1,-10},{-3,1},{10,12},{19,14}},C,3);Stroke(A,B,{{-3,1},{-11,8},{-17,15}},C,3);Stroke(A,B,{{0,-7},{-9,-4},{-16,1}},C,3);Stroke(A,B,{{0,-7},{8,-3},{15,-10}},C,3);if(Kind==9)Stroke(A,B,{{-22,12},{-22,-10},{-27,-5},{-22,-10},{-17,-5}},C);}
  }else if(Kind==12||Kind==13){Circle(A,B+2,12,C);Stroke(A,B,{{-6,-10},{-6,-17},{7,-17},{7,-10},{16,-6}},C);if(Kind==13){Stroke(A,B,{{-6,-24},{-11,-30},{-7,-36}},Muted);Stroke(A,B,{{5,-24},{1,-30},{5,-36}},Muted);}}
  else if(Kind==14){Stroke(A,B,{{-14,-12},{14,-12},{14,13},{-14,13},{-14,-12},{0,-4},{14,-12}},C);}
  else if(Kind==15){Circle(A,B,14,C);Stroke(A,B,{{-7,0},{-1,7},{10,-8}},C,3);}
  else if(Kind==16){Circle(A,B,13,C);Circle(A,B,5,C);for(int32 D:{-1,1}){Line(A-19,B*1.,A-13,B,C);Line(A+13,B,A+19,B,C);Line(A,B+D*13,A,B+D*19,C);}}
  else if(Kind==18){Outline(A-12,B-2,24,17,C);Stroke(A,B,{{-7,-2},{-7,-10},{-4,-14},{4,-14},{7,-10},{7,-2}},C);}
  else {Stroke(A,B,{{-15,12},{-15,-3},{-7,-3},{-7,-12},{8,-12},{8,-3},{15,-3},{15,12}},C);Line(A-15,B+12,A+15,B+12,C);}
 }
 void Navigation(const FString& T,double A,double B,double W,bool Selected){Write(T,A+W*.5,B+14,21,Selected?Brass:Ivory,2,95,true);if(Selected)Line(A+10,B+54,A+W-10,B+54,Brass,2);}
 void Corners(double A,double B,double W,double Height){for(int32 I=0;I<4;++I){double CX=A+(I%2?W:0),CY=B+(I/2?Height:0),DX=I%2?-1:1,DY=I/2?-1:1;Line(CX,CY,CX+DX*16,CY,Brass);Line(CX,CY,CX,CY+DY*16,Brass);}}
};
