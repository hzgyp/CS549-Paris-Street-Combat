"""Run the unchanged sight gate against the corrected new V3 packages."""
import os
import runpy
from pathlib import Path

os.environ["CS549_NPC_SIGHT_VERSION"] = "V3"
os.environ["CS549_NPC_SIGHT_AUTHOR_RESULT"] = "b1_sight_author_v3.json"
os.environ["CS549_NPC_SIGHT_RUNTIME_RESULT"] = "b1_sight_runtime_v3.json"
runpy.run_path(str(Path(__file__).with_name("ue_b1_sight_test_v2.py")), run_name="__main__")
