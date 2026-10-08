using UnrealBuildTool;
public class ParisMapSurveyV1 : ModuleRules
{
    public ParisMapSurveyV1(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new[] {"Core", "CoreUObject", "Engine", "NavigationSystem", "AIModule"});
        PrivateDependencyModuleNames.AddRange(new[] {"Json"});
    }
}
