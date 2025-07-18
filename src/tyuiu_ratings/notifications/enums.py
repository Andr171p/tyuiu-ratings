from enum import StrEnum


class NotificationLevel(StrEnum):
    INFO = "INFO"          # Уведомления информационного характера
    POSITIVE = "POSITIVE"  # Несущие положительный характер (проход на бюджет, зачисление, начисление доп-баллов)
    WARNING = "WARNING"    # Предупреждения (абитуриент значительно опустился в рейтинге)
    CRITICAL = "CRITICAL"  # Критический уровень (больше не проходит на бюджет -> дать рекомендации)
