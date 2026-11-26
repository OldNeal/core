from app.logic.main import MainLogic
from app.service.base import BaseService

class MainService(BaseService):
    def __init__(self, session, user_id: int | None = None, purpose_user_id: int | None = None, is_admin: bool = False):
        super().__init__(session, user_id, purpose_user_id, is_admin)
        self.logic = MainLogic(session, user_id=user_id, purpose_user_id=purpose_user_id, is_admin=self.is_admin)

    async def info(self):
        return await self.logic.info()

    async def settings(self):
        return await self.logic.settings()

    async def settings_values(self):
        return await self.logic.settings_values()

    async def settings_redact(self, parametrs: dict):
        return await self.logic.settings_redact(parametrs)

    async def settings_default(self, default):
        return await self.logic.settings_default(default)

    async def update(self, user):
        return await self.logic.update(user)
    
    async def get_telegram(self, tg_id: int | None = None):
        return await self.logic.get_telegram(tg_id)

    async def search_users(
        self,
        user_id: int | None = None,
        tg_id: int | None = None,
        username: str | None = None,
        name: str | None = None,
        page: int | None = None,
        per_page: int = 5,
    ):
        return await self.logic.search_users(user_id, tg_id, username, name, page, per_page)

    async def list_users(
        self,
        page: int | None = None,
        per_page: int = 5,
        ):
        return await self.logic.list_users(page, per_page)

    async def delete_user(self, user_id: int):
        return await self.logic.delete_user(user_id)
