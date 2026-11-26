from typing import Any, Literal

from app.validate.logic.base import BaseLogicValidate


SettingGroupTag = Literal['main', 'privacy', 'permission', 'appearance']
SettingDependencyOperator = Literal['equals', 'not_equals', 'in', 'not_in']


class SettingDependency(BaseLogicValidate):
    tag: str
    operator: SettingDependencyOperator = 'equals'
    value: Any
    description: str | None = None


class SettingSubparameterMetadata(BaseLogicValidate):
    tag: str
    name: str
    type: str = 'str'
    default_value: Any
    emodzi: str | None = None
    custom_emodzi_id: str | None = None
    description: str | None = None
    is_redact: bool = True
    is_hidden: bool = False
    min_length: int | None = None
    max_length: int | None = None
    pattern: str | None = None


class SettingParametrMetadata(BaseLogicValidate):
    tag: str
    name: str
    group: SettingGroupTag
    type: str
    emodzi: str | None = None
    custom_emodzi_id: str | None = None
    description: str | None = None
    is_redact: bool
    is_hidden: bool
    resettable: bool
    choises: dict[str, str] | None = None
    allowed_values: list[Any] | None = None
    min_value: int | float | None = None
    max_value: int | float | None = None
    min_length: int | None = None
    max_length: int | None = None
    pattern: str | None = None
    key_min_value: int | float | None = None
    key_max_value: int | float | None = None
    depends_on: list[SettingDependency] | None = None
    subparameters: list[SettingSubparameterMetadata] | None = None


class SettingSubparameterValidate(SettingSubparameterMetadata):
    value: Any
    is_default_value: bool


class SettingGroupMetadata(BaseLogicValidate):
    tag: SettingGroupTag
    name: str
    emodzi: str | None = None
    custom_emodzi_id: str | None = None
    description: str | None = None


class SettingParametrValidate(SettingParametrMetadata):
    """Полное описание параметра и его текущего значения в ответе API."""

    value: Any
    default_value: Any
    is_default_value: bool
    subparameters: list[SettingSubparameterValidate] | None = None


class SettingGroupValidate(SettingGroupMetadata):
    """Описание группы параметров в ответе API."""

    parametrs: list[SettingParametrValidate]


class OrganSettingValidate(BaseLogicValidate):
    groups: list[SettingGroupValidate]
