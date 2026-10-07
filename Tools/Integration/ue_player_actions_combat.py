"""Run retained combat assertions against new action classes and separated owner pose."""
import os
from pathlib import Path
os.environ['CS549_COMBAT_PIE_IDENTITY']=os.environ['CS549_ACTION_IDENTITY']
os.environ['CS549_CITY_NATIVE_CHECKPOINT']='CITY_CONTINUOUS_ARMS_NATIVE_INVENTORY_20261003.json'
os.environ['CS549_CONTINUOUS_ARMS_NATIVE_TEST']='1'
os.environ['CS549_ACTIONS_NATIVE_TEST']='1'
for n in ('CS549_CONTINUOUS_ARMS_MUZZLE_PREVIEW','CS549_PLAYER_AIM_PREVIEW','CS549_FIRST_PERSON_VIEW_PREVIEW'):os.environ[n]='0'
p=Path(__file__).with_name('ue_paris_combat_pie.py')
exec(compile(p.read_text(),str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})
