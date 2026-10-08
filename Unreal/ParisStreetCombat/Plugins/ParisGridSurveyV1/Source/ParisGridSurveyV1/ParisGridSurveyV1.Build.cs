using UnrealBuildTool;
public class ParisGridSurveyV1 : ModuleRules
{
    public ParisGridSurveyV1(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine", "NavigationSystem" });
        PrivateDependencyModuleNames.AddRange(new string[] { "Json" });
    }
}
