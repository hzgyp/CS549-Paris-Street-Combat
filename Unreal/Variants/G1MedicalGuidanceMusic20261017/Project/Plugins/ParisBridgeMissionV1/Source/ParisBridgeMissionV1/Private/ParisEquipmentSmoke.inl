// Transient CPU smoke; the licensed material/atlas inputs remain read-only.
UDistributionFloatConstant* FloatConstant(UObject* Outer,float V){auto* D=NewObject<UDistributionFloatConstant>(Outer);D->Constant=V;return D;}
UDistributionVectorConstant* VectorConstant(UObject* Outer,FVector V){auto* D=NewObject<UDistributionVectorConstant>(Outer);D->Constant=V;return D;}
UDistributionVectorUniform* VectorRange(UObject* Outer,FVector Low,FVector High){auto* D=NewObject<UDistributionVectorUniform>(Outer);D->Min=Low;D->Max=High;D->bLockAxes=false;return D;}
UParticleSystem* DenseSmoke(FSmoke& C){
    auto* Source=LoadObject<UParticleSystem>(nullptr,TEXT("/Game/WW2City/Library_Meshingun/VFX_Meshingun/SmokeFog/Niagara/P_Smoke.P_Smoke"));check(Source&&!Source->Emitters.IsEmpty());
    auto* SourceLOD=Source->Emitters[0]->LODLevels[0].Get();auto* PS=NewObject<UParticleSystem>();auto* Emitter=NewObject<UParticleSpriteEmitter>(PS);auto* LOD=NewObject<UParticleLODLevel>(Emitter);LOD->Level=0;LOD->bEnabled=true;
    // Never DuplicateObject a cooked Required module (MI027).
    LOD->RequiredModule=NewObject<UParticleModuleRequired>(PS);auto* Required=LOD->RequiredModule.Get();
    auto* Material=UMaterialInstanceDynamic::Create(SourceLOD->RequiredModule->Material,PS);C.Material=Material;
    Material->SetScalarParameterValue(TEXT("Opacity"),3.f*float(SmokeFactor(C)));Material->SetScalarParameterValue(TEXT("Fade_Distance"),20.f);Material->SetVectorParameterValue(TEXT("Color"),FLinearColor(.72,.73,.70));
    Required->Material=Material;Required->SubImages_Horizontal=SourceLOD->RequiredModule->SubImages_Horizontal;Required->SubImages_Vertical=SourceLOD->RequiredModule->SubImages_Vertical;Required->InterpolationMethod=SourceLOD->RequiredModule->InterpolationMethod;
    const auto Schedule=ParisSmokePresentation::Remaining(C.Life);
    Required->EmitterDuration=float(Schedule.EmissionDuration);Required->EmitterLoops=1;Required->bEmitterDurationUseRange=false;Required->bUseLegacyEmitterTime=false;
    Required->bUseLocalSpace=false;Required->bKillOnDeactivate=false;Required->bKillOnCompleted=false;
    Required->ScreenAlignment=PSA_FacingCameraPosition;Required->bUseMaxDrawCount=true;Required->MaxDrawCount=160;
    LOD->SpawnModule=NewObject<UParticleModuleSpawn>(PS);LOD->SpawnModule->Rate.Distribution=FloatConstant(PS,48);LOD->SpawnModule->RateScale.Distribution=FloatConstant(PS,1);LOD->SpawnModule->BurstScale.Distribution=FloatConstant(PS,1);LOD->SpawnModule->bApplyGlobalSpawnRateScale=false;
    auto* Life=NewObject<UParticleModuleLifetime>(PS);Life->Lifetime.Distribution=FloatConstant(PS,float(ParisSmokePresentation::PuffSeconds));
    auto* Size=NewObject<UParticleModuleSize>(PS);Size->StartSize.Distribution=VectorConstant(PS,FVector(24));
    auto* Expansion=NewObject<UParticleModuleSizeMultiplyLife>(PS);auto* Growth=NewObject<UDistributionVectorConstantCurve>(PS);
    for(const auto& Key:ParisSmokePresentation::Expansion)Growth->ConstantCurve.AddPoint(Key.Time,FVector(Key.Value));
    Expansion->LifeMultiplier.Distribution=Growth;Expansion->MultiplyX=Expansion->MultiplyY=Expansion->MultiplyZ=true;
    auto* Velocity=NewObject<UParticleModuleVelocity>(PS);Velocity->StartVelocity.Distribution=VectorRange(PS,FVector(-70,-70,50),FVector(70,70,90));Velocity->StartVelocityRadial.Distribution=FloatConstant(PS,0);
    auto* Location=NewObject<UParticleModuleLocation>(PS);Location->StartLocation.Distribution=VectorRange(PS,FVector(-1,-1,-.3),FVector(1,1,.3));
    auto* Color=NewObject<UParticleModuleColorOverLife>(PS);Color->ColorOverLife.Distribution=VectorConstant(PS,FVector(.75,.75,.74));auto* Alpha=NewObject<UDistributionFloatConstantCurve>(PS);
    for(const auto& Key:ParisSmokePresentation::Alpha)Alpha->ConstantCurve.AddPoint(Key.Time,Key.Value);
    Color->AlphaOverLife.Distribution=Alpha;
    LOD->Modules={Life,Size,Expansion,Velocity,Location,Color};
    for(auto Module:SourceLOD->Modules)if(Module->IsA<UParticleModuleSubUV>()||Module->IsA<UParticleModuleParameterDynamic>())LOD->Modules.Add(Module);
    Emitter->LODLevels.Add(LOD);Emitter->UpdateModuleLists();PS->Emitters.Add(Emitter);PS->LODMethod=PARTICLESYSTEMLODMETHOD_DirectSet;
    // Dynamic bounds follow world-space puffs even if the burning canister moves.
    PS->bAutoDeactivate=false;PS->SecondsBeforeInactive=0;PS->bUseFixedRelativeBoundingBox=false;
    PS->WarmupTime=float(Schedule.Warmup);PS->WarmupTickRate=1.f/60.f;
    return PS;
}
