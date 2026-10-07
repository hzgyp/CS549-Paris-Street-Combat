"""Fresh listener-free native proof with corrected non-overlapping test scene."""
import os
import runpy
from pathlib import Path

os.environ["CS549_NPC_SIGHT_VERSION"] = "V4"
os.environ["CS549_NPC_SIGHT_CLEAR_SCENE"] = "1"
os.environ["CS549_NPC_SIGHT_AUTHOR_RESULT"] = "b1_sight_author_v4.json"
os.environ["CS549_NPC_SIGHT_RUNTIME_RESULT"] = "sight_verified.json"
runpy.run_path(str(Path(__file__).with_name("ue_b1_sight_test_v2.py")), run_name="__main__")
