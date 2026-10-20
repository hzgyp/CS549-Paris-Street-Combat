"""Finite obstacle-cover and squad maneuver plans built only from observations.

Queries use the existing capsule/path/ray adapter. A role never grants fire
permission, and a requested destination never counts as physical arrival.
"""
from copy import deepcopy
import math
from .npc_oracle import Observation, distance


class ManeuverWorld:
    def _init_maneuvers(self):
        self.maneuvers = {}
        self.bound = None
        self.german_contact = None
        self.flank_legs = {}
        self.cover_queries = 0

    def _coordination(self):
        return bool(self.parameters['tactical_coordination'])

    def _arrival_tolerance(self, aid):
        # A corner peek needs a tighter physical stop than an ordinary MoveTo:
        # the general .45 m radius can still leave the actual ray behind a wall.
        plan = self.maneuvers.get(aid, {})
        if plan.get('active') and plan.get('holder') == aid and plan.get('cover', {}).get('arrived_hide'):
            return .08
        return self.cfg['arrival_radius']

    def _cover_pair(self, aid, desired, threat, avoid=(), anchor=None):
        """At most49 hide probes/32 peek probes; at most6 actual path queries.

        Both hide and peek are real capsule centres. The blocker and clear peek
        ray are recorded separately from the complete physical connector.
        """
        self.cover_queries += 1
        actor = self.actors[aid]
        offsets = sorted(((x, y) for x in range(-3, 4) for y in range(-3, 4)),
                         key=lambda p: (p[0]*p[0]+p[1]*p[1], p))
        rows, geometrical = [], []
        for index, (x, y) in enumerate(offsets):
            hide = (desired[0]+x, desired[1]+y)
            row = {'id': aid+'.W'+str(index+1), 'position': hide, 'role': 'ObstacleCover',
                   'valid': False, 'score': -100., 'features': {}, 'contributions': {}, 'gates': []}
            rows.append(row)
            if not self.geo.free(hide):
                row['gates'].append('BlockedClearance');continue
            if anchor is not None and distance(hide, anchor) > self.cfg['ally_player_envelope']:
                row['gates'].append('PlayerLeash');continue
            if any(distance(hide, p) < self.cfg['reservation_separation'] for p in avoid):
                row['gates'].append('ReservedByTeammate');continue
            if not self.geo.blocked(hide, threat):
                row['gates'].append('ExposedHideRay');continue
            peek = None
            for radius in (1., 1.8):
                for n in range(16):
                    angle = n*math.pi/8
                    point = (hide[0]+radius*math.cos(angle), hide[1]+radius*math.sin(angle))
                    if (self.geo.free(point) and not self.geo.blocked(hide, point, self.cfg['capsule_radius'])
                            and distance(point, threat) <= self._vision('allied')['sight_range']-.12
                            and not self.geo.blocked(point, threat)
                            and all(not self.geo.blocked((point[0]+.12*math.cos(k*math.pi/4),
                                                          point[1]+.12*math.sin(k*math.pi/4)), threat) for k in range(8))
                            and (anchor is None or distance(point, anchor) <= self.cfg['ally_player_envelope'])
                            and all(distance(point, p) >= self.cfg['reservation_separation'] for p in avoid)):
                        peek = point;break
                if peek is not None:break
            if peek is None:
                row['gates'].append('NoConnectedClearPeek');continue
            score = 10-distance(hide, desired)-distance(actor.position, hide)*.12
            row.update(score=round(score, 6), features={'cover': 1., 'lane': 1.}, peek=peek,
                       gates=['PathNotEvaluated'])
            geometrical.append(row)
        chosen = None
        for row in sorted(geometrical, key=lambda r: (-r['score'], r['id']))[:6]:
            route = self.geo.path(actor.position, row['position'])
            row['path_status'] = route['status']
            row['gates'] = [] if route['status'] == 'Complete' else [route['status']]
            if route['status'] != 'Complete':continue
            hide, peek = row['position'], row['peek']
            ray = self.geo.sight_evidence(hide, math.atan2(threat[1]-hide[1], threat[0]-hide[0]), threat,
                                           {'sight_range': 1000, 'sight_fov_degrees': 180})['ray']
            assert ray and ray['blocked']
            row['valid'] = True
            chosen = {'id': row['id'], 'hide': list(hide), 'peek': list(peek), 'threat': list(threat),
                      'blocker': deepcopy(ray), 'hide_blocked': True, 'peek_clear': True,
                      'connector_clear': True, 'path_status': 'Complete', 'path_length': route['length'],
                      'peek_ray_margin_probes_m': .12,
                      'query_at': self.at, 'candidate_limit': 49, 'peek_limit': 32, 'path_limit': 6,
                      'arrived_hide': False}
            break
        return chosen, rows

    def _bound_goal(self, aid, pair, hold=False):
        actor = self.actors[aid]
        if distance(actor.position, pair['hide']) <= self.cfg['arrival_radius']:
            pair['arrived_hide'] = True
        return tuple(pair['peek'] if hold and pair['arrived_hide'] else pair['hide'])

    def _plan_allies(self):
        selected = self._plan_basic_allies()
        for aid in ('A1', 'A2'):self.maneuvers.pop(aid, None)
        if not self._coordination() or self.parameters['allied_mode'] == 0:
            self.bound = None;return selected
        living = [a for a in ('A1', 'A2') if self.actors[a].alive]
        player = self.actors['P']
        known = [self.minds[a].knowledge for a in living if self.minds[a].knowledge]
        observation = max(known, key=lambda o: (o.at, o.actor_id)) if known else None
        threat = tuple(observation.position) if observation else (player.position[0]+10*math.cos(player.heading),
                                                                  player.position[1]+10*math.sin(player.heading))
        if len(living) != 2:
            self.bound = None
            for aid in living:
                self.maneuvers[aid] = {'active': False, 'role': 'Solo', 'reason': 'no living bound partner; independent tactical fallback', 'at': self.at}
            return selected
        generation = self.moves['P'].generation
        if (not self.bound or self.bound['generation'] != generation
                or self.bound['mode'] != self.parameters['allied_mode']
                or distance(player.position, self.bound['origin']) >= 3
                or bool(observation) != (self.bound['basis']=='observed_contact')):
            self.bound = {'generation': generation, 'mode': self.parameters['allied_mode'],
                          'mover': 'A1', 'holder': 'A2', 'phase': 1, 'legs': {}, 'started': False,
                          'origin': tuple(player.position), 'heading': player.heading,
                          'threat': threat, 'basis': 'observed_contact' if observation else 'authored_forward_watch',
                          'created': self.at, 'failed': False}
        b = self.bound
        mover, holder = b['mover'], b['holder']
        # Exchange only after an admitted mover really reaches its hide centre.
        moving_pair = b['legs'].get(mover)
        if (b['started'] and moving_pair and distance(self.actors[mover].position, moving_pair['hide']) <= self.cfg['arrival_radius']):
            moving_pair['arrived_hide'] = True
            b['last_swap'] = {'at': self.at, 'arrived_actor': mover, 'position': list(self.actors[mover].position),
                              'hide': deepcopy(moving_pair['hide']), 'error': distance(self.actors[mover].position,moving_pair['hide'])}
            b['mover'], b['holder'] = holder, mover
            b['phase'] += 1;b['started'] = False
            b['legs'].pop(holder, None)
            self.event(mover, 'BoundSwap', 'physical cover arrival; exchange mover and covering partner')
            mover, holder = b['mover'], b['holder']
        forward = (math.cos(b['heading']), math.sin(b['heading']))
        side = (-forward[1], forward[0])
        if not b['failed']:
            for aid in (holder, mover):
                if aid in b['legs']:continue
                sign = -1 if aid == 'A1' else 1
                front = (1 if aid == holder else self.parameters['scout_distance'])
                if b['phase'] > 1 and aid == mover:
                    cover = b['legs'][holder]['hide']
                    desired = (cover[0]+3*forward[0]+sign*1.5*side[0], cover[1]+3*forward[1]+sign*1.5*side[1])
                else:
                    desired = (player.position[0]+front*forward[0]+sign*self.cfg['follow_distance']*side[0],
                               player.position[1]+front*forward[1]+sign*self.cfg['follow_distance']*side[1])
                avoid = [p for k,v in b['legs'].items() if k != aid for p in (v['hide'],v['peek'])]
                pair, rows = self._cover_pair(aid, desired, b['threat'], avoid, player.position)
                self.scores[aid] = rows
                if pair is None:
                    b['failed'] = True;break
                # A new bound must make forward progress, not relabel the same point.
                if aid == mover and (distance(pair['hide'], self.actors[aid].position) < .8
                    or (pair['hide'][0]-self.actors[aid].position[0])*forward[0]+(pair['hide'][1]-self.actors[aid].position[1])*forward[1] < .5):
                    b['failed'] = True;break
                b['legs'][aid] = pair
        if b['failed']:
            for aid in living:
                self.maneuvers[aid] = {'active': False, 'role': 'OpenFormation', 'at': self.at,
                    'reason': 'no complete separated obstacle-cover pair or forward bound; explicit formation fallback',
                    'phase': b['phase'], 'cover': deepcopy(b['legs'].get(aid)),
                    'last_swap': deepcopy(b.get('last_swap')), 'threat_basis': b['basis']}
            return selected
        holder_pair, mover_pair = b['legs'][holder], b['legs'][mover]
        holder_goal = self._bound_goal(holder, holder_pair, True)
        watch = self.actors[holder]
        at_peek = distance(watch.position, holder_goal) <= .08
        if at_peek:
            watch.heading = math.atan2(b['threat'][1]-watch.position[1], b['threat'][0]-watch.position[0])
        ready_gates = {'entered_hide': holder_pair['arrived_hide'], 'at_peek': at_peek,
                       'ammunition': watch.ammo > 0, 'holder_budget': not self.moves[holder].exhausted,
                       'actual_watch_sight': self.geo.see(watch.position, watch.heading, b['threat'], self._vision('allied')),
                       'mover_budget': not self.moves[mover].exhausted and self.moves[mover].chase < self.cfg['ally_chase_travel_budget']}
        ready = all(ready_gates.values())
        if ready:b['started'] = True
        goals = {holder: holder_goal, mover: self._bound_goal(mover, mover_pair) if ready else None}
        for aid in living:
            pair = b['legs'][aid];is_holder = aid == holder
            goal = goals[aid]
            status = 'CoverWatch' if is_holder and ready else 'PrepareCover' if is_holder else 'Advance' if ready else 'WaitCover'
            detail = {'active': True, 'role': status, 'partner': mover if is_holder else holder,
                      'phase': b['phase'], 'holder': holder, 'mover': mover, 'holder_ready': ready,
                      'ready_gates': deepcopy(ready_gates), 'peek_tolerance_m': .08,
                      'cover': deepcopy(pair), 'at': self.at, 'threat_basis': b['basis'],
                      'last_swap': deepcopy(b.get('last_swap')),
                      'goal': list(goal) if goal else None, 'reason': 'physical holder readiness gates movement; swap only on actual hide arrival'}
            self.maneuvers[aid] = detail
            self.plans[aid].update(role='Overwatch' if is_holder else 'Support', goal=list(goal) if goal else None,
                                   slot=pair['id'], reason=status+'; '+detail['reason'], maneuver=deepcopy(detail))
            if goal:selected[aid] = {'id':pair['id'], 'position':goal, 'role':self.plans[aid]['role']}
            else:selected.pop(aid, None)
        return selected

    def _coordinate_germans(self):
        for aid in ('G1', 'G2', 'G3'):self.maneuvers.pop(aid, None)
        if not self._coordination():return
        living = [a for a in ('G1','G2','G3') if self.actors[a].alive]
        observers = [a for a in living if self.minds[a].live_visible and self.minds[a].memory]
        if not observers:return
        leader = min(observers)
        seen = self.minds[leader].memory
        self.german_contact = {'source':leader, 'target_id':seen.actor_id, 'position':list(seen.position), 'at':seen.at, 'basis':'own_sight_broadcast'}
        occupied = [self.actors[leader].position]
        flankers = [a for a in living if a != leader]
        dx,dy = seen.position[0]-self.actors[leader].position[0], seen.position[1]-self.actors[leader].position[1]
        length = max(math.hypot(dx,dy),.001);f=(dx/length,dy/length);s=(-f[1],f[0])
        self.maneuvers[leader] = {'active':True,'role':'ContactWatch','at':self.at,'goal':None,
                                  'contact':deepcopy(self.german_contact),'reason':'own observer holds contact; teammates receive frozen sight report'}
        for index,aid in enumerate(flankers):
            mind = self.minds[aid];sign = -1 if index==0 else 1
            previous = self.flank_legs.get(aid)
            if (not previous or previous['target_id']!=seen.actor_id
                or previous.get('source')!=leader or previous['side']!=sign
                or self.at-previous['at']>=2 and distance(previous['origin'],seen.position)>=2):
                desired = (seen.position[0]-5*f[0]+sign*4*s[0], seen.position[1]-5*f[1]+sign*4*s[1])
                options=[desired]+[(desired[0]+r*math.cos(n*math.pi/4),desired[1]+r*math.sin(n*math.pi/4)) for r in (1.5,3,6,9,12,15) for n in range(8)]
                goal=None;gates=[];route_length=0
                for point in options:
                    if not self.geo.free(point):gates.append('BlockedClearance');continue
                    if distance(point,self.actors[aid].position)<.8:gates.append('NoPhysicalAdvance');continue
                    if self.geo.blocked(point,seen.position):gates.append('NoFinalContactLane');continue
                    if distance(point,seen.position)>self._vision('german')['sight_range']-.12:gates.append('FinalLaneOutOfRange');continue
                    if any(distance(point,p)<self.cfg['reservation_separation'] for p in occupied):gates.append('ReservedByTeammate');continue
                    # Keep the assigned side: projection cannot turn both flankers into one lane.
                    if ((point[0]-seen.position[0])*s[0]+(point[1]-seen.position[1])*s[1])*sign < 1.2:
                        gates.append('WrongFlankSide');continue
                    route=self.geo.path(self.actors[aid].position,point)
                    if route['status']=='Complete':goal=point;route_length=route['length'];break
                    gates.append(route['status'])
                previous={'at':self.at,'expires':self.at+min(18,max(8,route_length/self.cfg['move_speed']+2)),
                          'origin':list(seen.position),'target_id':seen.actor_id,'source':leader,'goal':list(goal) if goal else None,
                          'desired':list(desired),'side':sign,'gates':gates,'candidate_limit':49,'path_length':route_length,
                          'path_status':'Complete' if goal else 'NoAdmittedFlank'}
                self.flank_legs[aid]=previous
            if previous['goal']:occupied.append(previous['goal'])
            if not mind.live_visible and mind.search_deadline<0 and (not mind.memory or seen.at>mind.memory.at):
                mind.memory=Observation(seen.actor_id,tuple(seen.position),seen.at,'report',0,leader)
            self.maneuvers[aid]={'active':True,'role':'FlankLeft' if sign<0 else 'FlankRight','at':self.at,
                                 'goal':deepcopy(previous['goal']),'contact':deepcopy(self.german_contact),
                                 'leg':deepcopy(previous),'reason':'own observer holds contact; opposite admitted flank; own sight required to fire'}

    def _maneuver_enemy_intent(self, aid):
        plan=self.maneuvers.get(aid)
        source=plan.get('contact',{}).get('source') if plan else None
        target=plan.get('contact',{}).get('target_id') if plan else None
        if (self._coordination() and plan and plan['active'] and source and self.actors[source].alive
                and self.minds[source].live_visible and target in self.actors and self.actors[target].alive):
            mind=self.minds[aid]
            # Use the same alert/current-sight policy for actual firing state.
            if mind.live_visible:self._enemy_intent(aid)
            if plan['role']=='ContactWatch':return None
            if self.at >= plan['leg']['expires']:
                plan['reason']='finite flank leg exhausted; hold until a materially new contact or human order'
                plan['goal']=None
                return None
            if plan['goal']:
                if not mind.live_visible:mind.transition('Investigate',self.at,'shared own-sight contact; flank approach without blind fire')
                return tuple(plan['goal'])
            return None
        goal=self._enemy_intent(aid)
        self.maneuvers.pop(aid,None)
        if self._coordination() and self.actors[aid].alive:
            mind=self.minds[aid]
            if mind.state in ('Investigate','Search'):
                self.maneuvers[aid]={'active':False,'role':'SearchSector','at':self.at,'sector':int(aid[-1]),
                    'goal':list(goal) if goal else None,'origin':list(mind.search_origin) if mind.search_origin else None,
                    'deadline':mind.search_deadline,'reason':'private frozen evidence; disjoint angular search sector; actual arrival advances index'}
        return goal

    def _sector_offset(self, aid, index, investigate=False):
        if not self._coordination():
            return ((0,0),(0,-1.6),(0,1.6))[int(aid[-1])-1] if investigate else ((0,1.8),(1.8,0),(0,-1.8),(-1.8,0))[(index+int(aid[-1])-1)%4]
        sector=int(aid[-1])-1
        angle=sector*2*math.pi/3+(-.35,.35,-.2,.2)[index%4]
        radius=2. if investigate else (2.5,4.,5.,3.2)[index%4]
        return radius*math.cos(angle),radius*math.sin(angle)
