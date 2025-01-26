# utils/logging_utils.py
import logging
import os

def setup_logger(name: str, log_file: str = None, level: int = logging.INFO) -> logging.Logger:
    """
    Настройка логгера для проекта.

    Args:
        name (str): Имя логгера (обычно __name__).
        log_file (str): Путь к файлу для сохранения логов. Если None, логи выводятся только в консоль.
        level (int): Уровень логирования (например, logging.INFO).

    Returns:
        logging.Logger: Настроенный логгер.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Убедимся, что логгер не дублирует обработчики
    if logger.hasHandlers():
        logger.handlers.clear()

    # Формат логов с дополнительной информацией
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]'
    )

    # Консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Файловый обработчик (опционально)
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

# Пример использования
if __name__ == "__main__":
    log = setup_logger("test_logger", "logs/test.log")
    log.info("Это тестовое сообщение.")
