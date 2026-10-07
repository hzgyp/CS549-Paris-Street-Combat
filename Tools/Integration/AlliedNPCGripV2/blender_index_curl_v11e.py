"""Retain original requested0.4cm/7degree comparison; NOT contact acceptance."""
from pathlib import Path
entry=Path(__file__).with_name('blender_index_curl_v11d.py')
source=entry.read_text(encoding='utf-8')
changes={
    "OUT=BASE/'index_curl_v11d'":"OUT=BASE/'index_curl_v11e'",
    'TOPO,HELPER,Path(__file__))':'TOPO,HELPER,Path(__file__),entry)',
    "    assert choices,'No small rearward axial clearance interval'\n    distance=min(choices,key=lambda x:abs(x-.4))":"    # Original requested comparison, not a new seating solve or accepted fit.\n    distance=.4",
    "    assert gate,'Analytic axial placement retained but exact local contact failed'\n    r['status']='index_curl_v11d_local_geometry_pass'":"    r['comparison_only']=True\n    r['status']='index_curl_v11e_deformation_pass_contact_failed_comparison'",
}
for old,new in changes.items():
    assert source.count(old)==1,old
    source=source.replace(old,new)
exec(compile(source,str(entry)+':v11e_comparison','exec'),globals())
