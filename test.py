import csv
import random
import asyncio

from faststream.rabbit import RabbitBroker

from src.tyuiu_ratings.applicant.dto import ApplicantUpdateEvent
from src.tyuiu_ratings.applicant.schemas import Applicant
from src.tyuiu_ratings.constants import DIRECTIONS_MAPPING_CSV

from src.tyuiu_ratings.settings import RabbitSettings


def get_directions_from_csv(file_path = DIRECTIONS_MAPPING_CSV):
    directions = []
    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            directions.append(row["Направление подготовки 2025"])
    return directions


DIRECTIONS = get_directions_from_csv()

INSTITUTES = [
    "Институт информационных технологий",
    "Институт нефти и газа",
    "Строительный институт",
    "Институт экономики и управления",
    "Химико-технологический институт"
]


def generate_random_applicant(applicant_id: int) -> ApplicantUpdateEvent:
    """Генерация одного случайного абитуриента"""
    return Applicant(
        applicant_id=applicant_id,
        rank=random.randint(1, 1000),
        institute=random.choice(INSTITUTES),
        direction=random.choice(DIRECTIONS),
        priority=random.randint(1, 5),
        points=random.randint(100, 310),  # Минимальный порог 100 баллов
        bonus_points=random.randint(0, 10),
        original=random.choice([True, False])
    )


def generate_applicants(count: int = 1000) -> list[ApplicantUpdateEvent]:
    """Генерация списка абитуриентов"""
    return [generate_random_applicant(i) for i in range(1, count + 1)]

# Генерация 1000 абитуриентов
applicants = generate_applicants(1000)
print(dict(applicants[0].model_dump()))

async def main() -> None:
    broker = RabbitBroker(RabbitSettings().rabbit_url)
    await broker.start()
    await broker.publish(applicants, queue="applicants")
    await broker.close()


# Пример использования
if __name__ == "__main__":
    asyncio.run(main())
    ...
    # from src.tyuiu_ratings.utils import mapping_direction
    # print(mapping_direction('27.03.01 Стандартизация и метрология (Стандартизация, метрология и управление качеством в отраслях топливно-энергетического комплекса); 27.03.05 Инноватика (Управление инновациями в промышленности (машиностроение))'))
