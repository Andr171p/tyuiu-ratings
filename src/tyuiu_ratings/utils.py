from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .core.domain import Rank

import pandas as pd

from .constants import DIRECTIONS_MAPPING_CSV


def calculate_pages(total_count: int, limit: int) -> int:
    pages = total_count // limit
    return pages


def calculate_velocity(history: list["Rank"]) -> list[float]:
    df = pd.DataFrame([rank.model_dump() for rank in history])
    df.set_index("date", inplace=True)
    df["rating_change"] = df["rating"].diff().fillna(0)
    return -df["rating_change"].to_list()


def calculate_mean_velocity(history: list["Rank"]) -> float:
    df = pd.DataFrame([rank.model_dump() for rank in history])
    df.set_index("date", inplace=True)
    df["rating_change"] = df["rating"].diff().fillna(0)
    return -df["rating_change"].mean()


def calculate_acceleration(history: list["Rank"]) -> list[float]:
    df = pd.DataFrame([rank.model_dump() for rank in history])
    df.set_index("date", inplace=True)
    df["rating_change"] = df["rating"].diff().fillna(0)
    df["acceleration"] = -df["rating_change"].diff()
    return df["acceleration"].fillna(0).to_list()


def calculate_stability(history: list["Rank"]) -> float:
    df = pd.DataFrame([rank.model_dump() for rank in history])
    df.set_index("date", inplace=True)
    return df["rating"].std()


def mapping_direction(direction: str) -> Optional[str]:
    df = pd.read_csv(DIRECTIONS_MAPPING_CSV)
    idx = df.index[df["Направление подготовки 2025"] == direction].tolist()
    return df.loc[idx[0], "Направление подготовки"] if idx else None
