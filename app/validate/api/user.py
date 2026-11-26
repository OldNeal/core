from app.validate.api.base import AnswerBody, QueryBody, BaseAPIValidate
from app.validate.logic.setting import OrganSettingValidate


class AnswerUserSetting(AnswerBody):
    settings: OrganSettingValidate


class AnswerUserSettingValues(AnswerBody):
    values: dict


class QueryUserSetting(QueryBody):
    parametrs: dict


class UserSettingDefault(BaseAPIValidate):
    parametr: str | None = None
    group: str | None = None
    is_all: bool = False


class QueryUserSettingDefault(QueryBody):
    to_default: UserSettingDefault
