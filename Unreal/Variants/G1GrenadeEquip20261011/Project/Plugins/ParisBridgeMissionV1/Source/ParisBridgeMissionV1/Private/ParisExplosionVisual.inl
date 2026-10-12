// Existing authored transient Niagara fire and dust; render only. No damage, collision or smoke cover.
UDistributionFloatConstant* FloatConstant(UObject* Outer,float V);
UDistributionVectorConstant* VectorConstant(UObject* Outer,FVector V);
UDistributionVectorUniform* VectorRange(UObject* Outer,FVector Low,FVector High);
UParticleSystem* BlastParticles(bool Fire){
 auto* Source=LoadObject<UParticleSystem>(nullptr,TEXT("/Game/WW2City/Library_Meshingun/VFX_Meshingun/SmokeFog/Niagara/P_Smoke.P_Smoke"));check(Source&&!Source->Emitters.IsEmpty());
 auto* SourceLOD=Source->Emitters[0]->LODLevels[0].Get();auto* PS=NewObject<UParticleSystem>();auto* E=NewObject<UParticleSpriteEmitter>(PS);auto* L=NewObject<UParticleLODLevel>(E);L->Level=0;L->bEnabled=true;
 L->RequiredModule=NewObject<UParticleModuleRequired>(PS);auto* R=L->RequiredModule.Get();
 // Existing fire material has a cooked ParticleSprites shader, unlike Niagara-only M_Glow.
 auto* Base=Fire?LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/WW2City/Environment/Particle/Fire/Material/Fire/M_Fire_SubUV_11X11_Noise.M_Fire_SubUV_11X11_Noise")):SourceLOD->RequiredModule->Material.Get();check(Base);auto* Mat=UMaterialInstanceDynamic::Create(Base,PS);Mat->SetScalarParameterValue(TEXT("Opacity"),1.5f);Mat->SetScalarParameterValue(TEXT("Fade_Distance"),0.f);Mat->SetVectorParameterValue(TEXT("Color"),FLinearColor(.32,.29,.25));R->Material=Fire?Base:Mat;
 R->SubImages_Horizontal=SourceLOD->RequiredModule->SubImages_Horizontal;R->SubImages_Vertical=SourceLOD->RequiredModule->SubImages_Vertical;R->InterpolationMethod=SourceLOD->RequiredModule->InterpolationMethod;
 if(Fire){R->SubImages_Horizontal=11;R->SubImages_Vertical=11;R->InterpolationMethod=PSUVIM_Linear_Blend;}
 R->EmitterDuration=.4f;R->EmitterLoops=1;R->bUseLocalSpace=false;R->ScreenAlignment=PSA_FacingCameraPosition;R->bUseMaxDrawCount=true;R->MaxDrawCount=48;
 L->SpawnModule=NewObject<UParticleModuleSpawn>(PS);L->SpawnModule->Rate.Distribution=FloatConstant(PS,0);L->SpawnModule->RateScale.Distribution=FloatConstant(PS,1);L->SpawnModule->BurstScale.Distribution=FloatConstant(PS,1);L->SpawnModule->bApplyGlobalSpawnRateScale=false;FParticleBurst Burst;Burst.Count=Fire?24:18;Burst.CountLow=Burst.Count;Burst.Time=0;L->SpawnModule->BurstList.Add(Burst);
 auto* Life=NewObject<UParticleModuleLifetime>(PS);Life->Lifetime.Distribution=FloatConstant(PS,Fire?.65f:1.6f);
 auto* Size=NewObject<UParticleModuleSize>(PS);Size->StartSize.Distribution=VectorRange(PS,Fire?FVector(90):FVector(85),Fire?FVector(140):FVector(140));
 auto* Velocity=NewObject<UParticleModuleVelocity>(PS);Velocity->StartVelocity.Distribution=VectorRange(PS,FVector(-150,-150,Fire?75:35),FVector(150,150,Fire?270:100));Velocity->StartVelocityRadial.Distribution=FloatConstant(PS,0);
 auto* Location=NewObject<UParticleModuleLocation>(PS);Location->StartLocation.Distribution=VectorRange(PS,FVector(-30,-30,8),FVector(30,30,20));
 auto* Color=NewObject<UParticleModuleColorOverLife>(PS);Color->ColorOverLife.Distribution=VectorConstant(PS,Fire?FVector(2):FVector(.32,.29,.25));
 auto* Alpha=NewObject<UDistributionFloatConstantCurve>(PS);Alpha->bCanBeBaked=false;Alpha->ConstantCurve.AddPoint(0,1);Alpha->ConstantCurve.AddPoint(.55f,.8f);Alpha->ConstantCurve.AddPoint(1,0);Color->AlphaOverLife.Distribution=Alpha;
 L->Modules={Life,Size,Velocity,Location,Color};
 if(Fire){auto* UV=NewObject<UParticleModuleSubUV>(PS);auto* Frames=NewObject<UDistributionFloatConstantCurve>(PS);Frames->bCanBeBaked=false;Frames->ConstantCurve.AddPoint(0,0);Frames->ConstantCurve.AddPoint(1,120);UV->SubImageIndex.Distribution=Frames;L->Modules.Add(UV);
 auto* Dynamic=NewObject<UParticleModuleParameterDynamic>(PS);Dynamic->DynamicParams.Reset();const FName Names[]={TEXT("LerpNoise"),TEXT("X"),TEXT("Contrast"),TEXT("Scale")};const float Values[]={0,0,1,1};for(int32 I=0;I<4;++I){FEmitterDynamicParameter Param;Param.ParamName=Names[I];Param.bSpawnTimeOnly=true;Param.ValueMethod=EDPV_UserSet;Param.ParamValue.Distribution=FloatConstant(PS,Values[I]);Dynamic->DynamicParams.Add(Param);}Dynamic->UpdateUsageFlags();L->Modules.Add(Dynamic);
 }else for(auto M:SourceLOD->Modules)if(M->IsA<UParticleModuleSubUV>()||M->IsA<UParticleModuleParameterDynamic>())L->Modules.Add(M);
 E->LODLevels.Add(L);E->UpdateModuleLists();PS->Emitters.Add(E);PS->LODMethod=PARTICLESYSTEMLODMETHOD_DirectSet;PS->bAutoDeactivate=true;PS->SecondsBeforeInactive=0;PS->bUseFixedRelativeBoundingBox=true;PS->FixedRelativeBoundingBox=FBox(FVector(-300,-300,-40),FVector(300,300,400));return PS;
}
void ExplosionVisual(UWorld* W,FVector At){
 for(bool Fire:{true,false}){auto* PS=BlastParticles(Fire);auto* C=UGameplayStatics::SpawnEmitterAtLocation(W,PS,At,FRotator::ZeroRotator,FVector::OneVector,true,EPSCPoolMethod::None,true);check(C);C->SetCanEverAffectNavigation(false);
 if(FParse::Param(FCommandLine::Get(),TEXT("ParisBlastDiag"))){TWeakObjectPtr<UParticleSystemComponent> Weak=C;FTimerHandle D;W->GetTimerManager().SetTimer(D,[Weak,Fire](){if(!Weak.IsValid()){UE_LOG(LogTemp,Display,TEXT("PARIS_BLAST_DIAG fire=%d component_gone"),Fire);return;}for(auto* I:Weak->EmitterInstances)if(I){auto* P=I->ActiveParticles?I->GetParticle(0):nullptr;UE_LOG(LogTemp,Display,TEXT("PARIS_BLAST_DIAG fire=%d active=%d alpha=%f size=%s at=%s material=%s"),Fire,I->ActiveParticles,P?P->Color.A:-1.f,P?*P->Size.ToString():TEXT("None"),P?*P->Location.ToString():TEXT("None"),*Weak->GetMaterial(0)->GetPathName());}},.2f,false);}}
 auto* Flash=Prop(W,TEXT("Blast"),At);auto* Light=NewObject<UPointLightComponent>(Flash);Flash->AddInstanceComponent(Light);Light->SetupAttachment(Flash->GetRootComponent());Light->SetIntensity(12000);Light->SetAttenuationRadius(650);Light->SetLightColor(FLinearColor(1,.42,.08));Light->RegisterComponent();Flash->SetLifeSpan(.18f);
 Event(W,TEXT("explosion_visual"),TEXT("transient_warm_flash_embers_dust"));
}
