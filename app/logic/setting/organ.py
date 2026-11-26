from pydantic import Field, ValidationInfo, field_validator, model_validator

from app.db.models.organ import OrganDB
from app.logic.setting.base import BaseSetting, BaseLogicValidate

class OrganSetting(BaseSetting):
    type = 'organ'
    MIN_RANK = 0
    MAX_RANK = 9

    hidden: bool = Field(default=False, json_schema_extra={'group': 'main'})
    closen: bool = Field(default=False, json_schema_extra={'group': 'main'})
    start_rank: int = Field(default=9, json_schema_extra={'group': 'main'})

    name: str | None = Field(default=None, json_schema_extra={'group': 'appearance', 'resettable': True})
    emodzi: str | None = Field(default=None, json_schema_extra={'group': 'appearance', 'resettable': True})
    custom_emodzi_id: str | None = Field(default=None, json_schema_extra={'group': 'appearance', 'resettable': True})
    description: str | None = Field(default=None, json_schema_extra={'group': 'appearance', 'resettable': True})
    rank_names: dict[str, str] = Field(default_factory=OrganDB.default_rank_name, json_schema_extra={'group': 'appearance'})

    redact_rank: int = Field(default=0, json_schema_extra={'group': 'permission'})
    redact_titul: int = Field(default=0, json_schema_extra={'group': 'permission'})
    kick: int = Field(default=0, json_schema_extra={'group': 'permission'})
    redact_setting: int = Field(default=0, json_schema_extra={'group': 'permission'})

    @field_validator('hidden', 'closen', mode='before')
    @classmethod
    def _validate_bool_fields(cls, value, info: ValidationInfo):
        return cls._validate_bool(value, info)

    @field_validator('start_rank', 'redact_rank', 'redact_titul', 'kick', 'redact_setting', mode='before')
    @classmethod
    def _validate_rank_fields(cls, value, info: ValidationInfo):
        return cls._validate_rank(value, info)

    @field_validator('name', 'emodzi', 'custom_emodzi_id', 'description', mode='before')
    @classmethod
    def _validate_str_fields(cls, value, info: ValidationInfo):
        return cls._validate_str(value, info)

    @field_validator('rank_names', mode='before')
    @classmethod
    def _validate_rank_names_field(cls, value, info: ValidationInfo):
        return cls._validate_rank_names(value, info)

