from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent));from battlefield_common import *
source=(Path(__file__).parent/'build_battlefield_combat.py').read_text()
exec('# Add one guarded dispatch'+source.split('# Add one guarded dispatch',1)[1],globals())
