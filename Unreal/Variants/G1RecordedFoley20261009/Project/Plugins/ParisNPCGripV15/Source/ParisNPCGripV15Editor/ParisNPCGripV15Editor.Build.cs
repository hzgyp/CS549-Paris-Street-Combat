using UnrealBuildTool;
public class ParisNPCGripV15Editor : ModuleRules
{
    public ParisNPCGripV15Editor(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage=PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new[]{"Core","CoreUObject","Engine","ParisNPCGripV15","AnimGraph","BlueprintGraph"});
        PrivateDependencyModuleNames.AddRange(new[]{"UnrealEd","AssetTools","Kismet","KismetCompiler","Json"});
    }
}
