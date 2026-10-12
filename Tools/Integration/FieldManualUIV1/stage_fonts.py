"""Stage only new independently licensed font bytes; never edit hard-linked assets."""
from pathlib import Path
import sys,argparse,shutil
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/TacticalEquipmentV1'))
from prepare import OUT,read,write,sha
ap=argparse.ArgumentParser();ap.add_argument('revision');a=ap.parse_args()
stage=Path(read(OUT/a.revision/'runtime.json')['path'])/'Windows/WW2FranceLiberation/UI'
engine=Path('C:/Program Files/Epic Games/UE_5.8/Engine')
entries=[]
for name in ['Roboto-Regular.ttf','Roboto-BoldCondensed.ttf']:
    src=engine/'Content/Slate/Fonts'/name;dst=stage/name;assert not dst.exists();shutil.copyfile(src,dst)
    entries.append(dict(path=name,sha256=sha(dst),size_bytes=dst.stat().st_size,source=str(src)))
license=engine/'Source/ThirdParty/Licenses/ROBOTO_License.txt'
shutil.copyfile(license,stage/'Roboto-Apache2.txt')
write(stage/'Roboto-provenance.json',dict(license='Apache-2.0',copyright='Font data copyright Google 2012',license_source=str(license),license_sha256=sha(stage/'Roboto-Apache2.txt'),source='Installed pinned UE 5.8 Engine font distribution',files=entries))
print('Staged Roboto fonts and original Apache license')
