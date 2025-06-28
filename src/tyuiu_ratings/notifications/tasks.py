import logging

import pytz

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from dishka import Scope

from .use_cases import BroadcastNotificationsUseCase

from ..ioc import container
from ..constants import CURRENT_TIMEZONE, BROADCAST_HOURS, BROADCAST_MINUTES

logger = logging.getLogger(__name__)


async def broadcast_notifications_task() -> None:
    """Задача для рассылки уведомлений абитуриентам"""
    async with container(scope=Scope.REQUEST) as request_container:
        broadcast_notifications_use_case = await request_container.get(BroadcastNotificationsUseCase)
        try:
            await broadcast_notifications_use_case()
        except Exception as e:
            logger.error(f"Error while broadcasts notifications: {e}")


def create_scheduler_app() -> AsyncIOScheduler:
    timezone = pytz.timezone(CURRENT_TIMEZONE)
    scheduler = AsyncIOScheduler(timezone=timezone)
    scheduler.add_job(
        broadcast_notifications_task,
        CronTrigger(hour=BROADCAST_HOURS, minute=BROADCAST_MINUTES, timezone=timezone)
    )
    return scheduler
