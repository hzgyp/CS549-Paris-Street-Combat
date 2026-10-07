"""Functional blade tangency and closest marked-stock seating; right skin fixed."""
from pathlib import Path
entry=Path(__file__).with_name('blender_trigger_surface_v10b.py')
source=entry.read_text(encoding='utf-8')
changes={
    "OUT=BASE/'trigger_surface_v10b'":"OUT=BASE/'trigger_tangent_v10c'",
    "paths=(PREVIOUS,MEASURE,GEOMETRY,TOPO,HELPER,Path(__file__))":
    "paths=(PREVIOUS,MEASURE,GEOMETRY,TOPO,HELPER,Path(__file__),entry)",
    "from mathutils import Vector,Matrix":"from mathutils import Vector,Matrix,Quaternion",
    "rot=swing(old,target);angle=math.degrees(math.acos(np.clip((np.trace(rot)-1)/2,-1,1)))\n        seat=target-rot@old":
    """normal_world=g[:3,:3]@normals[j]
        normal_world/=np.linalg.norm(normal_world)
        desired=-pn
        initial=swing(normal_world,desired)
        # With blade normals paired, solve one remaining twist analytically to
        # retain the marked neck as closely as possible. No angle grid.
        a=initial@(-old);b=-target
        a-=desired*np.dot(a,desired);b-=desired*np.dot(b,desired)
        assert np.linalg.norm(a)>1e-6 and np.linalg.norm(b)>1e-6
        twist=math.atan2(np.dot(desired,np.cross(a,b)),np.dot(a,b))
        spin=np.array(Quaternion(Vector(desired),twist).to_matrix(),float)
        rot=spin@initial
        angle=math.degrees(math.acos(np.clip((np.trace(rot)-1)/2,-1,1)))
        seat=target-rot@old""",
    "'normal_local':normals[j].tolist(),'angle_deg':angle":
    "'normal_local':normals[j].tolist(),'normal_opposition_error':float(np.linalg.norm(rot@normal_world+pn)),'angle_deg':angle",
    "trigger_surface_v10b_local_geometry_pass":"trigger_tangent_v10c_local_geometry_pass",
    "trigger_surface_v10b_residual_retained":"trigger_tangent_v10c_residual_retained",
}
for old,new in changes.items():
    assert source.count(old)==1,old
    source=source.replace(old,new)
exec(compile(source,str(entry)+':tangent_v10c','exec'),globals())
