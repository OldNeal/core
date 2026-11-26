from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import Literal
from app.validate.api.base import QueryBody, AnswerBaseInfo, QueryUserUpdate, AnswerUserBody, AnswerUsersBody
from app.api.endpoints.beyonder import beyonder_router
from app.api.endpoints.wiki import wiki_router
from app.api.endpoints.stats import stats_router
from app.api.endpoints.activity import activity_router
from app.api.endpoints.organ import organ_router
from app.api.endpoints.newspaper import news_paper_router
from app.api.endpoints.logs import logs_router
from app.api.endpoints.player import player_router
from app.api.endpoints.item import item_router
from app.service.main import MainService
from app.api.depends.session import get_session
from app.exception import get_exception_codes
from app.validate.api.user import AnswerUserSetting, AnswerUserSettingValues, QueryUserSetting, QueryUserSettingDefault
from app.logic.setting.base import SETTING_METADATA
from app.validate.logic.setting import SettingParametrMetadata

base_router = APIRouter()

main_router = APIRouter(prefix='', tags=['main'], responses=get_exception_codes(types=[]))

@main_router.get('/settings/name', response_model=SettingParametrMetadata)
async def setting_name(
    setting_type: Literal['user', 'organ', 'news_paper'] = Query(alias='type', description='Тип настроек'),
    tag: str = Query(description='Тег параметра настройки'),
):
    metadata = SETTING_METADATA['types'].get(setting_type, {}).get(tag)
    if metadata is None:
        raise HTTPException(status_code=404, detail='Параметр настройки не найден')
    return SettingParametrMetadata.model_validate(metadata)

user_router = APIRouter(prefix='/user', tags=['user'], responses=get_exception_codes(types=['setting']))

@user_router.post('/settings', response_model=AnswerUserSetting)
async def user_settings(query: QueryBody, session=Depends(get_session())):
    return await MainService(session, query.user_id).settings()

@user_router.post('/settings/values', response_model=AnswerUserSettingValues)
async def user_settings_values(query: QueryBody, session=Depends(get_session())):
    return await MainService(session, query.user_id).settings_values()

@user_router.patch('/settings/redact', response_model=AnswerUserSetting)
async def user_settings_redact(query: QueryUserSetting, session=Depends(get_session())):
    return await MainService(session, query.user_id).settings_redact(query.parametrs)

@user_router.patch('/settings/default', response_model=AnswerUserSetting)
async def user_settings_default(query: QueryUserSettingDefault, session=Depends(get_session())):
    return await MainService(session, query.user_id).settings_default(query.to_default)

@main_router.get('/info', response_model=AnswerBaseInfo)
async def get_info(
                   user_id: int = Query(description='ID пользователя'),
                   session = Depends(get_session())
                   ):
    return await MainService(session, purpose_user_id=user_id).info()

@main_router.put('/user/update', response_model=AnswerUserBody)
async def user_new(
                   query: QueryUserUpdate, 
                   session = Depends(get_session())
                   ):
    return await MainService(session).update(query)

@main_router.get('/user', response_model=AnswerUserBody)
async def user_telegram(
                   user_id: int = Query(None, description='ID пользователя'),
                   tg_id: int = Query(None, description='Telegram ID пользователя'),
                   session = Depends(get_session())
                   ):
    return await MainService(session, purpose_user_id=user_id).get_telegram(tg_id)

@main_router.get('/user/search', response_model=AnswerUsersBody)
async def user_search(
                   user_id: int | None = Query(None, description='ID пользователя'),
                   tg_id: int | None = Query(None, description='Telegram ID пользователя'),
                   username: str | None = Query(None, description='Telegram username'),
                   name: str | None = Query(None, description='Обычное имя пользователя'),
                   page: int | None = Query(None, ge=0, description='Номер страницы'),
                   per_page: int = Query(5, ge=1, description='Результатов на странице'),
                   session = Depends(get_session())
                   ):
    return await MainService(session).search_users(user_id, tg_id, username, name, page, per_page)

@main_router.get('/user/list', response_model=AnswerUsersBody)
async def user_list(
                   page: int | None = Query(None, ge=0, description='Номер страницы'),
                   per_page: int = Query(5, ge=1, description='Результатов на странице'),
                   session = Depends(get_session())
                   ):
    return await MainService(session).list_users(page, per_page)

@main_router.patch('/user/delete', response_model=AnswerUserBody)
async def user_delete(
                   query: QueryBody,
                   user_id: int = Query(description='ID пользователя'),
                   session = Depends(get_session())
                   ):
    return await MainService(
        session,
        user_id=query.user_id,
        is_admin=query.is_admin,
    ).delete_user(user_id)

base_router.include_router(main_router)
base_router.include_router(user_router)
base_router.include_router(activity_router)
base_router.include_router(beyonder_router)
base_router.include_router(organ_router)
base_router.include_router(player_router)
base_router.include_router(item_router)
base_router.include_router(news_paper_router)
base_router.include_router(wiki_router)
base_router.include_router(stats_router)
base_router.include_router(logs_router)
