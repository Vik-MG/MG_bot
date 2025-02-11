# handlers/__init__.py
from aiogram import Router
from core.utils.logging_utils import setup_logger
from .manager import router as manager_router
from .start import router as start_router
from .client_type import router as client_type_router
from .retail import router as retail_router
from .wholesale import router as wholesale_router
from .contacts import router as contacts_router

# Настройка логгера
logger = setup_logger(__name__)

def register_all_handlers(router: Router):
    """Регистрация всех обработчиков через роутеры."""
    try:
        router.include_router(manager_router)
        logger.info("Обработчик manager зарегистрирован.")
        
        router.include_router(start_router)
        logger.info("Обработчик start зарегистрирован.")

        router.include_router(client_type_router)
        logger.info("Обработчик client_type зарегистрирован.")
        
        router.include_router(retail_router)
        logger.info("Обработчик retail зарегистрирован.")
        
        router.include_router(wholesale_router)
        logger.info("Обработчик wholesale зарегистрирован.")
        
        router.include_router(contacts_router)
        logger.info("Обработчик contacts зарегистрирован.")
    except Exception as e:
        logger.error(f"Ошибка при регистрации обработчиков: {e}", exc_info=True)
        raise
