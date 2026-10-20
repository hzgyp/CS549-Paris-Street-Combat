"""Live 2D tactical adapter. Decisions consume observations, never hidden targets.

This deliberately extends the retained offline oracle; it is not an UE adapter.
"""
import math
from .npc_oracle import Observation, distance
from .npc_maneuvers import ManeuverWorld


class TacticalWorld(ManeuverWorld):
    def _init_tactics(self):
        self.squad_alerts = {}
        self.shots = []
        self.incidents = []
        self.combat_checks = {}
        self.plans = {}
        self._init_maneuvers()

    def _fire_check(self, aid, target_id=None, manual=False):
        actor = self.actors[aid]
        mind = self.minds.get(aid)
        if not manual:
            target_id = mind.memory.actor_id if mind and mind.live_visible and mind.memory else None
        detail = {'at': self.at, 'target': target_id, 'range_limit': 20,
                  'ammo': actor.ammo, 'cooldown_remaining': round(max(0, 1.5-(self.at-actor.last_fire)), 3),
                  'damage': self.parameters['combat_damage'], 'own_sight_required': not manual}
        target = self.actors.get(target_id)
        reason = None
        if not actor.alive:
            reason = 'shooter_dead'
        elif not manual and not self._allow_fire:
            reason = 'simulation_paused'
        elif not manual and mind.state not in ('Engage', 'Support', 'Overwatch'):
            reason = 'alert_or_noncombat_state'
        elif not target or not target.alive or target.team == actor.team:
            reason = 'no_live_hostile_in_own_sight'
        else:
            d = distance(actor.position, target.position)
            detail.update({'origin': list(actor.position), 'target_position': list(target.position), 'distance': d})
            if not manual and not self.geo.see(actor.position, actor.heading, target.position, self._vision(actor.team)):
                reason = 'own_sight_lost'
            elif d > 20:
                reason = 'weapon_range'
            elif self.geo.blocked(actor.position, target.position):
                reason = 'wall_occlusion'
            else:
                dx, dy = target.position[0]-actor.position[0], target.position[1]-actor.position[1]
                for other in self.actors.values():
                    if not other.alive or other.id in (aid, target_id):
                        continue
                    u = ((other.position[0]-actor.position[0])*dx+(other.position[1]-actor.position[1])*dy)/max(d*d, 1e-9)
                    closest = (actor.position[0]+u*dx, actor.position[1]+u*dy)
                    if 0 < u < 1 and distance(closest, other.position) < self.cfg['capsule_radius']:
                        reason = 'body_blocks_fire'
                        detail['blocking_actor'] = other.id
                        break
        if not reason and actor.ammo <= 0:
            reason = 'ammunition_empty'
        if not reason and detail['cooldown_remaining'] > 0:
            reason = 'weapon_cooldown'
        detail.update({'permitted': reason is None, 'reason': reason or 'clear_own_sight_and_fire_lane'})
        return detail

    def _fire(self, aid, target_id=None, manual=False):
        check = self._fire_check(aid, target_id, manual)
        self.combat_checks[aid] = check
        if not check['permitted']:
            return {**check, 'fired': False}
        actor, target = self.actors[aid], self.actors[check['target']]
        actor.ammo -= 1
        actor.last_fire = self.at
        actor.heading = math.atan2(target.position[1]-actor.position[1], target.position[0]-actor.position[0])
        damage = min(target.health, self.parameters['combat_damage'])
        target.health = round(target.health-damage, 6)
        killed = target.health <= 0
        shot = {**check, 'id': len(self.shots)+1, 'shooter': aid, 'fired': True,
                'damage_applied': damage, 'killed': killed, 'health_after': target.health}
        # Copy event coordinates; later movement must not alter a report/history.
        self.shots.append(shot)
        self.event(aid, 'Shot', f'{check["target"]}: {damage:g} damage; {target.health:g} health')
        if damage:
            self._report_attack(target.id, aid, killed)
        if killed:
            target.alive = False
            self._cancel(target.id)
            self.moves[target.id].goal, self.moves[target.id].points, self.moves[target.id].result = None, [], 'Dead'
            self.reservations.pop(target.id, None)
            self.reports.pop(target.id, None)
            if target.id in self.minds:
                self.minds[target.id].live_visible = False
                self.minds[target.id].search_deadline = -1
                self.minds[target.id].transition('Dead', self.at, '2D health reached zero; reset required')
            for mind in self.minds.values():
                mind.invalidate(target.id, self.at)
            self.event(target.id, 'Casualty', '2D casualty; no automatic revival or replacement')
            if target.id in self.minds:
                self.combat_checks[target.id] = self._fire_check(target.id)
                self._tick_behavior(target.id, {'goal': None})
        return shot

    def _report_attack(self, victim_id, attacker_id, killed):
        victim, attacker = self.actors[victim_id], self.actors[attacker_id]
        own = self.minds.get(victim_id)
        seen = own.memory if own and own.live_visible and own.memory and own.memory.actor_id == attacker_id else None
        # Gunfire is an explicit observable emission. If the victim did not see
        # its source, report only a coarse muzzle/bearing estimate at that event.
        origin = tuple(seen.position) if seen else tuple(round(x/2)*2 for x in attacker.position)
        incident = {'id': len(self.incidents)+1, 'at': self.at, 'victim': victim_id,
                    'kind': 'casualty' if killed else 'hit', 'team': victim.team,
                    'position': list(origin), 'target_id': seen.actor_id if seen else 'unknown',
                    'sense': 'report', 'source': victim_id,
                    'basis': 'victim_last_sight' if seen else 'coarse_gunfire_bearing',
                    'uncertainty': 0 if seen else 1.5, 'recipients': []}
        for aid, mind in self.minds.items():
            if self.actors[aid].alive and self.actors[aid].team == victim.team and (aid != victim_id or not killed):
                incident['recipients'].append(aid)
                prior = self.squad_alerts.get(aid)
                # Active reports never refresh their deadline on every bullet.
                fresh = not prior or (self.at-prior['at'] >= self.cfg['search_duration']
                                     or distance(prior['position'], origin) >= 4)
                if fresh or killed and prior['kind'] != 'casualty':
                    self.squad_alerts[aid] = {**incident, 'recipients': []}
                    self.event(aid, 'SquadReport', f'{victim_id} {incident["kind"]}; frozen {incident["basis"]}; own sight required to fire')
        self.incidents.append(incident)

    def _accept_report(self, aid):
        mind = self.minds[aid]
        notice = self.squad_alerts.get(aid)
        if not notice or mind.live_visible:
            return False
        if self.at-notice['at'] > self.cfg['memory_age'] or notice['id'] <= getattr(mind, '_accepted_notice', 0):
            return False
        mind._accepted_notice = notice['id']
        # A casualty update during this search explains urgency but does not
        # restart its lifetime or overwrite a newer own observation.
        if mind.search_deadline >= 0:
            return True
        if mind.memory and mind.memory.at > notice['at']:
            return False
        mind.memory = Observation(notice['target_id'], tuple(notice['position']), notice['at'],
                                  'report', notice['uncertainty'], notice['victim'])
        mind.transition('Investigate', self.at, 'same-squad hit/casualty report; no visual lock')
        return True

    def _enemy_intent(self, aid):
        """Per-brain finite search, with distinct sectors from frozen evidence."""
        mind, actor = self.minds[aid], self.actors[aid]
        self._accept_report(aid)
        if (mind.memory and mind.memory.sense == 'hearing' and mind.state == 'Alert'
                and self.at-mind.state_since < self.cfg['alert_dwell']-1e-8):
            return None
        if mind.live_visible or (mind.memory and mind.memory.sense == 'sight'
                                 and self.at-mind.last_sight < self.cfg['loss_grace']-1e-8):
            goal = mind.enemy_intent(self.at, actor.position, self.cfg)
            if mind.state == 'Engage':
                mind.reason = 'own current sight; finite 2D fire gates apply'
            return goal
        if mind.memory and mind.memory.at > mind.consumed_observation:
            if mind.search_deadline < 0:
                mind.search_started, mind.search_deadline = self.at, self.at+self.cfg['search_duration']
                mind.search_index, mind.search_origin, mind.search_goal = 0, mind.memory.position, None
                mind.transition('Investigate', self.at, 'frozen own observation or squad report; finite search')
            if self.at >= mind.search_deadline-1e-8 or mind.search_index >= self.cfg['search_points']:
                mind.consumed_observation, mind.search_deadline = mind.memory.at, -1
                mind.transition('Return', self.at, 'deadline or finite searched points exhausted')
                return mind.home
            sector = int(aid[-1])-1
            origin = mind.search_origin
            # Spread the investigation approaches; knowledge origin is unchanged.
            offset = self._sector_offset(aid, mind.search_index, investigate=True)
            investigate = (origin[0]+offset[0], origin[1]+offset[1])
            if mind.state == 'Investigate':
                goal = self._follow_goal(aid, investigate)
                if goal is not None and distance(actor.position, goal) > self.cfg['arrival_radius']:
                    mind.search_goal = goal
                    return goal
                mind.transition('Search', self.at, 'approach reached or no complete approach; inspect bounded sector points')
                mind.search_goal = None
            if mind.state == 'Search':
                if mind.search_goal is not None and distance(actor.position, mind.search_goal) <= self.cfg['arrival_radius']:
                    mind.search_index += 1
                    mind.search_goal = None
                    if mind.search_index >= self.cfg['search_points']:
                        mind.consumed_observation, mind.search_deadline = mind.memory.at, -1
                        mind.transition('Return', self.at, 'all finite sector points physically visited')
                        return mind.home
                dx, dy = self._sector_offset(aid, mind.search_index)
                mind.search_goal = (origin[0]+dx, origin[1]+dy)
                return mind.search_goal
        return mind.enemy_intent(self.at, actor.position, self.cfg)

    def _plan_basic_allies(self):
        player = self.actors['P']
        self.scores, self.plans = {}, {}
        selected = {}
        for index, aid in enumerate(('A1', 'A2')):
            actor, mind, movement = self.actors[aid], self.minds[aid], self.moves[aid]
            if not actor.alive:
                continue
            own = mind.memory if mind.memory and self.at-mind.memory.at <= self.cfg['report_age'] else None
            reports = [Observation(r.actor_id, r.position, r.at, 'report', r.uncertainty, k)
                       for k, r in self.reports.items() if k != aid and self.actors[k].alive]
            self._accept_report(aid)
            if mind.memory and mind.memory.sense == 'report' and self.at-mind.memory.at <= self.cfg['report_age']:
                reports.append(mind.memory)
            mind.knowledge = own or (max(reports, key=lambda r: (r.at, r.actor_id)) if reports else None)
            mode = int(self.parameters['allied_mode'])
            leashed = distance(actor.position, player.position) <= self.cfg['ally_player_envelope']
            contact = bool(mind.knowledge and leashed and movement.chase < self.cfg['ally_chase_travel_budget'])
            role = ('Support' if index == 0 else 'Overwatch') if contact else ('Scout' if mode == 2 and index == 0 else 'Cover' if mode else 'Follow')
            heading = player.heading
            if contact:
                heading = math.atan2(mind.knowledge.position[1]-player.position[1], mind.knowledge.position[0]-player.position[0])
            f, s = (math.cos(heading), math.sin(heading)), (-math.sin(heading), math.cos(heading))
            sign, radius = (-1 if index == 0 else 1), self.cfg['follow_distance']
            front = self.parameters['scout_distance'] if role == 'Scout' else (-radius if role == 'Follow' else (1 if index == 0 else -1))
            side = 1.2*sign if role in ('Scout', 'Follow') else radius*sign
            desired = (player.position[0]+front*f[0]+side*s[0], player.position[1]+front*f[1]+side*s[1])
            candidates = [desired]+[(player.position[0]+radius*math.cos(heading+sign*a), player.position[1]+radius*math.sin(heading+sign*a))
                                    for a in (.45, .9, 1.4, 1.9, 2.4, 2.9)]
            if contact:
                candidates.append(actor.position)
            rows = []
            for cid, point in enumerate(candidates):
                gates = []
                if not self.geo.free(point):
                    gates.append('BlockedClearance')
                if distance(point, player.position) > self.cfg['ally_player_envelope'] or distance(point, player.position) < .8:
                    gates.append('PlayerLeash')
                if any(distance(point, r['position']) < self.cfg['reservation_separation'] for r in selected.values()):
                    gates.append('ReservedByTeammate')
                route = self.geo.path(actor.position, point) if not gates else {'status': 'Rejected', 'length': 0}
                if not gates and route['status'] != 'Complete':
                    gates.append(route['status'])
                if movement.exhausted:
                    gates.append('MoveBudgetExhausted')
                lane = bool(contact and not self.geo.blocked(point, mind.knowledge.position))
                score = (2*float(lane) if contact else 0)+max(0, 1-distance(point, desired)/12)-route['length']/60
                rows.append({'id': aid+'.C'+str(cid+1), 'position': tuple(point), 'role': role, 'valid': not gates,
                             'gates': gates, 'score': round(score, 6), 'features': {'lane': float(lane)}, 'contributions': {}})
            good = [r for r in rows if r['valid']]
            chosen = max(good, key=lambda r: (r['score'], r['id'])) if good else None
            self.scores[aid] = rows
            if chosen:
                selected[aid] = chosen
            self.plans[aid] = {'role': role, 'desired_slot': list(desired), 'goal': list(chosen['position']) if chosen else None,
                'slot': chosen['id'] if chosen else None, 'contact': contact, 'mode': mode,
                'follow_distance': radius, 'scout_distance': self.parameters['scout_distance'],
                'observation': self._tree_observation(mind.knowledge),
                'reason': 'observed contact within player leash' if contact else 'friendly player heading and separated reachable wings',
                'leash': self.cfg['ally_player_envelope'], 'chase_used': movement.chase,
                'chase_limit': self.cfg['ally_chase_travel_budget']}
        return selected
