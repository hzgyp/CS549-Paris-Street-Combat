using UnrealBuildTool;
public class ParisNavDiagnosticsV1 : ModuleRules
{
    public ParisNavDiagnosticsV1(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new[] { "Core", "CoreUObject", "Engine" });
        PrivateDependencyModuleNames.AddRange(new[] { "AIModule", "NavigationSystem", "Json" });
    }
}
