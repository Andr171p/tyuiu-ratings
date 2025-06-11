from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

import pytz

from ..ioc import container
from ..constants import CURRENT_TIMEZONE, BROADCAST_HOURS, BROADCAST_MINUTES
from ..core.use_cases.notification import BroadcastNotificationsUseCase


async def broadcast_notifications_task() -> None:
    """Задача для рассылки уведомлений абитуриентам"""
    broadcast_notifications_use_case = await container.get(BroadcastNotificationsUseCase)
    await broadcast_notifications_use_case.broadcast()


def create_scheduler_app() -> AsyncIOScheduler:
    timezone = pytz.timezone(CURRENT_TIMEZONE)
    scheduler = AsyncIOScheduler(timezone=timezone)
    scheduler.add_job(
        broadcast_notifications_task,
        CronTrigger(hour=BROADCAST_HOURS, minute=BROADCAST_MINUTES, timezone=timezone)
    )
    return scheduler
