"""Resume only the existing unsaved human-review setup in the same open editor."""
import datetime,os,runpy
from pathlib import Path
os.environ['CS549_RELOAD_HUMAN_ID']='human_v5_resume_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
os.environ['CS549_RELOAD_HUMAN_RESUME']='1'
try:
    runpy.run_path(str(Path(__file__).with_name('ue_human_preview.py')),run_name='__main__')
finally:
    os.environ.pop('CS549_RELOAD_HUMAN_RESUME',None)
