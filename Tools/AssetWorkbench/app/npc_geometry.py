"""Small synthetic geometry adapter; bounded BFS is NOT production NavMesh."""
from collections import deque
import math
from .npc_oracle import distance
from .npc_sight import evaluate_sight, rectangle_ray


def intersects(a, b, rect, inflate=0):
    x, y, w, h = rect
    lo, hi = 0.0, 1.0
    for start, delta, mn, mx in ((a[0], b[0]-a[0], x-inflate, x+w+inflate),
                                 (a[1], b[1]-a[1], y-inflate, y+h+inflate)):
        if abs(delta) < 1e-12:
            if start < mn or start > mx:
                return False
        else:
            p, q = (mn-start)/delta, (mx-start)/delta
            lo, hi = max(lo, min(p, q)), min(hi, max(p, q))
            if lo > hi:
                return False
    return True


class Geometry:
    def __init__(self, walls, cfg, width=32, height=22):
        self.walls, self.cfg = walls, cfg
        self.width, self.height = width, height
        self.cache = {}
        self.query_count = self.expansions = self.max_expansions = 0
        self.budget_failures = 0
        self.cache_hits = 0

    def blocked(self, a, b, inflate=0):
        return any(intersects(a, b, r, inflate) for r in self.walls)

    def sight_evidence(self, origin, heading, target, vision=None):
        return evaluate_sight(origin, heading, target, self.cfg if vision is None else vision,
                              lambda a, b: rectangle_ray(a, b, self.walls))

    def free(self, p):
        r = self.cfg['capsule_radius']
        return r < p[0] < self.width-r and r < p[1] < self.height-r and not self.blocked(p, p, r)

    def path(self, start, goal):
        """Budget exhaustion is distinct from proven finite-fixture unreachability."""
        self.query_count += 1
        if not self.free(start) or not self.free(goal):
            return {'status': 'InvalidEndpoint', 'points': [], 'length': 0, 'expanded': 0}
        if not self.blocked(start, goal, self.cfg['capsule_radius']):
            return {'status': 'Complete', 'points': [goal], 'length': distance(start, goal), 'expanded': 0}
        first, last = tuple(round(x) for x in start), tuple(round(x) for x in goal)
        key = (first, last)
        if key in self.cache:
            self.cache_hits += 1
            status, grid = self.cache[key]
            expanded = 0
        else:
            queue, previous = deque([first]), {first: None}
            expanded, status = 0, 'Unreachable'
            while queue:
                if expanded >= self.cfg['path_node_budget']:
                    status = 'BudgetExceeded'
                    self.budget_failures += 1
                    break
                node = queue.popleft()
                expanded += 1
                if node == last:
                    status = 'Complete'
                    break
                for dx, dy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                    nxt = (node[0]+dx, node[1]+dy)
                    if nxt not in previous and self.free(nxt) and not self.blocked(node, nxt, self.cfg['capsule_radius']):
                        previous[nxt] = node
                        queue.append(nxt)
            grid = []
            if status == 'Complete':
                node = last
                while node is not None:
                    grid.append(node)
                    node = previous[node]
                grid.reverse()
            self.cache[key] = (status, grid)
        self.expansions += expanded
        self.max_expansions = max(self.max_expansions, expanded)
        if status != 'Complete':
            return {'status': status, 'points': [], 'length': 0, 'expanded': expanded}
        points = list(grid) + [goal]
        points = [tuple(p) for p in points]
        # Validate actual continuous connectors too; rounded nodes aren't arrival.
        check = [start] + points
        if any(self.blocked(a, b, self.cfg['capsule_radius']) for a, b in zip(check, check[1:])):
            return {'status': 'ConnectorBlocked', 'points': [], 'length': 0, 'expanded': expanded}
        length = sum(distance(a, b) for a, b in zip(check, check[1:]))
        return {'status': status, 'points': points, 'length': length, 'expanded': expanded}

    def see(self, origin, heading, target, vision=None):
        cfg = self.cfg if vision is None else vision
        delta = (target[0]-origin[0], target[1]-origin[1])
        d = math.hypot(*delta)
        dot = (delta[0]*math.cos(heading)+delta[1]*math.sin(heading))/max(d, 1e-9)
        return d <= cfg['sight_range'] and dot >= math.cos(math.radians(cfg['sight_fov_degrees']/2)) and not self.blocked(origin, target)
