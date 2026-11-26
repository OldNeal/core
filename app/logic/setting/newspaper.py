from pydantic import Field, ValidationInfo, field_validator, model_validator

from app.logic.setting.base import BaseSetting, BaseLogicValidate

class NewsPaperSetting(BaseSetting):
    type = 'news_paper'
    MIN_RANK = 0
    MAX_RANK = 2

    name: str | None = Field(default=None, json_schema_extra={'group': 'appearance', 'resettable': True})
    emodzi: str | None = Field(default=None, json_schema_extra={'group': 'appearance', 'resettable': True})
    custom_emodzi_id: str | None = Field(default=None, json_schema_extra={'group': 'appearance', 'resettable': True})
    description: str | None = Field(default=None, json_schema_extra={'group': 'appearance', 'resettable': True})

    start_rank: int = Field(default=2, json_schema_extra={'group': 'main'})
    editor_rank: int = Field(default=1, json_schema_extra={'group': 'permission'})

    @field_validator('name', 'emodzi', 'custom_emodzi_id', 'description', mode='before')
    @classmethod
    def _validate_str_fields(cls, value, info: ValidationInfo):
        return cls._validate_str(value, info)

    @field_validator('start_rank', 'editor_rank', mode='before')
    @classmethod
    def _validate_rank_fields(cls, value, info: ValidationInfo):
        return cls._validate_rank(value, info)

