"""Author new V4 packages with public cross-Blueprint sight recording."""
import os
import runpy
from pathlib import Path

os.environ["CS549_NPC_SIGHT_VERSION"] = "V4"
os.environ["CS549_NPC_SIGHT_AUTHOR_RESULT"] = "b1_sight_author_v4.json"
runpy.run_path(str(Path(__file__).with_name("ue_b1_sight_author_v2.py")), run_name="__main__")
