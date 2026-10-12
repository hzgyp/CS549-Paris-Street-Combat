from pathlib import Path
import sys,shutil
source=Path(sys.argv[1]);dest=Path(sys.argv[2]);dest.mkdir(exist_ok=False)
for folder in ['Config','Source','Plugins']:
    shutil.copytree(source/folder,dest/folder,ignore=shutil.ignore_patterns('Binaries','Intermediate','Saved','__pycache__'))
shutil.copyfile(source/'WW2FranceLiberation.uproject',dest/'WW2FranceLiberation.uproject')
