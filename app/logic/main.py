from app.logic.base import BaseLogic
from app.validate.api.base import AnswerBaseInfo, QueryUserUpdate, AnswerUsersBody
from app.db.models.main import TgUserDB
from app.exception.base import ParametrValidationException, UserDontFind
from app.logic.setting import UserSetting
from app.validate.api.user import AnswerUserSetting, AnswerUserSettingValues, UserSettingDefault

class MainLogic(BaseLogic):
    async def settings(self):
        user = await self.get_user()
        setting = UserSetting(user.setting)
        return AnswerUserSetting(user=self.return_query_body(user), settings=setting.validate)

    async def settings_values(self):
        user = await self.get_user()
        setting = UserSetting(user.setting)
        return AnswerUserSettingValues(user=self.return_query_body(user), values=setting.values)

    async def settings_redact(self, parametrs: dict):
        user = await self.get_user()
        setting = UserSetting(user.setting)
        setting.update(parametrs)
        user.setting = setting.model_dump_db()
        self.dao.user.update_obj(user, setting.model_dump())
        await self.dao.flush()
        return AnswerUserSetting(user=self.return_query_body(user), settings=setting.validate)

    async def settings_default(self, default: UserSettingDefault):
        user = await self.get_user()
        setting = UserSetting(user.setting)
        if default.is_all:
            setting.to_default()
            user.setting = {}
            user.name = None
            user.emodzi = None
            user.custom_emodzi_id = None
            user.description = None
        elif default.group:
            user.setting = setting.to_default(default.group)
            if default.group == 'appearance':
                user.name = None
                user.emodzi = None
                user.custom_emodzi_id = None
                user.description = None
        elif default.parametr:
            if default.parametr in UserSetting._all_fields():
                user.setting = dict(user.setting)
                user.setting.pop(default.parametr, None)
            elif default.parametr in {'name', 'emodzi', 'custom_emodzi_id', 'description'}:
                setattr(user, default.parametr, None)
            else:
                setting.check_tag({default.parametr: None})
        else:
            raise ParametrValidationException('Укажите параметр, группу или is_all')
        await self.dao.flush()
        return AnswerUserSetting(user=self.return_query_body(user), settings=setting.validate)

    async def info(self):
        user =  await self.get_user()
        body = self.return_query_body(user)
        return AnswerBaseInfo(user=body, purpose=body).to_query(user)

    async def update(self, data: QueryUserUpdate):
        user = await self.dao.user.query_by_user_id(data.user_id)
        if user is None and data.telegram:
            user = await self.dao.user.query_by_tg_id(data.telegram.tg_id)
        created = user is None
        if user is None:
            user = await self.dao.user.add({})
        if data.telegram:
            if user.tg_user:
                user.tg_user.username = data.telegram.username
                user.tg_user.fullname = data.telegram.fullname
            else:
                user.tg_user = TgUserDB(
                    tg_id=data.telegram.tg_id, 
                    username=data.telegram.username,
                    fullname=data.telegram.fullname
                )
                user.tg_id = data.telegram.tg_id
            await self.dao.flush()
        await self.store.user.cache_user(user.id, user.tg_id)
        if created:
            self.botlog.user_create(user.id, user.tg_id)
        return self.return_query_body(user)
    
    async def get_telegram(self, tg_id: int | None = None):
        if not tg_id is None:
            user = await self.dao.user.query_by_tg_id(tg_id)
        elif not self.purpose_user_id is None:
            user = await self.dao.user.query_by_user_id(self.purpose_user_id)
        else:
            raise ParametrValidationException('Вы не указали айди пользователя')
        if user is None:
            raise UserDontFind()
        await self.store.user.cache_user(user.id, user.tg_id)
        return self.return_query_body(user)

    async def search_users(
        self,
        user_id: int | None = None,
        tg_id: int | None = None,
        username: str | None = None,
        name: str | None = None,
        page: int | None = None,
        per_page: int = 5,
    ):
        if (
            user_id is None
            and tg_id is None
            and not (username and username.strip().lstrip('@').strip())
            and not (name and name.strip())
        ):
            raise ParametrValidationException('Укажите хотя бы один параметр поиска')
        users, count = await self.dao.user.search_users_paginated(
            user_id,
            tg_id,
            username,
            name,
            page,
            per_page,
        )
        return AnswerUsersBody(
            search_value=self.check_is_not_none(user_id, tg_id, username, name),
            users=[self.return_query_body(user) for user in users],
            count=count,
            page=self.pagination(page, per_page, count),
            )

    async def list_users(
        self,
        page: int | None = None,
        per_page: int = 5,
        ):
        users, count = await self.dao.user.search_users_paginated(page=page, per_page=per_page)
        return AnswerUsersBody(
            users=[self.return_query_body(user) for user in users],
            count=count,
            page=self.pagination(page, per_page, count),
            )


    async def delete_user(self, user_id: int):
        if user_id != self.user_id:
            self.check_permission()
        user = await self.dao.user.query_by_user_id(user_id)
        if user is None:
            raise UserDontFind()

        response = self.return_query_body(user)
        await self.dao.user.delete_one_by_id(user_id)
        await self.store.user.delete_user(user.id, user.tg_id)
        return response
