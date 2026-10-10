using UnrealBuildTool;
public class WW2FranceLiberationEditorTarget : TargetRules {
 public WW2FranceLiberationEditorTarget(TargetInfo Target) : base(Target) {
  Type=TargetType.Editor; DefaultBuildSettings=BuildSettingsVersion.Latest;
  IncludeOrderVersion=EngineIncludeOrderVersion.Latest; ExtraModuleNames.Add("WW2FranceLiberation");
 }
}
