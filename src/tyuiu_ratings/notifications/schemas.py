from typing import Optional

from uuid import UUID

from pydantic import BaseModel

from ..constants import NOTIFICATION_LEVEL


class Notification(BaseModel):
    """Уведомление для абитуриента"""
    level: NOTIFICATION_LEVEL
    user_id: UUID
    photo: Optional[str] = None  # Картинка в формате base64
    text: str
