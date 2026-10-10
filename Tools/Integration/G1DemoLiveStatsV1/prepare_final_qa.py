from pathlib import Path
HERE=Path(__file__).parent;ROOT=HERE.parents[2]
assert not (HERE/'verify_final_media.py').exists(), 'Keep the completed04 checker and its bounded frame-count correction'
s=(ROOT/'Tools/Integration/G1DemoInputV1/verify_final_media.py').read_text('utf-8')
s=s.replace('tmp/g1-demo-draft03-20261009','tmp/g1-demo-draft04-20261010').replace('DemoDraft03_20261009','DemoDraft04_20261010').replace('Paris_G1_MVP_Draft_03.mp4','Paris_G1_MVP_Draft_04_Live_Performance.mp4')
s=s.replace('actions_probe_v3','actions_panel_v1').replace('victory_v6','victory_panel_v1').replace('defeat_v5','defeat_panel_v1').replace("('pending',timeline['duration']-3)","('ending',timeline['duration']-3)")
s=s.replace('manual play, FPS, stress, teammate or course acceptance.','manual play, formal benchmark/capacity or course acceptance. Native live counters reflect only this instrumented capture.')
(HERE/'verify_final_media.py').write_text(s,'utf-8')
print('New04 QA tool saved; old03 QA unchanged')
