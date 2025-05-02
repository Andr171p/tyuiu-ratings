from datetime import datetime

from pydantic import BaseModel

from ..entities.admission import Profile


class ProfileReadDTO(Profile):
    created_at: datetime
    updated_at: datetime
