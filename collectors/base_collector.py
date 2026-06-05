"""
Базовый класс для всех коллекторов данных (API и парсинг)
"""
import asyncio
import aiohttp
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseCollector(ABC):
    """Базовый класс для сбора данных из любого источника"""

    def __init__(self, source_name: str, config: Dict[str, Any]):
        self.source_name = source_name
        self.config = config
        self.session = None
        self.rate_limit_delay = 1.0  # секунд между запросами
        self.last_request_time = None
        self.data_cache = {}

    async def __aenter__(self):
        """Асинхронный контекстный менеджер"""
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрытие сессии"""
        if self.session:
            await self.session.close()

    async def _rate_limit(self):
        """Контроль частоты запросов"""
        if self.last_request_time:
            elapsed = (datetime.now() - self.last_request_time).total_seconds()
            if elapsed < self.rate_limit_delay:
                await asyncio.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = datetime.now()

    @abstractmethod
    async def fetch(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """Основной метод получения данных"""
        pass

    @abstractmethod
    async def get_all_data(self) -> Dict[str, Any]:
        """Получение всех доступных данных из источника"""
        pass

    def save_data(self, data: Dict[str, Any], filename: str = None):
        """Сохранение данных в JSON"""
        if not filename:
            filename = f"{self.source_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        filepath = f"outputs/{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"💾 Данные сохранены: {filepath}")
        return filepath

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Валидация полученных данных"""
        return bool(data) and isinstance(data, (dict, list))

    async def retry_fetch(self, endpoint: str, params: Dict = None, 
                         max_retries: int = 3) -> Optional[Dict]:
        """Повторные попытки при ошибках"""
        for attempt in range(max_retries):
            try:
                result = await self.fetch(endpoint, params)
                if self.validate_data(result):
                    return result
            except Exception as e:
                logger.warning(f"⚠️ Попытка {attempt + 1}/{max_retries} не удалась: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Экспоненциальная задержка

        logger.error(f"❌ Все попытки для {endpoint} исчерпаны")
        return None
