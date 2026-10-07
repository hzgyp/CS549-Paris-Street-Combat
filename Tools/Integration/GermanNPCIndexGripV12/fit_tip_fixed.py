"""Distal-only same comparison; correct quaternion API before any fit."""
import ast
from pathlib import Path
from mathutils import Quaternion
def q_slerp(a,b,alpha):
    qa=Quaternion((a[3],*a[:3]));qb=Quaternion((b[3],*b[:3]));qa.normalize();qb.normalize()
    q=qa.slerp(qb,alpha);return [q.x,q.y,q.z,q.w]
TEMPLATE=Path(__file__).with_name('fit_patch.py')
ADAPTER=Path(__file__).with_name('fit_tip.py')
tree=ast.parse(TEMPLATE.read_text(encoding='utf-8'))
changed={'output':0,'index':0,'rotation':0,'script_input':0}
for node in ast.walk(tree):
    if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
        name=node.targets[0].id
        if name=='OUT':node.value=ast.parse("BASE/'distal_existing_grasp_v4b'",mode='eval').body;changed['output']+=1
        if name=='index':node.value=ast.parse("('index_03_r',)",mode='eval').body;changed['index']+=1
    if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Subscript):
        if isinstance(node.targets[0].value,ast.Name) and node.targets[0].value.id=='local':
            node.value=ast.parse("mat({'t':[0,0,0], 'q':q_slerp(encode(original)['q'],encode(donor)['q'],0.5), 's':np.linalg.norm(original[:3,:3],axis=0).tolist()})[:3,:3]",mode='eval').body;changed['rotation']+=1
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='paths' for t in node.targets):
        node.value.elts.extend(ast.parse('(TEMPLATE,ADAPTER)',mode='eval').body.elts);changed['script_input']+=1
assert changed=={'output':1,'index':1,'rotation':1,'script_input':1},changed
ast.fix_missing_locations(tree)
exec(compile(tree,str(TEMPLATE)+' [corrected distal-only adapter]','exec'),globals())
