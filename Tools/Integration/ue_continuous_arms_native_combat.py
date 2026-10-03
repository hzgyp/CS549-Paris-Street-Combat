"""Dispatch existing combat assertions with native display and observer-only Python."""
import os
from pathlib import Path
os.environ['CS549_COMBAT_PIE_IDENTITY']=os.environ['CS549_ARMS_NATIVE_IDENTITY']
os.environ['CS549_CITY_NATIVE_CHECKPOINT']=os.environ.get('CS549_ARMS_NATIVE_CHECKPOINT','CITY_RIFLE_ACTION_DRAFT_INVENTORY_20261002.json')
os.environ['CS549_CONTINUOUS_ARMS_NATIVE_TEST']='1'
os.environ['CS549_CONTINUOUS_ARMS_MUZZLE_PREVIEW']='0'
os.environ['CS549_PLAYER_AIM_PREVIEW']='0'
os.environ['CS549_FIRST_PERSON_VIEW_PREVIEW']='0'
p=Path(__file__).with_name('ue_paris_combat_pie.py')
exec(compile(p.read_text(),str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})
