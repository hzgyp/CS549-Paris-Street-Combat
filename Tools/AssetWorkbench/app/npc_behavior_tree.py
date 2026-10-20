"""Bounded reactive behavior trees; these definitions drive execution and the UI."""
from copy import deepcopy


def _definition(faction):
    nodes = []

    def node(nid, kind, zh, en, children=(), op=None, description=None):
        bindings = {'formation': ['follow_distance'], 'visible': ['german_sight_range', 'german_sight_fov_degrees'],
                    'grace': ['loss_grace'], 'enemy_policy': ['search_duration'],
                    'tactical_plan': ['allied_mode', 'follow_distance', 'scout_distance'],
                    'fire_ready': ['combat_damage'], 'fire': ['combat_damage'],
                    'bound_plan': ['tactical_coordination'], 'squad_maneuver': ['tactical_coordination']}
        nodes.append({'id': nid, 'kind': kind, 'label': [zh, en], 'children': list(children),
                      'op': op, 'parameters': bindings.get(op, []), 'description': description or [zh, en]})
        return nid

    def move(prefix, zh, en):
        leaf = node(prefix+'.move', 'Action', zh, en, op='move', description=[
            '请求真实路径。移动中返回运行；实际到达才成功；失败和预算耗尽保留在子节点。',
            'Request a real path. Running while moving; success only on actual arrival. Failures remain visible.'])
        return node(prefix+'.intent', 'ForceSuccess', '保留当前意图', 'Keep selected intent', [leaf], description=[
            '路径失败时保留意图，等待已有的有限重试；不会改选另一角色，也不表示到达。',
            'Keep the selected intent on path failure for bounded retries; this does not mean arrival.'])

    fire = node('attack', 'Selector', '自主交火 · 独立于移动', 'Autonomous fire · independent of movement', [
        node('attack.valid', 'Sequence', '射击条件全部通过', 'All fire gates pass', [
            node('attack.check', 'Condition', '自己的视线、射界、弹药与冷却？', 'Own sight, clear lane, ammo and cooldown?', op='fire_ready'),
            node('attack.fire', 'Action', '执行二维射击与伤害', 'Apply 2D shot and damage', op='fire')]),
        node('attack.hold', 'Action', '禁止射击 · 记录原因', 'Withhold fire · record reason', op='fire_hold')])

    if faction == 'allied':
        budget = node('budget', 'Sequence', '预算耗尽时等待', 'Wait when budget is exhausted', [
            node('budget.check', 'Condition', '移动预算已耗尽？', 'Movement budget exhausted?', op='budget'),
            node('budget.wait', 'Action', '等待新指令', 'Wait for new order', op='wait_budget')])
        role = node('role', 'Sequence', '分工支援与掩护', 'Assigned support / overwatch', [
            node('role.check', 'Condition', '有有效的共同分工？', 'Valid joint assignment?', op='assigned'),
            node('role.reserve', 'Action', '占用分工位置', 'Reserve assigned position', op='reserve_role'),
            move('role', '移动到支援位置', 'Move to support position')])

        def formation(prefix, regroup):
            reserve = node(prefix+'.reserve', 'Action', '占用独立队形位置', 'Reserve separated slot', op='reserve_formation')
            navigation = node(prefix+'.navigation', 'Selector', '到达队形或明确等待', 'Move to formation or wait', [
                node(prefix+'.path', 'Sequence', '有可用队形路径', 'Usable formation path', [
                    node(prefix+'.goal', 'Condition', '队形目标可到达？', 'Reachable formation goal?', op='goal'),
                    reserve, move(prefix, '移动到队形位置', 'Move to formation slot')]),
                node(prefix+'.wait', 'Action', '无路径时等待', 'Wait without a path', op='wait_no_path')])
            children = ([node(prefix+'.contact', 'Condition', '有近期敌情？', 'Recent hostile contact?', op='contact')] if regroup else [])
            children += [node(prefix+'.compute', 'Action', '寻找独立队形目标', 'Find separated formation goal', op='formation'), navigation]
            return node(prefix, 'Sequence', '带敌情归队' if regroup else '跟随玩家', 'Regroup with contact' if regroup else 'Follow player', children)

        # Keep legacy node ids where their meanings still apply. Each plan is
        # independent: the other ally's absence cannot disable this brain.
        def plan_branch(nid, zh, en, op):
            return node(nid, 'Sequence', zh, en, [
                node(nid+'.check', 'Condition', zh+'？', en+'?', op=op),
                node(nid+'.reserve', 'Action', '接纳独立战术位置', 'Admit independent tactical goal', op='tactical_plan')])
        # Remove the old joint-assignment and rear-only branches from definition.
        nodes = [n for n in nodes if not (n['id']=='role' or n['id'].startswith('role.') or n['id'].startswith('follow') or n['id'].startswith('regroup'))]
        plan = node('plan', 'Selector', '接敌优先 · 前出或环绕', 'Contact first · scout or cover', [
            node('bound', 'Sequence', '真实掩体 · 交替掩护推进', 'Obstacle cover · alternating bounds', [
                node('bound.check', 'Condition', '有完整的双人掩体方案？', 'Complete two-member cover plan?', op='bound_plan'),
                node('bound.geometry', 'Condition', '藏身遮挡、探出射界和连接路径通过？', 'Blocked hide, clear peek and connector?', op='cover_geometry'),
                node('bound.role', 'Selector', '按实际到位分配推进与掩护', 'Assign advance / cover by physical readiness', [
                    node('bound.cover', 'Sequence', '掩护者先进入掩体并探出观察', 'Holder takes cover and peeks to watch', [
                        node('bound.holder', 'Condition', '本成员负责掩护？', 'This member is the holder?', op='bound_holder'),
                        node('bound.hold', 'Action', '执行藏身 / 探出观察位置', 'Execute hide / peek watch goal', op='tactical_plan')]),
                    node('bound.advance', 'Sequence', '掩护已就绪才推进', 'Advance only when cover is ready', [
                        node('bound.ready', 'Condition', '队友实际到位且射界与弹药可用？', 'Partner physically ready with lane and ammo?', op='bound_ready'),
                        node('bound.move', 'Action', '推进到下一处真实掩体', 'Advance to next admitted obstacle cover', op='tactical_plan')]),
                    node('bound.wait', 'Action', '等待掩护就绪 · 停止旧推进路径', 'Wait for holder · stop old advance path', op='tactical_plan')])]),
            plan_branch('role', '敌情有效且未超出玩家边界', 'Contact valid and within player leash', 'tactical_contact'),
            plan_branch('scout', '前出探路角色', 'Forward scout role', 'scouting'),
            plan_branch('cover', '环绕侧翼掩护角色', 'Cover wing role', 'covering'),
            node('follow.compute', 'Action', '独立跟随 / 归队位置', 'Independent follow / regroup slot', op='tactical_plan')])
        nav = node('navigation', 'Selector', '战术移动与明确等待', 'Tactical movement or explicit wait', [
            budget,
            node('travel', 'Sequence', '完整战术路径', 'Complete tactical path', [
                node('travel.goal', 'Condition', '有接纳的战术目标？', 'Admitted tactical goal?', op='goal'),
                move('travel', '移动到前出 / 掩护 / 接敌位置', 'Move to scout / cover / contact goal')]),
            node('follow.wait', 'Action', '无可用路径时等待', 'Wait without an admitted path', op='wait_no_path')])
        root = node('live', 'Sequence', '盟军 · 战术决策、交火、导航', 'Allied tactics, fire and navigation', [plan, fire, nav], description=[
            '每人独立接敌；无敌情时按玩家朝向前出、环绕或跟随。射击不等待到达；仍需自己的实时视线和安全射界。',
            'Independent contact response; otherwise scout, cover or follow the friendly heading. Fire need not wait for arrival, but needs own sight and a safe lane.'])
    else:
        def branch(nid, zh, en, condition, action):
            return node(nid, 'Sequence', zh, en, [
                node(nid+'.check', 'Condition', zh+'？', en+'?', op=condition),
                node(nid+'.update', 'Action', action[0], action[1], op='enemy_policy')])

        sight = node('sight', 'Sequence', '当前看见敌方', 'Hostile currently visible', [
            node('sight.check', 'Condition', '有实时视线与观察？', 'Live sight and observation?', op='visible'),
            node('sight.response', 'Selector', '警戒后进入交战意图', 'Alert before engage intent', [
                branch('alert', '需要警戒停留', 'Alert dwell needed', 'alert', ['保持警戒', 'Hold alert']),
                node('engage', 'Action', '允许当前交战意图', 'Allow current engage intent', op='enemy_policy')])])
        policy = node('policy', 'Selector', '感知与记忆决策', 'Perception / memory decisions', [
            branch('coordination', '目击者压制与两翼包抄', 'Observer watch and opposite flanks', 'squad_maneuver', ['执行目击者 / 左翼 / 右翼分工', 'Execute observer / left / right flank role']),
            branch('hearing', '听觉警戒未结束', 'Hearing alert still dwelling', 'hearing', ['保持听觉警戒', 'Hold hearing alert']),
            sight,
            branch('squad', '收到同小队遇袭 / 阵亡通报', 'Same-squad hit / casualty report', 'squad_report', ['按通报分区调查与搜索', 'Investigate and search a reported sector']),
            branch('grace', '刚丢失视线', 'Within sight-loss grace', 'grace', ['等待确认，禁止开火', 'Hold without firing']),
            branch('memory', '有未消费的观察', 'Unconsumed observation', 'memory', ['调查 / 有限搜索 / 到期返回', 'Investigate / bounded search / return']),
            node('return', 'Action', '返回锚点或守卫', 'Return to anchor or guard', op='enemy_policy')])
        search = node('search', 'Sequence', '搜索点净空适配', 'Adapt search point to clearance', [
            node('search.check', 'Condition', '正在搜索地图偏移点？', 'Raster search offset requested?', op='search'),
            node('search.project', 'Action', '有限搜索候选点', 'Bounded search candidates', op='project_search', description=[
                '只在固定最后观察点偏移附近检查有限候选；不读取隐藏玩家位置，不延长搜索期限。',
                'Check finite candidates around the frozen last-seen offset; no hidden player position or deadline extension.']),
            node('search.navigation', 'Selector', '移动或跳过不可达点', 'Move or skip unreachable point', [
                node('search.path', 'Sequence', '搜索路径', 'Search path', [
                    node('search.goal', 'Condition', '候选搜索点可用？', 'Search candidate available?', op='goal'),
                    move('search', '移动到搜索点', 'Move to search point')]),
                node('search.skip', 'Action', '跳过并停止旧路径', 'Skip and cancel old path', op='cancel')])])
        navigation = node('navigation', 'Selector', '真实路径与移动', 'Actual path / movement', [
            node('guard', 'Sequence', '守卫锚点', 'Guard anchor', [
                node('guard.check', 'Condition', '已回到守卫状态？', 'Guard state?', op='guard'),
                node('guard.restore', 'Action', '恢复朝向并驻守', 'Restore heading and hold', op='guard_hold')]),
            search,
            node('travel', 'Sequence', '调查或返回路径', 'Investigation / return path', [
                node('travel.goal', 'Condition', '有移动目标？', 'Movement goal present?', op='goal'),
                move('travel', '移动到观察点或锚点', 'Move to observation or anchor')]),
            node('hold', 'Action', '站定并停止旧路径', 'Hold and cancel old path', op='cancel')])
        root = node('live', 'Sequence', '德军决策、交火与导航', 'German decisions, fire and navigation', [policy, fire, navigation], description=[
            '先根据真实感知与个人记忆选择意图，再执行对应导航。序列从上到下执行，失败或运行时停止。',
            'Select intent using actual senses and private memory, then execute navigation. A sequence stops on failure or running.'])
    root = node('root', 'Selector', '存活与小队战术', 'Lifecycle and squad tactics', [
        node('dead', 'Sequence', '阵亡成员停止行动', 'Casualty stops acting', [
            node('dead.check', 'Condition', '生命值已归零？', 'Health depleted?', op='dead'),
            node('dead.hold', 'Action', '停止移动与射击', 'Stop movement and firing', op='dead_hold')]), root])
    return {'schema': 'paris.npc.behavior-tree.v1', 'id': faction, 'root': root, 'nodes': nodes,
            'reactive': True, 'decision_interval': .5, 'max_node_visits': len(nodes)}


DEFINITIONS = {f: _definition(f) for f in ('allied', 'german')}


def definitions():
    return deepcopy(DEFINITIONS)


def tick_tree(faction, at, condition, action):
    """Evaluate once per node, no loops or hidden policy fallback; retain skipped nodes."""
    tree = DEFINITIONS[faction]
    nodes = {n['id']: n for n in tree['nodes']}
    trace = {'definition': faction, 'at': at, 'visited': [],
             'nodes': {nid: {'status': 'Skipped', 'detail': {}} for nid in nodes}}

    def visit(nid):
        if nid in trace['visited'] or len(trace['visited']) >= tree['max_node_visits']:
            raise RuntimeError('Behavior tree exceeded its finite node budget')
        trace['visited'].append(nid)
        n = nodes[nid]
        kind, detail = n['kind'], {}
        if kind == 'Condition':
            passed, detail = condition(n['op'])
            status = 'Success' if passed else 'Failure'
        elif kind == 'Action':
            status, detail = action(n['op'])
        elif kind == 'ForceSuccess':
            child = visit(n['children'][0])
            status = 'Running' if child == 'Running' else 'Success'
            detail = {'child_status': child, 'arrival_claim': False}
        else:
            status = 'Failure' if kind == 'Selector' else 'Success'
            for child in n['children']:
                status = visit(child)
                if (kind == 'Selector' and status != 'Failure') or (kind == 'Sequence' and status != 'Success'):
                    detail = {'selected_child' if kind == 'Selector' else 'stopped_child': child}
                    break
        if status not in ('Success', 'Failure', 'Running'):
            raise RuntimeError('Invalid behavior tree result')
        trace['nodes'][nid] = {'status': status, 'detail': detail}
        return status

    trace['status'] = visit(tree['root'])
    return trace
