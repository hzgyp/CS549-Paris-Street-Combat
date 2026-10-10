using UnrealBuildTool;

public class ParisMuzzleFlashV1 : ModuleRules
{
    public ParisMuzzleFlashV1(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new[] { "Core", "CoreUObject", "Engine", "Niagara" });
        PrivateDependencyModuleNames.AddRange(new[] { "Json" });
        if (Target.bBuildEditor) PrivateDependencyModuleNames.AddRange(new[] { "MeshDescription", "StaticMeshDescription" });
    }
}
