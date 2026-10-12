using UnrealBuildTool;
public class WW2FranceLiberation : ModuleRules {
 public WW2FranceLiberation(ReadOnlyTargetRules Target):base(Target) {
  PCHUsage=PCHUsageMode.UseExplicitOrSharedPCHs;
  PrivateDependencyModuleNames.AddRange(new string[]{"Core"});
 }
}
