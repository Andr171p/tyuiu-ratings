__all__ = (
    "profiles_router",
    "applicants_router",
    "rating_history_router",
    "competition_lists_router"
)

from .profiles import profiles_router
from .applicants import applicants_router
from .rating_history import rating_history_router
from .competition_lists import competition_lists_router
