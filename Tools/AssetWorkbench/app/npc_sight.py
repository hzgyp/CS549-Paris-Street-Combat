"""Sight evidence for the existing ordered gates; never supplies private memory."""
import math


def evaluate_sight(origin, heading, target, vision, trace_ray):
    delta = (target[0]-origin[0], target[1]-origin[1])
    distance = math.hypot(*delta)
    dot = (delta[0]*math.cos(heading)+delta[1]*math.sin(heading))/max(distance, 1e-9)
    record = {'schema': 'paris.npc.sight.v1', 'origin': list(origin), 'heading': heading,
              'target_position': list(target), 'distance_m': distance, 'range_m': vision['sight_range'],
              'dot': dot, 'angle_degrees': math.degrees(math.acos(max(-1, min(1, dot)))),
              'fov_degrees': vision['sight_fov_degrees'], 'half_fov_degrees': vision['sight_fov_degrees']/2,
              'gates': {'distance': 'Skipped', 'angle': 'Skipped', 'occlusion': 'Skipped'},
              'visible': False, 'failure': None, 'ray': None}
    # Same predicates/order as Geometry.see and RasterGeometry.see. Displayed angles
    # are descriptive; only the original dot/cos comparison admits the FOV gate.
    if distance > vision['sight_range']:
        record['gates']['distance'], record['failure'] = 'Failure', 'Distance'
        return record
    record['gates']['distance'] = 'Success'
    if not dot >= math.cos(math.radians(vision['sight_fov_degrees']/2)):
        record['gates']['angle'], record['failure'] = 'Failure', 'Angle'
        return record
    record['gates']['angle'] = 'Success'
    record['ray'] = trace_ray(origin, target)
    if record['ray']['blocked']:
        record['gates']['occlusion'], record['failure'] = 'Failure', 'Occlusion'
    else:
        record['gates']['occlusion'], record['visible'] = 'Success', True
    return record


def rectangle_ray(origin, target, walls):
    """Same inclusive segment/slab test as intersects; nearest entry is evidence."""
    nearest = None
    for index, (x, y, w, h) in enumerate(walls):
        lo, hi = 0.0, 1.0
        for start, delta, mn, mx in ((origin[0], target[0]-origin[0], x, x+w),
                                     (origin[1], target[1]-origin[1], y, y+h)):
            if abs(delta) < 1e-12:
                if start < mn or start > mx:
                    break
            else:
                p, q = (mn-start)/delta, (mx-start)/delta
                lo, hi = max(lo, min(p, q)), min(hi, max(p, q))
                if lo > hi:
                    break
        else:
            if nearest is None or lo < nearest[0]:
                nearest = lo, index
    if nearest is None:
        return {'blocked': False, 'point': None, 'cell': None, 'reason': None}
    at, index = nearest
    return {'blocked': True, 'point': [origin[i]+at*(target[i]-origin[i]) for i in (0, 1)],
            'cell': None, 'entry_t': at, 'wall_index': index, 'reason': 'fixture_wall'}
