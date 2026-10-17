// Blender-exported inert exterior, built transiently without native package writes.
TStrongObjectPtr<UStaticMesh> PressureMineMeshCache;
TStrongObjectPtr<UMaterialInstanceDynamic> PressureMineMaterialCache;
TArray<TStrongObjectPtr<UTexture2D>> PressureMineTextures;
UStaticMesh* PressureMineMesh(UWorld* W){
    if(PressureMineMeshCache.IsValid())return PressureMineMeshCache.Get();
    const FString Dir=FPaths::ConvertRelativePathToFull(FPaths::Combine(FPlatformProcess::BaseDir(),TEXT("../../Equipment/Mine")));
    FString Text;checkf(FFileHelper::LoadFileToString(Text,*(Dir/TEXT("mine_geometry.json"))),TEXT("Pressure mine exterior geometry missing"));
    TSharedPtr<FJsonObject> O;auto Reader=TJsonReaderFactory<>::Create(Text);checkf(FJsonSerializer::Deserialize(Reader,O)&&O.IsValid(),TEXT("Pressure mine exterior JSON invalid"));
    const int32 Count=int32(O->GetNumberField(TEXT("triangles")));const auto& Rows=O->GetArrayField(TEXT("vertices"));
    checkf(O->GetNumberField(TEXT("schema"))==1&&Count==10809&&Rows.Num()==Count*3,TEXT("Pressure mine exterior identity/count mismatch"));
    // Read-only clone of an already-cooked glTF shader with all three texture branches enabled.
    auto* Parent=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/ParisCombat/Weapons/GermanRifleUEV1/ImportV1/GermanRifle_FineWood_V15/Materials/V15_FineWalnut_Handguard.V15_FineWalnut_Handguard"));
    checkf(Parent,TEXT("Pressure mine cooked PBR shader unavailable"));
    auto* Material=UMaterialInstanceDynamic::Create(Parent,GetTransientPackage());
    PressureMineMaterialCache.Reset(Material);
    for(const auto& Pair:{TPair<FString,FString>(TEXT("BaseColorTexture"),TEXT("mine_albedo.png")),TPair<FString,FString>(TEXT("MetallicRoughnessTexture"),TEXT("mine_orm.png")),TPair<FString,FString>(TEXT("NormalTexture"),TEXT("mine_normal.png"))}){
        auto* Texture=FImageUtils::ImportFileAsTexture2D(Dir/Pair.Value);
        checkf(Texture&&Texture->GetSizeX()==1024&&Texture->GetSizeY()==1024,TEXT("Pressure mine PBR texture invalid"));
        Texture->SRGB=Pair.Key==TEXT("BaseColorTexture");Texture->UpdateResource();
        Material->SetTextureParameterValue(*Pair.Key,Texture);PressureMineTextures.Emplace(Texture);
    }
    Material->SetVectorParameterValue(TEXT("BaseColorFactor"),FLinearColor::White);
    Material->SetScalarParameterValue(TEXT("MetallicFactor"),1);Material->SetScalarParameterValue(TEXT("RoughnessFactor"),1);
    Material->SetScalarParameterValue(TEXT("NormalScale"),1);Material->SetScalarParameterValue(TEXT("SpecularFactor"),.5);
    FMeshDescription Description;FStaticMeshAttributes Attr(Description);Attr.Register();
    auto Positions=Attr.GetVertexPositions();auto Normals=Attr.GetVertexInstanceNormals();auto Tangents=Attr.GetVertexInstanceTangents();
    auto Signs=Attr.GetVertexInstanceBinormalSigns();auto UVs=Attr.GetVertexInstanceUVs();UVs.SetNumChannels(1);
    auto Colors=Attr.GetVertexInstanceColors();const FPolygonGroupID Group=Description.CreatePolygonGroup();Attr.GetPolygonGroupMaterialSlotNames()[Group]=TEXT("MinePBR");
    for(int32 I=0;I<Rows.Num();I+=3){TArray<FVertexInstanceID> Triangle;
        for(int32 J=0;J<3;++J){const auto& R=Rows[I+J]->AsArray();checkf(R.Num()==12,TEXT("Pressure mine vertex schema invalid"));
            double V[12];for(int32 K=0;K<12;++K){V[K]=R[K]->AsNumber();checkf(FMath::IsFinite(V[K]),TEXT("Pressure mine nonfinite vertex"));}
            checkf(FVector(V[0],V[1],V[2]).GetAbsMax()<40,TEXT("Pressure mine scale invalid"));
            const FVertexID Vertex=Description.CreateVertex();Positions[Vertex]=FVector3f(V[0],V[1],V[2]);
            const FVertexInstanceID VI=Description.CreateVertexInstance(Vertex);Normals[VI]=FVector3f(V[3],V[4],V[5]);Tangents[VI]=FVector3f(V[6],V[7],V[8]);
            Signs[VI]=float(V[9]);UVs.Set(VI,0,FVector2f(V[10],V[11]));Colors[VI]=FVector4f(1,1,1,1);Triangle.Add(VI);
        }
        // UE uses clockwise front faces. The authored Blender-to-UE reflection
        // was already followed by a loop swap; undo that extra swap here.
        Swap(Triangle[1],Triangle[2]);Description.CreateTriangle(Group,Triangle);
    }
    auto* Mesh=NewObject<UStaticMesh>(GetTransientPackage());FStaticMaterial Slot(Material,TEXT("MinePBR"));Slot.UVChannelData=RuntimeExteriorUVInfo(Rows);Mesh->GetStaticMaterials().Add(Slot);
    UStaticMesh::FBuildMeshDescriptionsParams Params;Params.bFastBuild=true;Params.bBuildSimpleCollision=false;Params.bMarkPackageDirty=false;Params.bCommitMeshDescription=false;Params.bAllowCpuAccess=true;
    checkf(Mesh->BuildFromMeshDescriptions({&Description},Params),TEXT("Pressure mine runtime render-buffer build failed"));
    const auto& Density=Mesh->GetStaticMaterials()[0].UVChannelData;
    UE_LOG(LogTemp,Display,TEXT("PARIS_EQUIPMENT_UV mesh=%s kind=Mine initialized=%d uv0=%.6f unused_zero=%d"),*Mesh->GetPathName(),int(Density.bInitialized),Density.LocalUVDensities[0],int(Density.LocalUVDensities[1]==0&&Density.LocalUVDensities[2]==0&&Density.LocalUVDensities[3]==0));
    PressureMineMeshCache.Reset(Mesh);Event(W,TEXT("mine_mesh_ready"),TEXT("Blender exterior 10809 triangles / baked PBR / transient shader instance"),Count);
    return Mesh;
}
void PressureMineVisual(UWorld* W,FTrap& T){
    T.Visual=Prop(W,TEXT("Trap"),T.Position);auto* C=NewObject<UStaticMeshComponent>(T.Visual.Get());T.Visual->AddInstanceComponent(C);
    C->SetStaticMesh(PressureMineMesh(W));C->SetupAttachment(T.Visual->GetRootComponent());C->SetCollisionEnabled(ECollisionEnabled::NoCollision);C->SetCanEverAffectNavigation(false);C->RegisterComponent();
    if(T.State!=TEXT("Armed"))T.Visual->SetActorHiddenInGame(true);
}
bool FootTouchesMine(ACharacter* C,const FTrap& T){
    if(!C||Dead(C)||!C->GetCharacterMovement()||!C->GetCharacterMovement()->IsMovingOnGround())return false;
    const auto* Capsule=C->GetCapsuleComponent();const FVector Feet=C->GetActorLocation()-FVector(0,0,Capsule->GetScaledCapsuleHalfHeight());
    return FVector::Dist2D(Feet,T.Position)<=Capsule->GetScaledCapsuleRadius()+14&&FMath::Abs(Feet.Z-T.Position.Z)<=18;
}
