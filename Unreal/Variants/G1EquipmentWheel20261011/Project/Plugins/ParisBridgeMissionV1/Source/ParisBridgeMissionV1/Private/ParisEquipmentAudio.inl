uint32 ReadLE(const uint8* B){return uint32(B[0])|(uint32(B[1])<<8)|(uint32(B[2])<<16)|(uint32(B[3])<<24);}
void ExplosionAV(UWorld* W,FVector At){auto& S=Session(W);TArray<uint8> Bytes;FString File=FPaths::ConvertRelativePathToFull(FPaths::Combine(FPlatformProcess::BaseDir(),TEXT("../../Audio/equipment_explosion.wav")));if(!FPaths::FileExists(File))File=FPaths::ProjectDir()/TEXT("Audio/equipment_explosion.wav");checkf(FFileHelper::LoadFileToArray(Bytes,*File)&&Bytes.Num()>44,TEXT("Equipment explosion PCM is required"));int32 Start=0,Size=0;
    for(int32 I=12;I+8<=Bytes.Num();){const uint32 Chunk=ReadLE(Bytes.GetData()+I+4);if(Chunk>uint32(Bytes.Num()-I-8))break;if(FMemory::Memcmp(Bytes.GetData()+I,"data",4)==0){Start=I+8;Size=int32(Chunk);break;}I+=8+int32(Chunk)+(Chunk&1);}check(Size>0);
    auto* Wave=NewObject<USoundWaveProcedural>();Wave->SetSampleRate(48000);Wave->NumChannels=1;Wave->Duration=Size/96000.f;Wave->SoundGroup=SOUNDGROUP_Effects;Wave->bLooping=false;Wave->QueueAudio(Bytes.GetData()+Start,Size);
    auto* Attenuation=NewObject<USoundAttenuation>();auto& A=Attenuation->Attenuation;A.bAttenuate=true;A.bSpatialize=true;A.AttenuationShape=EAttenuationShape::Sphere;A.AttenuationShapeExtents=FVector(150,0,0);A.FalloffDistance=4000;A.DistanceAlgorithm=EAttenuationDistanceModel::Logarithmic;
    S.Waves.Emplace(Wave);S.Voices.Add(UGameplayStatics::SpawnSoundAtLocation(W,Wave,At,FRotator::ZeroRotator,1.4f,1,0,Attenuation,nullptr,true));
    ExplosionVisual(W,At);
    Event(W,TEXT("explosion_recorded_cue"),TEXT("qubodup162363"),Wave->Duration);
}
