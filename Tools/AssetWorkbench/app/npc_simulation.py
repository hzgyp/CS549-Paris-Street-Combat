"""Authenticated private simulation sessions and exact local-owner map allowlist."""
from collections import OrderedDict
import hashlib
import json
import math
import secrets
import threading
import time
from typing import Literal
from fastapi import Request
from fastapi.responses import Response
from pydantic import BaseModel, ConfigDict, Field
from .npc_engine import World, CFG
from .npc_behavior_tree import definitions
from .npc_parameters import Parameters, parameter_schema
from .npc_raster import RasterGeometry, raster_data
from .security import WorkbenchError


class CreateInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    preset: Literal['follow', 'support', 'search', 'squad'] = 'follow'
    layout: dict[str, list[float]] | None = None
    scene: Literal['paris', 'exercise'] = 'paris'
    scope: Literal['saved', 'bounded_expanded'] = 'bounded_expanded'
    layer: int = Field(default=0, ge=0, le=4)
    headings: dict[str, float] | None = None
    expected_map_sha256: str | None = None
    parameters: Parameters | None = None


class MutationInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    revision: int = Field(ge=0)
    request_id: str = Field(min_length=8, max_length=80, pattern=r'^[A-Za-z0-9_-]+$')
    operation: Literal['step', 'place', 'walk', 'rotate', 'configure', 'fire']
    seconds: float = Field(default=.5, ge=.1, le=.5)
    motion_samples: bool = False
    actor_id: Literal['P', 'A1', 'A2', 'G1', 'G2', 'G3'] = 'P'
    position: list[float] | None = Field(default=None, min_length=2, max_length=2)
    heading: float | None = None
    parameters: Parameters | None = None


def install_npc_simulation(app, root, local_only=True):
    sessions = {}
    global_lock = threading.Lock()
    map_cache = {}
    figures = root/'tmp/map-survey-overnight-20261013/collections/complete_v3/figures_v1'

    def local():
        if not local_only:
            raise WorkbenchError('LOCAL_ONLY', '二维交互设计仅在本机平台开放', 403)

    def owner(request):
        local()
        return request.cookies.get('aw_session')

    def lookup(sid, request):
        with global_lock:
            row = sessions.get(sid)
            if not row or row['owner'] != owner(request):
                raise WorkbenchError('NOT_FOUND', '模拟会话不存在或已失效', 404)
            row['seen'] = time.monotonic()
            return row

    @app.get('/api/v1/npc-simulation')
    def descriptor():
        local()
        metadata = {'presets': ['follow', 'support', 'search', 'squad'], 'duration': 120, 'bounds': [180, 240],
                    'fixed_dt': .1, 'geometry': 'paris_raster_2d', 'UE_connected': False,
                    'config': {'sight_range': 14, 'sight_fov_degrees': 120, 'hearing_range': 10,
                               'capsule_radius': .35, 'arrival_radius': .45, 'search_duration': 12},
                    'map': {'available': False}, 'behavior_tree_definitions': definitions(), 'parameter_schema': parameter_schema()}
        if (figures/'FIGURE_AUDIT.json').is_file():
            audit = json.loads((figures/'FIGURE_AUDIT.json').read_text(encoding='utf-8'))
            if audit['status'] != 'pass_independent_figures_raw_hashes_tile_pixel_parity_scope_counts':
                raise WorkbenchError('MAP_IDENTITY', '地图审计身份不匹配', 409)
            metadata['map'] = {'available': True, 'bounds_m': audit['world_bounds_m'], 'dimensions': audit['dimensions'],
                               'cell_m': .25, 'origin_m': [70.875, -202.875], 'scopes': {'saved': 3, 'bounded_expanded': 5},
                               'reference_only': False, 'surface_ordinals_are_not_floors': True,
                               'black_policy': 'blocked_including_unknown', 'path_node_budget': 12000}
        return metadata

    @app.get('/api/v1/npc-simulation/masks/{scope}/{layer}')
    def sight_mask(scope: Literal['saved', 'bounded_expanded'], layer: int):
        local()
        try:
            data = raster_data(scope, layer)
        except (ValueError, OSError, KeyError) as e:
            raise WorkbenchError('MAP_IDENTITY', str(e), 422)
        return Response(data['sight'], media_type='application/octet-stream',
                        headers={'X-Map-SHA256': data['sha256']})

    @app.get('/api/v1/npc-simulation/maps/{scope}/{layer}/{kind}')
    def map_image(scope: Literal['saved', 'bounded_expanded'], layer: int, kind: Literal['candidate', 'status']):
        local()
        if not 0 <= layer < (3 if scope == 'saved' else 5):
            raise WorkbenchError('NOT_FOUND', '地图表面不存在', 404)
        key = f'{scope}/L{layer}_{kind}_25cm.png'
        path = figures/key
        if not path.is_file():
            raise WorkbenchError('NOT_FOUND', '本机测绘图未恢复', 404)
        stat = path.stat()
        stamp = (stat.st_size, stat.st_mtime_ns)
        if map_cache.get(key, {}).get('stamp') != stamp:
            audit = json.loads((figures/'FIGURE_AUDIT.json').read_text(encoding='utf-8'))
            expected = audit['outputs'].get(key.replace('/', '\\'))
            data = path.read_bytes()
            if not expected or len(data) != expected['size_bytes'] or hashlib.sha256(data).hexdigest() != expected['sha256']:
                raise WorkbenchError('MAP_IDENTITY', '地图字节与固定审计不一致', 409)
            map_cache[key] = {'stamp': stamp, 'data': data}
        return Response(map_cache[key]['data'], media_type='image/png')

    @app.post('/api/v1/npc-simulation/sessions')
    def create(payload: CreateInput, request: Request):
        who = owner(request)
        try:
            geo = RasterGeometry(dict(CFG, path_node_budget=12000), payload.scope, payload.layer) if payload.scene == 'paris' else None
            if payload.expected_map_sha256 and (geo is None or geo.data['sha256'] != payload.expected_map_sha256):
                raise ValueError('Saved layout map identity differs from the current audited raster')
            world = World(payload.preset, payload.layout, geo, payload.headings,
                          payload.parameters.model_dump(exclude_unset=True) if payload.parameters else None)
        except (ValueError, TypeError, OverflowError, OSError, KeyError) as e:
            raise WorkbenchError('INVALID_LAYOUT', str(e), 422)
        with global_lock:
            for k in list(sessions):
                if time.monotonic()-sessions[k]['seen'] > 3600:
                    del sessions[k]
            owned = sorted((k for k in sessions if sessions[k]['owner'] == who), key=lambda k: sessions[k]['seen'])
            if len(owned) >= 4:
                del sessions[owned[0]]
            if len(sessions) >= 32:
                raise WorkbenchError('SIM_BUSY', '本机模拟会话已满，稍后再试', 409)
            sid = secrets.token_urlsafe(18)
            sessions[sid] = {'world': world, 'owner': who, 'lock': threading.Lock(), 'seen': time.monotonic(), 'requests': OrderedDict()}
        return {'session_id': sid, 'frame': world.frame(), 'layout': world.layout()}

    @app.get('/api/v1/npc-simulation/sessions/{sid}')
    def current(sid: str, request: Request):
        row = lookup(sid, request)
        with row['lock']:
            return {'session_id': sid, 'frame': row['world'].frame(), 'layout': row['world'].layout(), 'history': row['world'].history}

    @app.post('/api/v1/npc-simulation/sessions/{sid}')
    def mutate(sid: str, payload: MutationInput, request: Request):
        row = lookup(sid, request)
        with row['lock']:
            fingerprint = payload.model_dump_json()
            if payload.request_id in row['requests']:
                old_fingerprint, old_result = row['requests'][payload.request_id]
                if old_fingerprint != fingerprint:
                    raise WorkbenchError('REQUEST_REUSED', '同一请求ID不能用于不同操作', 409)
                return old_result
            world = row['world']
            if payload.revision != world.revision:
                raise WorkbenchError('STALE_SIM', '模拟已更新，请恢复最新状态后再操作', 409)
            samples = [world.motion_sample()] if payload.operation == 'step' and payload.motion_samples else None
            try:
                if payload.operation == 'step':
                    world.step(payload.seconds, samples)
                elif payload.operation == 'configure':
                    if payload.parameters is None:
                        raise ValueError('Parameters are required')
                    world.configure(payload.parameters.model_dump(exclude_unset=True))
                else:
                    if payload.operation not in ('rotate', 'fire') and (payload.position is None or not all(math.isfinite(x) for x in payload.position)):
                        raise ValueError('A finite 2D position is required')
                    world.command(payload.operation, payload.actor_id, payload.position, payload.heading)
            except ValueError as e:
                raise WorkbenchError('INVALID_SIM_COMMAND', str(e), 422)
            world.revision += 1
            result = {'session_id': sid, 'frame': world.frame(), 'layout': world.layout()}
            if payload.operation != 'step':
                world.history.append(result['frame'])
                world.history = world.history[-240:]
            if samples is not None:
                result['motion_samples'] = samples
            row['requests'][payload.request_id] = (fingerprint, result)
            while len(row['requests']) > 100:
                row['requests'].popitem(last=False)
            return result
