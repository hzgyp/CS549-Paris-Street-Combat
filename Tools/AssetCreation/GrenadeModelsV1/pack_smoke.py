import bpy
from pathlib import Path
root=Path(__file__).resolve().parents[3];base=root/'Assets/LocalWorking/Experiments/GrenadeModels/20261011/smoke/finish_v1'
out=base/'ANM8SmokePacked.blend';assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(base/'ANM8Smoke.blend'));bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out))
