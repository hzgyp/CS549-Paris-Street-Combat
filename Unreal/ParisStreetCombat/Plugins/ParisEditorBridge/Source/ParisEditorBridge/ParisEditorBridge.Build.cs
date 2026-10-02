using UnrealBuildTool;

public class ParisEditorBridge : ModuleRules
{
    public ParisEditorBridge(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new[] { "Core", "CoreUObject", "Engine" });
        PrivateDependencyModuleNames.AddRange(new[] {
            "UnrealEd", "BlueprintGraph", "KismetCompiler", "AnimGraph", "AnimGraphRuntime",
            "AssetTools", "Json", "RenderCore", "RHI"
        });
    }
}
