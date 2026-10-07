"""Auditable current-V12 template reuse: distal-only existing pose, no fit scan.

The AST changes only the one-shot output identity, eligible index chain and
donor rotation application. The template, failed receipts and inputs stay exact.
All actual German geometry/contact/protection checks remain in the template.
"""
import ast,json
from pathlib import Path
TEMPLATE=Path(__file__).with_name('fit_patch.py')
tree=ast.parse(TEMPLATE.read_text(encoding='utf-8'))
changed={'output':0,'index':0,'rotation':0,'script_input':0}
for node in ast.walk(tree):
    if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
        name=node.targets[0].id
        if name=='OUT':
            node.value=ast.parse("BASE/'distal_existing_grasp_v4'",mode='eval').body;changed['output']+=1
        if name=='index':
            node.value=ast.parse("('index_03_r',)",mode='eval').body;changed['index']+=1
    if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Subscript):
        target=node.targets[0]
        if isinstance(target.value,ast.Name) and target.value.id=='local':
            node.value=ast.parse("mat({'t':[0,0,0], 'q':tm.slerp(encode(original)['q'],encode(donor)['q'],0.5), 's':np.linalg.norm(original[:3,:3],axis=0).tolist()})[:3,:3]",mode='eval').body
            changed['rotation']+=1
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='paths' for t in node.targets):
        node.value.elts.append(ast.parse('TEMPLATE',mode='eval').body);changed['script_input']+=1
assert changed=={'output':1,'index':1,'rotation':1,'script_input':1},changed
ast.fix_missing_locations(tree)
exec(compile(tree,str(TEMPLATE)+' [distal-only adapter]','exec'),globals())
