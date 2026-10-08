"""Copy installed Epic template bytes into a private, verified test dependency."""
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path("C:/Program Files/Epic Games/UE_5.8/Templates/TemplateResources/High/Characters/Content")
DEST = ROOT / "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/PureMapSurveyV1/template_defaults_v1_20261007"


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    assert not DEST.exists(), "Preserve original template copy"
    assert not (ROOT / "Unreal/ParisStreetCombat/Content/Characters").exists(), "Do not replace a mount"
    files = []
    for path in sorted(SOURCE.rglob("*")):
        if not path.is_file(): continue
        target = DEST / "Content/Characters" / path.relative_to(SOURCE)
        target.parent.mkdir(parents=True, exist_ok=True)
        before = digest(path)
        shutil.copy2(path, target)
        assert before == digest(target) == digest(path)
        files.append({"relative": path.relative_to(SOURCE).as_posix(), "bytes": target.stat().st_size, "sha256": before})
    (DEST / "manifest.json").write_text(json.dumps({"source": str(SOURCE), "scope": "Private Epic default mannequin test dependency only",
        "files": files, "total_bytes": sum(r["bytes"] for r in files)}, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"files": len(files), "bytes": sum(r["bytes"] for r in files), "mount_target": str(DEST / "Content/Characters")}))
