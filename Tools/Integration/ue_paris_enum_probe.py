"""Read-only installed enum spelling probe; no package writes."""
import json
from pathlib import Path
import unreal

root = Path(__file__).resolve().parents[2]
out = root / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/CityGameplay20261002/Setup/enum_api_v2.json'
assert not out.exists()
out.write_text(json.dumps({name: {'names': dir(getattr(unreal, name)), 'doc': getattr(unreal, name).__doc__}
    for name in dir(unreal) if name.startswith('CollisionResponse')}, indent=2))
