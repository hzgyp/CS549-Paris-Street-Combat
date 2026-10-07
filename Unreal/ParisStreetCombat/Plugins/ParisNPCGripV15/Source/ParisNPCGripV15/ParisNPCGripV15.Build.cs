using UnrealBuildTool;
public class ParisNPCGripV15 : ModuleRules
{
    public ParisNPCGripV15(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage=PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new[]{"Core","CoreUObject","Engine"});
        PrivateDependencyModuleNames.AddRange(new[]{"Json"});
    }
}
