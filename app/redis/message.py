from app.redis.base import BaseHashs, BaseStore
from config import settings as global_settings


class MessageHashs(BaseHashs):
    GET_ACTIVITY_POINT = 'message:telegram:notify:get-activity-point'
    ITEM = 'message:telegram:notify:item:{action}'
    ORGAN = 'message:telegram:notify:organ:{action}'

    @classmethod
    def organ(cls, action: str):
        if action not in {'rank', 'titul', 'kick', 'give'}:
            raise ValueError('Unknown organization notification action')
        return cls.ORGAN.format(action=action)

    @classmethod
    def item(cls, action: str):
        if action not in {'give', 'take'}:
            raise ValueError("action must be 'give' or 'take'")
        return cls.ITEM.format(action=action)


class MessageStore(BaseStore):
    hashs_cls = MessageHashs
    hashs: type[MessageHashs]

    async def save_activity_point_notification(
        self,
        tg_id: int,
        user_id: int,
        points: int,
        reason: str,
        settings: dict,
    ):
        if not self._notifications_enabled(
            settings,
            'notify_activity_points',
            global_settings.TELEGRAM_NOTIFY_ACTIVITY_POINTS,
        ):
            return 0
        return await self.client.hset(
            self.hashs_cls.GET_ACTIVITY_POINT,
            mapping={
                'tg_id': tg_id,
                'user_id': user_id,
                'points': points,
                'reason': reason,
            },
        )

    async def save_item_notification(
        self,
        action: str,
        tg_id: int,
        user_id: int,
        item_id: int,
        quantity: int,
        remaining: int,
        settings: dict,
        item_name: str,
        item_emodzi: str | None = None,
    ):
        global_enabled = {
            'give': global_settings.TELEGRAM_NOTIFY_ITEM_GIVE,
            'take': global_settings.TELEGRAM_NOTIFY_ITEM_TAKE,
        }[action]
        if not self._notifications_enabled(
            settings,
            f'notify_item_{action}',
            global_enabled,
        ):
            return 0
        return await self.client.hset(
            self.hashs_cls.item(action),
            mapping={
                'tg_id': tg_id,
                'user_id': user_id,
                'item_id': item_id,
                'item_name': item_name,
                'item_emodzi': item_emodzi or '',
                'quantity': quantity,
                'remaining': remaining,
            },
        )

    async def save_organ_notification(
        self, action: str, tg_id: int | None, user_id: int,
        actor_id: int, actor_name: str | None, organ_id: int,
        organ_name: str, settings: dict, old_value=None, new_value=None,
    ):
        key = self.hashs_cls.organ(action)
        if tg_id is None or not self._notifications_enabled(
            settings, 'notify_organ', global_settings.TELEGRAM_NOTIFY_ORGAN,
        ):
            return 0
        return await self.client.hset(key, mapping={
            'tg_id': tg_id,
            'user_id': user_id,
            'actor_id': actor_id,
            'actor_name': actor_name or '',
            'organ_id': organ_id,
            'organ_name': organ_name,
            'old_value': '' if old_value is None else str(old_value),
            'new_value': '' if new_value is None else str(new_value),
        })

    @staticmethod
    def _notifications_enabled(
        account_settings: dict,
        notification_type: str,
        globally_enabled: bool,
    ) -> bool:
        return (
            global_settings.TELEGRAM_NOTIFICATIONS_ENABLED
            and globally_enabled
            and account_settings.get('get_notify', True)
            and account_settings.get(notification_type, True)
        )
