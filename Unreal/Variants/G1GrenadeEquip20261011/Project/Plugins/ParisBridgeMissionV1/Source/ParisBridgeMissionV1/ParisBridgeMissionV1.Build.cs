using UnrealBuildTool;
public class ParisBridgeMissionV1 : ModuleRules
{
    public ParisBridgeMissionV1(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new[] { "Core", "CoreUObject", "Engine", "InputCore" });
        PrivateDependencyModuleNames.AddRange(new[] { "MovieSceneCapture", "Slate", "SlateCore", "RenderCore", "RHI", "MeshDescription", "StaticMeshDescription", "UMG", "ImageWrapper", "AudioMixer", "AIModule", "NavigationSystem", "Json", "ParisGripBindingV18" });
    }
}

