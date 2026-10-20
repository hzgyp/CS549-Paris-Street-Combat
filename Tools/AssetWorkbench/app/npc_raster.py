"""Read-only Paris raster geometry for the abstract 2D world, never UE geometry."""
from array import array
from collections import deque, OrderedDict
from functools import lru_cache
import hashlib
import heapq
import json
import math
from pathlib import Path
from PIL import Image, ImageFilter
from .npc_oracle import distance
from .npc_sight import evaluate_sight

FIGURES = Path(__file__).resolve().parents[3]/'tmp/map-survey-overnight-20261013/collections/complete_v3/figures_v1'
CELL = .25


@lru_cache(maxsize=8)
def raster_data(scope='bounded_expanded', layer=0):
    if scope not in ('saved', 'bounded_expanded') or not 0 <= layer < (3 if scope == 'saved' else 5):
        raise ValueError('Unknown survey surface')
    audit = json.loads((FIGURES/'FIGURE_AUDIT.json').read_text(encoding='utf-8'))
    if audit['status'] != 'pass_independent_figures_raw_hashes_tile_pixel_parity_scope_counts':
        raise ValueError('Map audit identity mismatch')
    key = f'{scope}/L{layer}_candidate_25cm.png'
    raw = (FIGURES/key).read_bytes()
    expected = audit['outputs'][key.replace('/', '\\')]
    sha = hashlib.sha256(raw).hexdigest()
    if len(raw) != expected['size_bytes'] or sha != expected['sha256']:
        raise ValueError('Map bytes do not match the pinned survey audit')
    with Image.open(FIGURES/key) as source:
        sight = source.convert('L')
    if sight.size != (720, 960) or set(sight.tobytes()) != {0, 255}:
        raise ValueError('Unexpected raster dimensions or palette')
    # A 2-cell square erosion is conservative for the 0.35m capsule, even
    # for continuous centre positions within a cell. Unknown remains blocked.
    nav = sight.filter(ImageFilter.MinFilter(5))
    from PIL import ImageDraw
    ImageDraw.Draw(nav).rectangle((0, 0, 719, 959), outline=0, width=2)
    mask, width, height = nav.tobytes(), 720, 960
    components = array('i', [0]) * (width*height)
    sizes = {}
    for first, value in enumerate(mask):
        if not value or components[first]:
            continue
        label = len(sizes)+1
        queue = deque([first]); components[first] = label; size = 0
        while queue:
            node = queue.popleft(); size += 1
            x, y = node % width, node // width
            for nxt in (node-1 if x else -1, node+1 if x+1 < width else -1,
                        node-width if y else -1, node+width if y+1 < height else -1):
                if nxt >= 0 and mask[nxt] and not components[nxt]:
                    components[nxt] = label; queue.append(nxt)
        sizes[label] = size
    return {'sight': sight.tobytes(), 'nav': mask, 'components': components, 'sizes': sizes,
            'scope': scope, 'layer': layer, 'sha256': sha, 'width': width, 'height': height}


class RasterGeometry:
    def __init__(self, cfg, scope='bounded_expanded', layer=0):
        self.data = raster_data(scope, layer)
        self.cfg = cfg
        self.width, self.height = 180, 240
        self.cache = OrderedDict()
        self.query_count = self.expansions = self.max_expansions = 0
        self.budget_failures = self.cache_hits = 0

    def description(self):
        return {'kind': 'paris_raster_2d', 'scope': self.data['scope'], 'layer': self.data['layer'],
                'sha256': self.data['sha256'], 'cell_m': CELL, 'width_px': 720, 'height_px': 960,
                'ue_origin_m': [-4, 4], 'black_policy': 'blocked_including_unknown',
                'footprint_clearance_m': .5, 'surface_ordinals_are_not_floors': True,
                'path_node_budget': self.cfg['path_node_budget'], 'UE_connected': False}

    def _index(self, point):
        if len(point) != 2 or not all(math.isfinite(x) for x in point):
            return None
        x, y = (math.floor(v/CELL) for v in point)
        return y*720+x if 0 <= x < 720 and 0 <= y < 960 else None

    def free(self, point):
        index = self._index(point)
        return index is not None and bool(self.data['nav'][index])

    def blocked(self, a, b, inflate=0):
        """Exact supercover traversal; corner crossings check both side cells."""
        mask = self.data['nav' if inflate else 'sight']
        first, last = self._index(a), self._index(b)
        if first is None or last is None:
            return True
        x, y = first % 720, first // 720
        ex, ey = last % 720, last // 720
        dx, dy = b[0]-a[0], b[1]-a[1]
        sx, sy = (1 if dx > 0 else -1), (1 if dy > 0 else -1)
        tx = (((x+(dx > 0))*CELL-a[0])/dx) if dx else math.inf
        ty = (((y+(dy > 0))*CELL-a[1])/dy) if dy else math.inf
        dtx, dty = (CELL/abs(dx) if dx else math.inf), (CELL/abs(dy) if dy else math.inf)
        def admitted(cx, cy):
            return 0 <= cx < 720 and 0 <= cy < 960 and mask[cy*720+cx]
        for _ in range(1682):
            if not admitted(x, y):
                return True
            if (x, y) == (ex, ey):
                return False
            if abs(tx-ty) < 1e-10:
                if not admitted(x+sx, y) or not admitted(x, y+sy):
                    return True
                x += sx; y += sy; tx += dtx; ty += dty
            elif tx < ty:
                x += sx; tx += dtx
            else:
                y += sy; ty += dty
        return True

    def sight_ray(self, a, b):
        """Evidence counterpart of blocked(inflate=0), preserving supercover order."""
        first, last = self._index(a), self._index(b)
        if first is None or last is None:
            return {'blocked': True, 'point': None, 'cell': None, 'reason': 'invalid_endpoint', 'checked_cells': 0}
        x, y = first % 720, first // 720
        ex, ey = last % 720, last // 720
        dx, dy = b[0]-a[0], b[1]-a[1]
        sx, sy = (1 if dx > 0 else -1), (1 if dy > 0 else -1)
        tx = (((x+(dx > 0))*CELL-a[0])/dx) if dx else math.inf
        ty = (((y+(dy > 0))*CELL-a[1])/dy) if dy else math.inf
        dtx, dty = (CELL/abs(dx) if dx else math.inf), (CELL/abs(dy) if dy else math.inf)
        entered, checked = 0.0, 0

        def admitted(cx, cy):
            nonlocal checked
            checked += 1
            return 0 <= cx < 720 and 0 <= cy < 960 and self.data['sight'][cy*720+cx]

        def hit(cx, cy, at):
            return {'blocked': True, 'point': [a[0]+at*dx, a[1]+at*dy], 'cell': [cx, cy],
                    'entry_t': at, 'cell_size_m': CELL, 'reason': 'black_including_unknown', 'checked_cells': checked}

        for _ in range(1682):
            if not admitted(x, y):
                return hit(x, y, entered)
            if (x, y) == (ex, ey):
                return {'blocked': False, 'point': None, 'cell': None, 'reason': None, 'checked_cells': checked}
            if abs(tx-ty) < 1e-10:
                if not admitted(x+sx, y):
                    return hit(x+sx, y, tx)
                if not admitted(x, y+sy):
                    return hit(x, y+sy, ty)
                entered = tx
                x += sx; y += sy; tx += dtx; ty += dty
            elif tx < ty:
                entered = tx
                x += sx; tx += dtx
            else:
                entered = ty
                y += sy; ty += dty
        return {'blocked': True, 'point': None, 'cell': None, 'reason': 'traversal_limit', 'checked_cells': checked}

    def sight_evidence(self, origin, heading, target, vision=None):
        return evaluate_sight(origin, heading, target, self.cfg if vision is None else vision, self.sight_ray)

    def path(self, start, goal):
        self.query_count += 1
        result = lambda status, points=(), expanded=0: {'status': status, 'points': list(points),
            'expanded': expanded, 'length': sum(distance(a, b) for a, b in zip([start]+list(points), points))}
        if not self.free(start) or not self.free(goal):
            return result('InvalidEndpoint')
        if not self.blocked(start, goal, .35):
            return result('Complete', [goal])
        first, last = self._index(start), self._index(goal)
        if self.data['components'][first] != self.data['components'][last]:
            return result('Unreachable')
        key = first, last
        expanded = 0
        if key in self.cache:
            self.cache_hits += 1
            status, indices = self.cache[key]
            self.cache.move_to_end(key)
        else:
            mask = self.data['nav']; previous = {first: None}; costs = {first: 0.0}
            lx, ly = last % 720, last // 720
            def heuristic(node):
                dx, dy = abs(node % 720-lx), abs(node // 720-ly)
                return max(dx, dy)+(math.sqrt(2)-1)*min(dx, dy)
            queue = [(heuristic(first), 0.0, first)]; closed = set(); status = 'Unreachable'
            while queue:
                _, cost, node = heapq.heappop(queue)
                if node in closed:
                    continue
                if expanded >= self.cfg['path_node_budget']:
                    status = 'BudgetExceeded'; self.budget_failures += 1; break
                closed.add(node); expanded += 1
                if node == last:
                    status = 'Complete'; break
                x, y = node % 720, node // 720
                for dx, dy in ((1,0),(0,1),(-1,0),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)):
                    nx, ny = x+dx, y+dy
                    if not 0 <= nx < 720 or not 0 <= ny < 960:
                        continue
                    nxt = ny*720+nx
                    if not mask[nxt] or dx and dy and (not mask[y*720+nx] or not mask[ny*720+x]):
                        continue
                    trial = cost+(math.sqrt(2) if dx and dy else 1)
                    if trial < costs.get(nxt, math.inf):
                        costs[nxt] = trial; previous[nxt] = node
                        heapq.heappush(queue, (trial+heuristic(nxt), trial, nxt))
            indices = []
            if status == 'Complete':
                node = last
                while node is not None:
                    indices.append(node); node = previous[node]
                indices.reverse()
            self.cache[key] = status, indices
            if len(self.cache) > 1024:
                self.cache.popitem(last=False)
        self.expansions += expanded; self.max_expansions = max(self.max_expansions, expanded)
        if status != 'Complete':
            return result(status, expanded=expanded)
        raw = [((i % 720+.5)*CELL, (i//720+.5)*CELL) for i in indices]+[tuple(goal)]
        # Bounded look-ahead smoothing; continuous connectors remain checked.
        points = []; origin = start; i = 0
        while i < len(raw):
            far = min(i+24, len(raw)-1)
            while far > i and self.blocked(origin, raw[far], .35):
                far -= 1
            if self.blocked(origin, raw[far], .35):
                return result('ConnectorBlocked', expanded=expanded)
            points.append(raw[far]); origin = raw[far]; i = far+1
        return result('Complete', points, expanded)

    def see(self, origin, heading, target, vision=None):
        cfg = self.cfg if vision is None else vision
        dx, dy = target[0]-origin[0], target[1]-origin[1]
        length = math.hypot(dx, dy)
        dot = (dx*math.cos(heading)+dy*math.sin(heading))/max(length, 1e-9)
        return length <= cfg['sight_range'] and dot >= math.cos(math.radians(cfg['sight_fov_degrees']/2)) and not self.blocked(origin, target)

    def preset_positions(self, preset):
        """Deterministic authored six-member fixtures validated on this surface."""
        if preset == 'squad':
            points = self.preset_positions('search')
            # Finite candidates near the existing German anchor, admitted using
            # actual clearance/component/occlusion. No map rewrite or warp.
            anchors = [points['G3'], points['G2']]
            pool = [p for anchor in anchors for p in [anchor]+[
                (anchor[0]+r*math.cos(i*math.pi/4), anchor[1]+r*math.sin(i*math.pi/4))
                for r in (1, 2, 3) for i in range(8)]]
            fixed = [points[k] for k in ('P', 'A1', 'A2', 'G1')]
            chosen = []
            for p in pool:
                if (self.free(p) and self.blocked(p, points['P']) and all(distance(p, q) >= 1 for q in fixed)
                        and distance(p, points['P']) <= self.cfg['sight_range']-.1
                        and all(distance(p, q) >= 2.5 for q in chosen)):
                    if self.data['components'][self._index(p)] == self.data['components'][self._index(points['P'])]:
                        chosen.append(p)
                        if len(chosen) == 2:
                            points['G2'], points['G3'] = chosen
                            return points
            raise ValueError('This surface has no admitted two-occluded-squadmate fixture')
        if not self.data['sizes']:
            raise ValueError('This surface has no admitted character centres')
        largest = max(self.data['sizes'], key=self.data['sizes'].get)
        # Prefer the measured CP1 neighbourhood, then scan the whole surface.
        anchors = [(74.875, 206.875)]
        anchors += [((x+.5)*CELL, (y+.5)*CELL) for y in range(20,940,8) for x in range(20,700,8)]
        anchors.sort(key=lambda p: distance(p, (74.875,206.875)))
        offsets = {'P':(0,0),'A1':(-3,-2),'A2':(-3,2),'G1':(8,0),'G2':(16,-4),'G3':(16,4)}
        for anchor in anchors:
            points = {k:(anchor[0]+d[0],anchor[1]+d[1]) for k,d in offsets.items()}
            if not all(self.free(p) and self.data['components'][self._index(p)] == largest for p in points.values()):
                continue
            if self.blocked(points['P'], points['G1']) or any(self.blocked(points['P'], points[k], .35) for k in ('A1','A2')):
                continue
            if preset == 'follow':
                points['G1'] = points['G2']; points['G2'] = (points['G2'][0]+1, points['G2'][1])
                if not self.free(points['G2']):
                    continue
            elif preset == 'search':
                points['P'] = (anchor[0]+5,anchor[1])
                if not self.free(points['P']):
                    continue
                for aid, side in (('A1', -3), ('A2', 3)):
                    wanted = (anchor[0]-23, anchor[1]+side)
                    options = [(wanted[0]+dx*CELL, wanted[1]+dy*CELL) for dx in range(-12,13) for dy in range(-12,13)]
                    options.sort(key=lambda p: (distance(p, wanted), p))
                    point = next((p for p in options if self.free(p) and self.data['components'][self._index(p)] == largest
                                  and all(distance(p,q) > .9 for k,q in points.items() if k != aid)), None)
                    if point is None:
                        break
                    points[aid] = point
                else:
                    return points
                continue
            return points
        raise ValueError('This surface has no validated six-member preset; choose another surface')
