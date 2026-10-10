using UnrealBuildTool;

public class WW2FranceLiberationTarget : TargetRules
{
	public WW2FranceLiberationTarget(TargetInfo Target) : base(Target)
	{
		DefaultBuildSettings = BuildSettingsVersion.Latest;
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
		Type = TargetType.Game;
		ExtraModuleNames.Add("WW2FranceLiberation");
	}
}
