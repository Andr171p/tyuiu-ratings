from typing import Literal

from pathlib import Path


# Директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent.parent

ENV_PATH = BASE_DIR / ".env"  # Переменные окружения


# Минимальное и максимальное количество баллов ЕГЭ:
MIN_POINTS = 0
MAX_POINTS = 310

# Минимальное и максимальное количество дополнительных баллов:
MIN_BONUS_POINTS = 0
MAX_BONUS_POINTS = 10

# Минимальное и максимальное значение среднего балла аттестата:
MIN_GPA = 3
MAX_GPA = 5

# Минимальное и максимальное количество баллов ЕГЭ за один предмет:
MIN_EXAM_POINTS = 0
MAX_EXAM_POINTS = 100

# Минимальное и максимальное значение приоритета:
MIN_PRIORITY = 1
MAX_PRIORITY = 5

# Возможные экзамены ЕГЭ:
AVAILABLE_SUBJECTS = Literal[
    "Русский язык",
    "Математика",
    "Информатика",
    "Физика",
    "Обществознание",
    "Химия",
    "История"
]

# Количество бюджетных мест на направления подготовки:
BUDGET_PLACES_FOR_DIRECTIONS = {
    "": ...
}

# Значения по умолчанию:
PREDICTED_YEAR = 2024
DEFAULT_GPA = 4.2
DEFAULT_GENDER = "male"


# Направления подготовки:
AVAILABLE_DIRECTIONS = Literal[""]

# Маппинг направлений подготовки:
DIRECTIONS_MAPPING_CSV = BASE_DIR / "file_store" / "directions_mapping_2025.csv"

# Уровни уведомлений абитуриентам:
NOTIFICATION_LEVELS = Literal[
    "INFO",  # Уведомления информационного характера
    "POSITIVE",  # Несущие положительный характер (проход на бюджет, зачисление, начисление доп-баллов)
    "WARNING",  # Предупреждения (абитуриент значительно опустился в рейтинге)
    "CRITICAL"  # Критический уровень (больше не проходит на бюджет -> дать рекомендации)
]

# Пагинация:
MIN_PAGE = 1
DEFAULT_LIMIT = 100

# Пороговые значения:
POSITIVE_THRESHOLD_PROBABILITY = 0.75
CRITICAL_THRESHOLD_PROBABILITY = 0.15
THRESHOLD_VELOCITY = -10
BUDGET_ZONE_THRESHOLD = 5
