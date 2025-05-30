from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .core.domain import RatingPosition

import pandas as pd

from .constants import DIRECTIONS_MAPPING_CSV


def calculate_pages(total_count: int, limit: int) -> int:
    """Рассчитывает количество страниц для пагинации"""
    pages = total_count // limit
    return pages


def calculate_velocity(history: list["RatingPosition"]) -> list[float]:
    """Вычисляет изменения позиций в рейтинге"""
    df = pd.DataFrame([rank.model_dump() for rank in history])
    df.set_index("date", inplace=True)
    df["rating_change"] = df["rating"].diff().fillna(0)
    return -df["rating_change"].to_list()


def calculate_mean_velocity(history: list["RatingPosition"]) -> float:
    """Вычисляет среднее изменение в позиции в рейтинге"""
    df = pd.DataFrame([rank.model_dump() for rank in history])
    df.set_index("date", inplace=True)
    df["rating_change"] = df["rating"].diff().fillna(0)
    return -df["rating_change"].mean()


def calculate_acceleration(history: list["RatingPosition"]) -> list[float]:
    """Вычисляет скорость изменений позиций в рейтинге"""
    df = pd.DataFrame([rank.model_dump() for rank in history])
    df.set_index("date", inplace=True)
    df["rating_change"] = df["rating"].diff().fillna(0)
    df["acceleration"] = -df["rating_change"].diff()
    return df["acceleration"].fillna(0).to_list()


def calculate_stability(history: list["RatingPosition"]) -> float:
    """Вычисляет стабильность изменений в рейтинге"""
    df = pd.DataFrame([rank.model_dump() for rank in history])
    df.set_index("date", inplace=True)
    return df["rating"].std()


def is_rating_stable(history: list["RatingPosition"], days_count: int, max_change: int) -> bool:
    """Проверяет стабильность позиции в рейтинге за N-ое количество дней """
    df = pd.DataFrame([rank.model_dump() for rank in history])
    df.set_index("date", inplace=True)
    cutoff_date = df.index.max() - pd.Timedelta(days=days_count)
    last_days = df[df.index >= cutoff_date]
    if len(last_days) < 2:
        return True
    changes = last_days["rating"].diff().abs().dropna()
    return changes.max() <= max_change


def mapping_direction(direction: str) -> Optional[str]:
    df = pd.read_csv(DIRECTIONS_MAPPING_CSV)
    idx = df.index[df["Направление подготовки 2025"] == direction].tolist()
    return df.loc[idx[0], "Направление подготовки"] if idx else None
