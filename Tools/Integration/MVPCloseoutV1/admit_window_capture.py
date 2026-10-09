"""Early external-video image admission; blank/incorrect frames are failures."""
import sys
from pathlib import Path
from PIL import Image,ImageStat
path=Path(sys.argv[1]);im=Image.open(path).convert('RGB')
assert im.size==(1920,1080),im.size
assert max(b-a for a,b in im.getextrema())>32 and sum(ImageStat.Stat(im).mean)>15,'Blank captured window'
print('Actual 1920x1080 nonblank window frame admitted; visual HUD review still required')
