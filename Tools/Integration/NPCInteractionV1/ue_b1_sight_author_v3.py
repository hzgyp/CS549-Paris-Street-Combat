"""Run corrected author into new V3 packages while preserving occupied V2 evidence."""
import os
import runpy
from pathlib import Path

os.environ["CS549_NPC_SIGHT_VERSION"] = "V3"
os.environ["CS549_NPC_SIGHT_AUTHOR_RESULT"] = "b1_sight_author_v3.json"
runpy.run_path(str(Path(__file__).with_name("ue_b1_sight_author_v2.py")), run_name="__main__")
