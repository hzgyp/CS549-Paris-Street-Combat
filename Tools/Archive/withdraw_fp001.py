"""One-time exact FP001 source withdrawal; never restores whole Git files."""
import ast, difflib, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CASE = ROOT / 'Failures/FP001-20261003-first-person-view'
paths = ['Tools/Integration/ue_paris_combat_pie.py',
    'Unreal/ParisStreetCombat/Plugins/ParisEditorBridge/Source/ParisEditorBridge/Private/ParisBlueprintAuthoring.cpp',
    'Unreal/ParisStreetCombat/Plugins/ParisEditorBridge/Source/ParisEditorBridge/Public/ParisBlueprintAuthoring.h']
patches, records = [], []
def once(s, old, new):
    assert s.count(old) == 1, old[:100]
    return s.replace(old, new, 1)

for path in paths:
    active = ROOT/path
    before = (CASE/'Changes/Before'/path).read_bytes()
    assert active.read_bytes() == before, f'Changed after archive snapshot: {path}'
    s = before.decode().replace('\r\n', '\n')
    original = s
    if path.endswith('.py'):
        start = s.index("fp_preview = os.environ.get('CS549_FIRST_PERSON_VIEW_PREVIEW')")
        end = s.index('\nguarded = ', start)
        s = s[:start] + "if os.environ.get('CS549_FIRST_PERSON_VIEW_PREVIEW') == '1':\n    raise RuntimeError('FP001 is archived after visual rejection; its preview is retired')\nif aim_preview:\n    assert checkpoint_name == 'CITY_RIFLE_ACTION_DRAFT_INVENTORY_20261002.json'\n    sys.path.insert(0, str(Path(__file__).parent))\n    from ue_player_aim_runtime_preview import trial_records, stage" + s[end:]
        s = s.replace('(aim_preview or fp_preview)', 'aim_preview').replace('if aim_preview or fp_preview:', 'if aim_preview:')
        s = once(s, '\nnear_blocker = None\n', '\n')
        s = once(s, 'origin_location, index, near_blocker', 'origin_location, index')
        s = once(s, "                    if fp_preview and a == player: expected_weapon = 'BP_PC_FirstPersonRifleV1_C'\n", '')
        start = s.index('                    if fp_preview and a == player:\n')
        end = s.index("                    assert abs(prop(w, 'LeftShiftCm')", start)
        s = s[:start] + '                    assert grip == mesh\n' + s[end:]
        start = s.index('                if fp_preview:\n')
        end = s.index("                report['final_state'] = state(player)", start)
        s = s[:start] + s[end:]
        start = s.index('                if fp_preview:\n')
        end = s.index("            elif phase == 'capture_wait':", start)
        s = s[:start] + "                advance('capture_wait')\n" + s[end:]
        assert 'fp_preview' not in s and 'FirstPersonViewV1' not in s and 'near_blocker' not in s
        ast.parse(s)
    elif path.endswith('.cpp'):
        s = once(s, '#include "AnimGraphNode_CopyPoseFromMesh.h"\n', '')
        start = s.index('FString UParisBlueprintAuthoring::BuildFirstPersonCopyPose(')
        end = s.index('#include "ParisReloadDraft.inl"', start)
        s = s[:start] + s[end:]
    else:
        s = once(s, '    /** New owner-view copy only. Standard node; never changes a source pose or saves. */\n    UFUNCTION(BlueprintCallable, Category="Paris|Editor")\n    static FString BuildFirstPersonCopyPose(UAnimBlueprint* Blueprint);\n\n', '')
    assert s != original
    after = s.encode()
    patches.extend(difflib.unified_diff(original.splitlines(True), s.splitlines(True), fromfile='before/'+path, tofile='after/'+path))
    active.write_bytes(after)
    records.append({'path':path,'before_sha256':hashlib.sha256(before).hexdigest(),'after_sha256':hashlib.sha256(after).hexdigest()})
(CASE/'Changes/withdraw_fp001.patch').write_text(''.join(patches), encoding='utf-8')
(CASE/'Changes/withdrawal.json').write_text(json.dumps({'scope':'Only FP001-specific helper and optional test branches removed; unrelated edits retained','files':records},indent=2)+'\n')
print(json.dumps({'withdrawn_shared_files':len(records)}))
