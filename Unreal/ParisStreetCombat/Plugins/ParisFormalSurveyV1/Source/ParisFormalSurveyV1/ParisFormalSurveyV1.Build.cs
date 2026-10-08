using UnrealBuildTool;
public class ParisFormalSurveyV1 : ModuleRules
{
    public ParisFormalSurveyV1(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine", "AIModule", "NavigationSystem" });
        PrivateDependencyModuleNames.AddRange(new string[] { "Json" });
    }
}
