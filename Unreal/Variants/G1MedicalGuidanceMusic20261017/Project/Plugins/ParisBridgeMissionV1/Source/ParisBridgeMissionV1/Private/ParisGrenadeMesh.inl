// Streaming density comes from the unchanged authored position/UV triangles.
FMeshUVChannelInfo RuntimeExteriorUVInfo(const TArray<TSharedPtr<FJsonValue>>& Rows){
    TArray<FVector2f> Samples;Samples.Reserve(Rows.Num()/3);
    for(int32 I=0;I<Rows.Num();I+=3){
        FVector3f P[3];FVector2f UV[3];
        for(int32 J=0;J<3;++J){const auto& R=Rows[I+J]->AsArray();P[J]=FVector3f(R[0]->AsNumber(),R[1]->AsNumber(),R[2]->AsNumber());UV[J]=FVector2f(R[10]->AsNumber(),R[11]->AsNumber());}
        const auto A=UV[1]-UV[0],B=UV[2]-UV[0];const float UVArea=FMath::Abs(A.X*B.Y-A.Y*B.X),WorldArea=FVector3f::CrossProduct(P[1]-P[0],P[2]-P[0]).Size();
        if(WorldArea>UE_SMALL_NUMBER&&UVArea>UE_SMALL_NUMBER)Samples.Emplace(FMath::Sqrt(WorldArea/UVArea),FMath::Sqrt(WorldArea));
    }
    Samples.Sort([](const FVector2f& A,const FVector2f& B){return A.X<B.X;});
    const int32 Cut=FMath::FloorToInt(.1f*Samples.Num());float Weighted=0,Weight=0;
    for(int32 I=Cut;I<Samples.Num()-Cut;++I){Weighted+=Samples[I].X*Samples[I].Y;Weight+=Samples[I].Y;}
    checkf(Weight>UE_SMALL_NUMBER,TEXT("Exterior UV streaming density has no valid triangles"));
    FMeshUVChannelInfo Info;Info.bInitialized=true;Info.LocalUVDensities[0]=Weighted/Weight;
    checkf(FMath::IsFinite(Info.LocalUVDensities[0])&&Info.LocalUVDensities[0]>0,TEXT("Exterior UV streaming density invalid"));return Info;
}
// Blender-exported inert exterior, built transiently without native package writes.
TStrongObjectPtr<UStaticMesh> GrenadeMeshCaches[2];
TStrongObjectPtr<UMaterialInstanceDynamic> GrenadeMaterialCaches[2];
TArray<TStrongObjectPtr<UTexture2D>> GrenadeTextures;
UStaticMesh* GrenadeMesh(UWorld* W,const FString& Kind){
    const int32 Index=Kind==TEXT("Frag")?0:1;const FString Stem=Index==0?TEXT("frag"):TEXT("smoke");
    auto& GrenadeMeshCache=GrenadeMeshCaches[Index];auto& GrenadeMaterialCache=GrenadeMaterialCaches[Index];
    if(GrenadeMeshCache.IsValid())return GrenadeMeshCache.Get();
    const FString Dir=FPaths::ConvertRelativePathToFull(FPaths::Combine(FPlatformProcess::BaseDir(),TEXT("../../Equipment/Grenades"),Kind));
    FString Text;checkf(FFileHelper::LoadFileToString(Text,*(Dir/(Stem+TEXT("_geometry.json")))),TEXT("Grenade exterior geometry missing"));
    TSharedPtr<FJsonObject> O;auto Reader=TJsonReaderFactory<>::Create(Text);checkf(FJsonSerializer::Deserialize(Reader,O)&&O.IsValid(),TEXT("Grenade exterior JSON invalid"));
    const int32 Count=int32(O->GetNumberField(TEXT("triangles")));const auto& Rows=O->GetArrayField(TEXT("vertices"));
    checkf(O->GetNumberField(TEXT("schema"))==1&&Count==(Index==0?2733:7562)&&Rows.Num()==Count*3,TEXT("Grenade exterior identity/count mismatch"));
    // Read-only clone of an already-cooked glTF shader with all three texture branches enabled.
    auto* Parent=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/ParisCombat/Weapons/GermanRifleUEV1/ImportV1/GermanRifle_FineWood_V15/Materials/V15_FineWalnut_Handguard.V15_FineWalnut_Handguard"));
    checkf(Parent,TEXT("Grenade cooked PBR shader unavailable"));
    auto* Material=UMaterialInstanceDynamic::Create(Parent,GetTransientPackage());
    GrenadeMaterialCache.Reset(Material);
    for(const auto& Pair:{TPair<FString,FString>(TEXT("BaseColorTexture"),(Stem+TEXT("_albedo.png"))),TPair<FString,FString>(TEXT("MetallicRoughnessTexture"),(Stem+TEXT("_orm.png"))),TPair<FString,FString>(TEXT("NormalTexture"),(Stem+TEXT("_normal.png")))}){
        auto* Texture=FImageUtils::ImportFileAsTexture2D(Dir/Pair.Value);
        checkf(Texture&&Texture->GetSizeX()==1024&&Texture->GetSizeY()==1024,TEXT("Grenade PBR texture invalid"));
        Texture->SRGB=Pair.Key==TEXT("BaseColorTexture");Texture->UpdateResource();
        Material->SetTextureParameterValue(*Pair.Key,Texture);GrenadeTextures.Emplace(Texture);
    }
    Material->SetVectorParameterValue(TEXT("BaseColorFactor"),FLinearColor::White);
    Material->SetScalarParameterValue(TEXT("MetallicFactor"),1);Material->SetScalarParameterValue(TEXT("RoughnessFactor"),1);
    Material->SetScalarParameterValue(TEXT("NormalScale"),1);Material->SetScalarParameterValue(TEXT("SpecularFactor"),.5);
    FMeshDescription Description;FStaticMeshAttributes Attr(Description);Attr.Register();
    auto Positions=Attr.GetVertexPositions();auto Normals=Attr.GetVertexInstanceNormals();auto Tangents=Attr.GetVertexInstanceTangents();
    auto Signs=Attr.GetVertexInstanceBinormalSigns();auto UVs=Attr.GetVertexInstanceUVs();UVs.SetNumChannels(1);
    auto Colors=Attr.GetVertexInstanceColors();const FPolygonGroupID Group=Description.CreatePolygonGroup();Attr.GetPolygonGroupMaterialSlotNames()[Group]=TEXT("MinePBR");
    for(int32 I=0;I<Rows.Num();I+=3){TArray<FVertexInstanceID> Triangle;
        for(int32 J=0;J<3;++J){const auto& R=Rows[I+J]->AsArray();checkf(R.Num()==12,TEXT("Grenade vertex schema invalid"));
            double V[12];for(int32 K=0;K<12;++K){V[K]=R[K]->AsNumber();checkf(FMath::IsFinite(V[K]),TEXT("Grenade nonfinite vertex"));}
            checkf(FVector(V[0],V[1],V[2]).GetAbsMax()<18,TEXT("Grenade scale invalid"));
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
    checkf(Mesh->BuildFromMeshDescriptions({&Description},Params),TEXT("Grenade runtime render-buffer build failed"));
    const auto& Density=Mesh->GetStaticMaterials()[0].UVChannelData;
    UE_LOG(LogTemp,Display,TEXT("PARIS_EQUIPMENT_UV mesh=%s kind=%s initialized=%d uv0=%.6f unused_zero=%d"),*Mesh->GetPathName(),*Kind,int(Density.bInitialized),Density.LocalUVDensities[0],int(Density.LocalUVDensities[1]==0&&Density.LocalUVDensities[2]==0&&Density.LocalUVDensities[3]==0));
    GrenadeMeshCache.Reset(Mesh);Event(W,TEXT("mine_mesh_ready"),Kind+TEXT(" exterior / PBR / fixed original attachment"),Count);
    return Mesh;
}
void GrenadeVisual(UWorld* W,AActor* A,const FString& Kind){
    auto* C=NewObject<UStaticMeshComponent>(A);A->AddInstanceComponent(C);
    C->SetStaticMesh(GrenadeMesh(W,Kind));C->SetupAttachment(A->GetRootComponent());
    C->SetCollisionEnabled(ECollisionEnabled::NoCollision);C->SetCanEverAffectNavigation(false);C->RegisterComponent();
}
