import json
import re
from pathlib import Path
from typing import ClassVar

from pydantic import Field, ValidationInfo, field_validator, model_validator

from app.validate.logic.setting import (
    BaseLogicValidate,
    OrganSettingValidate,
    SettingGroupMetadata,
    SettingGroupValidate,
    SettingParametrMetadata,
    SettingParametrValidate,
    SettingSubparameterValidate,
)
from app.exception.setting import (
    ChoisesValidateError,
    ParametrExistError,
    ParametrValidateError,
    RankValidateError,
)
from app.db.models.organ import OrganDB

with Path(__file__).with_name('metadata.json').open(encoding='utf-8') as metadata_file:
    _SETTING_METADATA = json.load(metadata_file)

SETTING_METADATA = {
    'groups': {
        tag: SettingGroupMetadata(tag=tag, **metadata).model_dump()
        for tag, metadata in _SETTING_METADATA['groups'].items()
    },
    'types': {
        setting_type: {
            tag: SettingParametrMetadata(
                tag=tag,
                type=setting_type,
                **metadata,
            ).model_dump()
            for tag, metadata in parameters.items()
        }
        for setting_type, parameters in _SETTING_METADATA['types'].items()
    },
}


class BaseSetting(BaseLogicValidate):
    type: ClassVar[str] = ''
    MIN_RANK: ClassVar[int] = 0
    MAX_RANK: ClassVar[int] = 9

    def __init__(self, data: dict | None = None, **kwargs):
        super().__init__(**(data or {}), **kwargs)

    @model_validator(mode='before')
    @classmethod
    def _check_unknown_tags(cls, data):
        if isinstance(data, dict):
            valid = set(cls.model_fields)
            for tag in data:
                if tag not in valid:
                    raise ParametrExistError(parametr_tag=tag)
        return data

    @classmethod
    def _validate_bool(cls, value, info: ValidationInfo):
        if type(value) is not bool:
            raise ParametrValidateError(parametr_tag=info.field_name, value=value, parametr_type='bool-типа')
        return value

    @classmethod
    def _validate_str(cls, value, info: ValidationInfo):
        if value is None:
            return None
        if type(value) is not str:
            raise ParametrValidateError(parametr_tag=info.field_name, value=value, parametr_type='строкой')
        return value

    @classmethod
    def _validate_rank(cls, value, info: ValidationInfo):
        if type(value) is not int:
            raise ParametrValidateError(parametr_tag=info.field_name, value=value, parametr_type='числом')
        if not (cls.MIN_RANK <= value <= cls.MAX_RANK):
            raise RankValidateError(parametr_tag=info.field_name, value=value, max_rank=cls.MAX_RANK, min_rank=cls.MIN_RANK)
        return value

    @classmethod
    def _validate_rank_names(cls, value, info: ValidationInfo):
        if type(value) is not dict:
            raise ParametrValidateError(parametr_tag=info.field_name, value=value, parametr_type='словарем')
        for k, v in value.items():
            if type(k) is not str or not k.isdigit():
                raise ParametrValidateError(parametr_tag=info.field_name, value=value, parametr_type='числом')
            if not (cls.MIN_RANK <= int(k) <= cls.MAX_RANK):
                raise RankValidateError(parametr_tag=info.field_name, value=value, max_rank=cls.MAX_RANK, min_rank=cls.MIN_RANK)
            if type(v) is not str:
                raise ParametrValidateError(parametr_tag=info.field_name, value=value, parametr_type='строкой')
        return OrganDB.default_rank_name() | value

    @classmethod
    def _all_fields(cls) -> list[str]:
        return list(cls.model_fields)

    def _field_default(self, name: str):
        return type(self).model_fields[name].get_default(call_default_factory=True)

    def _field_meta(self, name: str) -> dict:
        return SETTING_METADATA['types'][self.type][name]

    def _is_default(self, name: str) -> bool:
        value = getattr(self, name)
        return value is None or value == self._field_default(name)

    def _group_fields(self, group: str) -> list[str]:
        return [
            name for name in SETTING_METADATA['types'][self.type]
            if name in self._all_fields() and self._field_meta(name)['group'] == group
        ]

    @property
    def values(self) -> dict:
        return self.model_dump()

    @property
    def validate(self) -> OrganSettingValidate:
        groups = []
        metadata = SETTING_METADATA['types'][self.type]
        for group, group_metadata in SETTING_METADATA['groups'].items():
            names = self._group_fields(group)
            if not names:
                continue
            groups.append(
                SettingGroupValidate(
                    **group_metadata,
                    parametrs=[
                        self._parameter_response(name, metadata[name])
                        for name in names
                    ],
                )
            )
        return OrganSettingValidate(groups=groups)

    def _parameter_response(self, name: str, metadata: dict) -> SettingParametrValidate:
        parameter_metadata = metadata.copy()
        subparameter_metadata = parameter_metadata.pop('subparameters', None)
        value = getattr(self, name)
        subparameters = None
        if subparameter_metadata:
            subparameters = [
                SettingSubparameterValidate(
                    **subparameter,
                    value=value.get(subparameter['tag'], subparameter['default_value']),
                    is_default_value=value.get(subparameter['tag'], subparameter['default_value'])
                    == subparameter['default_value'],
                )
                for subparameter in subparameter_metadata
            ]
        return SettingParametrValidate(
            **parameter_metadata,
            value=value,
            default_value=self._field_default(name),
            is_default_value=self._is_default(name),
            subparameters=subparameters,
        )

    def check_tag(self, data: dict) -> None:
        valid = set(self._all_fields())
        for tag in data:
            if tag not in valid:
                raise ParametrExistError(parametr_tag=tag)

    @staticmethod
    def _validate_metadata_constraints(tag: str, value, metadata: dict) -> None:
        value_type = metadata.get('value_type') or metadata.get('type')
        if value_type == 'str-int' and (
            not isinstance(value, str) or re.fullmatch(r'[0-9]+', value) is None
        ):
            raise ParametrValidateError(
                parametr_tag=tag,
                value=value,
                parametr_type='строкой только из цифр',
            )

        allowed_values = metadata.get('allowed_values')
        if allowed_values is not None and value not in allowed_values:
            raise ChoisesValidateError(
                parametr_tag=tag,
                value=value,
                parametr_type='значением из списка',
                choises=allowed_values,
            )

        if type(value) in (int, float):
            minimum = metadata.get('min_value')
            maximum = metadata.get('max_value')
            if (minimum is not None and value < minimum) or (
                maximum is not None and value > maximum
            ):
                raise ParametrValidateError(
                    parametr_tag=tag,
                    value=value,
                    parametr_type=f'числом от {minimum} до {maximum}',
                )

        if isinstance(value, str):
            minimum_length = metadata.get('min_length')
            maximum_length = metadata.get('max_length')
            if minimum_length is not None and len(value) < minimum_length:
                raise ParametrValidateError(
                    parametr_tag=tag,
                    value=value,
                    parametr_type=f'строкой длиной не менее {minimum_length}',
                )
            if maximum_length is not None and len(value) > maximum_length:
                raise ParametrValidateError(
                    parametr_tag=tag,
                    value=value,
                    parametr_type=f'строкой длиной не более {maximum_length}',
                )
            pattern = metadata.get('pattern')
            if pattern is not None and re.fullmatch(pattern, value) is None:
                raise ParametrValidateError(
                    parametr_tag=tag,
                    value=value,
                    parametr_type=f'строкой формата {pattern}',
                )

    def update(self, data: dict):
        self.check_tag(data)
        current_values = {
            name: getattr(self, name)
            for name in self._all_fields()
        }
        updated_values = current_values | data
        for name, value in data.items():
            if isinstance(current_values[name], dict) and isinstance(value, dict):
                updated_values[name] = current_values[name] | value
        for name, value in updated_values.items():
            metadata = self._field_meta(name)
            self._validate_metadata_constraints(name, value, metadata)
            subparameters = {
                item['tag']: item
                for item in metadata.get('subparameters') or []
            }
            if isinstance(value, dict):
                for subtag, subvalue in value.items():
                    if subtag in subparameters:
                        self._validate_metadata_constraints(
                            f'{name}.{subtag}',
                            subvalue,
                            subparameters[subtag],
                        )
        updated_setting = type(self).model_validate(updated_values)
        for name in self._all_fields():
            setattr(self, name, getattr(updated_setting, name))
        return self

    def model_dump_db(self, is_default_value: bool = False) -> dict:
        return {
            name: getattr(self, name)
            for name in self._all_fields()
            if self._is_default(name) == is_default_value
        }

    def to_default(self, group: str | None = None) -> dict:
        if group is not None:
            if group not in SETTING_METADATA.get('groups'):
                raise ValueError(f'Unknown setting group: {group}')
            names = self._group_fields(group)
        else:
            names = self._all_fields()

        for name in names:
            if self._field_meta(name).get('resettable'):
                setattr(self, name, self._field_default(name))
        return self.model_dump_db()
