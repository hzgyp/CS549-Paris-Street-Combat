"""One read-only rendering process: fresh setup/input check, then actual-city views."""
import os
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
os.environ['CS549_CITY_REOPEN_IDENTITY'] = 'reopen_v3'
os.environ['CS549_CITY_CAPTURE_IDENTITY'] = 'views_v2'
os.environ['CS549_CITY_CAPTURE_MAP'] = '/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1'
runpy.run_path(str(ROOT / 'Tools/Integration/ue_paris_city_reopen.py'), run_name='__main__')
runpy.run_path(str(ROOT / 'Tools/Integration/ue_paris_city_capture.py'), run_name='__main__')
