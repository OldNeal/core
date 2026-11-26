from pydantic import Field, ValidationInfo, field_validator, model_validator, computed_field

from app.db.models.organ import OrganDB
from app.logic.setting.base import BaseSetting, BaseLogicValidate
from app.validate.api.base import UserSettingValidate
from app.exception.setting import ChoisesValidateError

NOTIFY_PLATFORMS = {
    'telegram':'Телеграмм'
    }
NOTIFY_TYPES = {
    'ephemeral_message':'Эфимерное сообщение', 
    'private_chat':'В личный чат с ботом'
    }

class UserSetting(BaseSetting):
    type = 'user'

    hidden_top: bool = Field(default=False, json_schema_extra={'group': 'privacy'})
    get_notify: bool = Field(default=True, json_schema_extra={'group': 'main'})
    notify_platform: str = Field(default=list(NOTIFY_PLATFORMS)[0], json_schema_extra={'group': 'main', 'choises':NOTIFY_PLATFORMS})
    notify_type: str = Field(default=list(NOTIFY_TYPES)[0], json_schema_extra={'group': 'main', 'choises':NOTIFY_TYPES})
    use_ephemeral_message: bool = Field(default=True, json_schema_extra={'group': 'main'})
    use_rich_message: bool = Field(default=True, json_schema_extra={'group': 'main'})

    name: str | None = Field(default=None, json_schema_extra={'group': 'appearance', 'resettable': True})
    emodzi: str | None = Field(default=None, json_schema_extra={'group': 'appearance', 'resettable': True})
    custom_emodzi_id: str | None = Field(default=None, json_schema_extra={'group': 'appearance', 'resettable': True})
    description: str | None = Field(default=None, json_schema_extra={'group': 'appearance', 'resettable': True})

    @computed_field
    @property
    def is_ephemeral(self) -> bool:
        return self.notify_type == list(NOTIFY_TYPES)[0]
    
    @computed_field
    @property
    def is_send_to_private(self) -> bool:
        return self.notify_type == list(NOTIFY_TYPES)[0]
  

    @field_validator('hidden_top', 'get_notify', 'use_ephemeral_message', 'use_rich_message', mode='before')
    @classmethod
    def _validate_bool_fields(cls, value, info: ValidationInfo):
        return cls._validate_bool(value, info)

    @field_validator('notify_platform', mode='before')
    @classmethod
    def _validate_notify_platform(cls, value, info: ValidationInfo):
        value = cls._validate_str(value, info).lower()
        if value not in NOTIFY_PLATFORMS.keys():
            raise ChoisesValidateError(choises=NOTIFY_PLATFORMS.keys())
        return value

    @field_validator('notify_type', mode='before')
    @classmethod
    def _validate_notify_type(cls, value, info: ValidationInfo):
        value = cls._validate_str(value, info).lower()
        if value not in NOTIFY_TYPES.keys():
            raise ChoisesValidateError(choises=NOTIFY_TYPES.keys())
        return value

    @field_validator('name', 'emodzi', 'custom_emodzi_id', 'description', mode='before')
    @classmethod
    def _validate_str_appearance_fields(cls, value, info: ValidationInfo):
        return cls._validate_str(value, info)

    def model_dump_response(self):
        return UserSettingValidate.model_validate(self)
