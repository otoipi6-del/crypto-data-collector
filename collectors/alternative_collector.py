"""
Alternative.me API Collector
Собирает: Fear & Greed Index
"""
from typing import Dict, Any
from datetime import datetime
import logging

from base_collector import BaseCollector

logger = logging.getLogger(__name__)


class AlternativeMeCollector(BaseCollector):
    """Коллектор Fear & Greed Index"""

    def __init__(self):
        config = {
            "base_url": "https://api.alternative.me",
            "rate_limit": 0,
        }
        super().__init__("alternative_me", config)
        self.rate_limit_delay = 0.1

    async def fetch(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        await self._rate_limit()
        url = f"{self.config['base_url']}{endpoint}"
        async with self.session.get(url, params=params) as response:
            response.raise_for_status()
            return await response.json()

    async def get_fear_greed(self, limit: int = 30) -> Dict:
        """Получить Fear & Greed Index"""
        params = {"limit": limit, "format": "json"}
        return await self.fetch("/fng/", params)

    async def get_all_data(self) -> Dict[str, Any]:
        logger.info("🚀 Собираем Fear & Greed Index...")

        data = {
            "timestamp": datetime.now().isoformat(),
            "source": "alternative_me",
            "fear_greed": {}
        }

        try:
            fg_data = await self.get_fear_greed(limit=30)
            data["fear_greed"] = fg_data

            if "data" in fg_data and len(fg_data["data"]) > 0:
                current = fg_data["data"][0]
                logger.info(f"✅ Текущий F&G: {current.get('value')} ({current.get('value_classification')})")
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")

        return data
