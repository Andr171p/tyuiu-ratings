from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .ratings.schemas import Rating

import pandas as pd

from .constants import DIRECTIONS_MAPPING_CSV


def calculate_pages(total_count: int, limit: int) -> int:
    """Рассчитывает количество страниц для пагинации"""
    pages = total_count // limit
    return pages


def calculate_velocity(ratings: list["Rating"]) -> list[float]:
    """Вычисляет изменения позиций в рейтинге"""
    df = pd.DataFrame([rating.model_dump() for rating in ratings])
    df.set_index("date", inplace=True)
    df["rank_change"] = df["rank"].diff().fillna(0)
    return -df["rank_change"].to_list()


def calculate_mean_velocity(ratings: list["Rating"]) -> float:
    """Вычисляет среднее изменение в позиции в рейтинге"""
    df = pd.DataFrame([rating.model_dump() for rating in ratings])
    df.set_index("date", inplace=True)
    df["rank_change"] = df["rank"].diff().fillna(0)
    return -df["rank_change"].mean()


def calculate_acceleration(ratings: list["Rating"]) -> list[float]:
    """Вычисляет скорость изменений позиций в рейтинге"""
    df = pd.DataFrame([rating.model_dump() for rating in ratings])
    df.set_index("date", inplace=True)
    df["rank_change"] = df["rank"].diff().fillna(0)
    df["acceleration"] = -df["rank_change"].diff()
    return df["acceleration"].fillna(0).to_list()


def calculate_stability(ratings: list["Rating"]) -> float:
    """Вычисляет стабильность изменений в рейтинге"""
    df = pd.DataFrame([rating.model_dump() for rating in ratings])
    df.set_index("date", inplace=True)
    return df["rank"].std()


def is_rating_stable(ratings: list["Rating"], days_count: int, max_change: int) -> bool:
    """Проверяет стабильность позиции в рейтинге за N-ое количество дней """
    df = pd.DataFrame([rating.model_dump() for rating in ratings])
    df.set_index("date", inplace=True)
    cutoff_date = df.index.max() - pd.Timedelta(days=days_count)
    last_days = df[df.index >= cutoff_date]
    if len(last_days) < 2:
        return True
    changes = last_days["rank"].diff().abs().dropna()
    return changes.max() <= max_change


def mapping_direction(direction: str) -> Optional[str]:
    df = pd.read_csv(DIRECTIONS_MAPPING_CSV)
    idx = df.index[df["Направление подготовки 2025"] == direction].tolist()
    return df.loc[idx[0], "Направление подготовки"] if idx else None
