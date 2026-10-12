using UnrealBuildTool;

public class ParisGripBindingV18 : ModuleRules
{
    public ParisGripBindingV18(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new[] { "Core", "CoreUObject", "Engine" });
        PrivateDependencyModuleNames.AddRange(new[] { "AnimationCore", "Json" });
    }
}
