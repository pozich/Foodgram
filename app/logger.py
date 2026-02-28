# app/logger.py
import logging
import sys

def setup_logging():
    # Все, что ниже, должно быть строго под функцией
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=logging.INFO, 
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )

    # Настройки уровней для библиотек
    logging.getLogger("aiogram").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    logging.info("🌲 Система логирования успешно инициализирована")
