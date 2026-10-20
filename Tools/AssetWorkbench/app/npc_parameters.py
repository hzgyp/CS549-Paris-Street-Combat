"""Session-local tuning; policy.json remains the reproducible baseline."""
import math
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


class Parameters(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    follow_distance: float = Field(default=3, ge=1, le=10)
    german_sight_range: float = Field(default=14, ge=2, le=40)
    german_sight_fov_degrees: float = Field(default=120, ge=30, le=180)
    loss_grace: float = Field(default=.6, ge=0, le=3)
    search_duration: float = Field(default=12, ge=1, le=30)
    allied_mode: Literal[0, 1, 2] = 2
    scout_distance: float = Field(default=5, ge=1, le=8)
    combat_damage: float = Field(default=20, ge=0, le=50)
    tactical_coordination: Literal[0, 1] = 1

    @field_validator('*', mode='before')
    @classmethod
    def finite_number(cls, value):
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError('A finite number is required')
        return value


LABELS = {
    'follow_distance': (['跟随 / 掩护半径', 'Follow / cover radius'], 'm', .5),
    'german_sight_range': (['德军视距', 'German sight range'], 'm', 1),
    'german_sight_fov_degrees': (['德军视野角度', 'German field of view'], '°', 5),
    'loss_grace': (['丢失视线宽限', 'Sight-loss grace'], 's', .1),
    'search_duration': (['搜索最长时间', 'Maximum search time'], 's', .5),
    'allied_mode': (['盟军行进分工', 'Allied movement roles'], '', 1),
    'scout_distance': (['前出探路距离', 'Scout distance ahead'], 'm', .5),
    'combat_damage': (['每发伤害（0为只观察）', 'Damage per shot (0: observe)'], 'HP', 5),
    'tactical_coordination': (['小队掩体与协同', 'Cover and squad coordination'], '', 1),
}


def parameter_schema():
    fields = Parameters.model_json_schema()['properties']
    return [{'key': key, 'label': label, 'unit': unit, 'step': step,
             'min': fields[key].get('minimum', 0), 'max': fields[key].get('maximum', 2),
             'default': fields[key]['default'],
             **({'choices': [{'value': v, 'label': label} for v, label in enumerate([
                 ['跟随', 'Follow'], ['环绕掩护', 'Cover wings'], ['前出探路 + 侧翼掩护', 'Scout + wing cover']])]} if key == 'allied_mode' else
                {'choices': [{'value': 0, 'label': ['基础分工', 'Basic roles']}, {'value': 1, 'label': ['掩体 / 交替推进 / 包抄', 'Cover / bounds / flanking']}]} if key == 'tactical_coordination' else {})}
            for key, (label, unit, step) in LABELS.items()]


def normalize(values=None, current=None):
    return Parameters.model_validate({**(current or {}), **(values or {})}).model_dump()
