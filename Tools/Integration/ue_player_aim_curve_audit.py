"""Read the existing aim asset's actual sample coordinates and Python editing APIs."""
import json,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/CityGameplay20261002/RifleCrosshairV4/curve_audit_v1.json'
assert not OUT.exists()
r={'errors':[],'properties':{},'api':{}}
a=unreal.load_asset('/Game/RifleAnimsetPro/BlendSpaces/RifleStandAim')
for n in ('blend_parameters','sample_data','interpolation_param'):
    try:r['properties'][n]=str(a.get_editor_property(n))
    except Exception:r['properties'][n]=traceback.format_exc()
r['api']={n:str(getattr(a,n).__doc__) for n in dir(a) if 'sample' in n or 'parameter' in n or 'skeleton' in n}
OUT.write_text(json.dumps(r,indent=2));unreal.SystemLibrary.quit_editor()
