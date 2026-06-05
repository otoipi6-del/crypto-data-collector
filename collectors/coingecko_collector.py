"""
CoinGecko API Collector
Собирает: цены, капитализация, объёмы, исторические данные, тренды
"""
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from base_collector import BaseCollector

logger = logging.getLogger(__name__)


class CoinGeckoCollector(BaseCollector):
    """Коллектор данных из CoinGecko API"""

    def __init__(self, api_key: str = None):
        config = {
            "base_url": "https://api.coingecko.com/api/v3",
            "rate_limit": 100,  # calls per minute (free tier)
            "api_key": api_key
        }
        super().__init__("coingecko", config)
        self.rate_limit_delay = 0.6  # 100 calls/min = 0.6s between calls
        self.headers = {}
        if api_key:
            self.headers["x-cg-demo-api-key"] = api_key

    async def fetch(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """Выполнение API-запроса"""
        await self._rate_limit()

        url = f"{self.config['base_url']}{endpoint}"

        async with self.session.get(url, params=params, headers=self.headers) as response:
            if response.status == 429:
                logger.warning("⚠️ Rate limit достигнут, ожидание...")
                await asyncio.sleep(60)
                return await self.fetch(endpoint, params)

            response.raise_for_status()
            return await response.json()

    async def get_coins_list(self) -> List[Dict]:
        """Получить список всех монет"""
        return await self.fetch("/coins/list")

    async def get_market_data(self, vs_currency: str = "usd", 
                             per_page: int = 100, page: int = 1) -> List[Dict]:
        """Рыночные данные топ-монет"""
        params = {
            "vs_currency": vs_currency,
            "order": "market_cap_desc",
            "per_page": per_page,
            "page": page,
            "sparkline": "false",
            "price_change_percentage": "24h,7d,30d"
        }
        return await self.fetch("/coins/markets", params)

    async def get_coin_data(self, coin_id: str) -> Dict:
        """Детальные данные по монете"""
        params = {
            "localization": "false",
            "tickers": "false",
            "market_data": "true",
            "community_data": "true",
            "developer_data": "true"
        }
        return await self.fetch(f"/coins/{coin_id}", params)

    async def get_global_data(self) -> Dict:
        """Глобальные рыночные метрики"""
        return await self.fetch("/global")

    async def get_trending(self) -> Dict:
        """Трендовые монеты"""
        return await self.fetch("/search/trending")

    async def get_categories(self) -> List[Dict]:
        """Категории криптоактивов"""
        return await self.fetch("/coins/categories")

    async def get_derivatives(self) -> List[Dict]:
        """Данные по деривативным биржам"""
        return await self.fetch("/derivatives/exchanges")

    async def get_nfts(self, per_page: int = 100, page: int = 1) -> List[Dict]:
        """Список NFT коллекций"""
        params = {"per_page": per_page, "page": page}
        return await self.fetch("/nfts/list", params)

    async def get_all_data(self) -> Dict[str, Any]:
        """Сбор всех основных данных"""
        logger.info("🚀 Начинаем сбор данных из CoinGecko...")

        data = {
            "timestamp": datetime.now().isoformat(),
            "source": "coingecko",
            "global": {},
            "top_coins": [],
            "trending": [],
            "categories": [],
            "derivatives": []
        }

        try:
            # Глобальные метрики
            data["global"] = await self.get_global_data()
            logger.info("✅ Глобальные данные получены")

            # Топ-100 монет
            data["top_coins"] = await self.get_market_data(per_page=100)
            logger.info(f"✅ Получены данные по {len(data['top_coins'])} монетам")

            # Тренды
            trending = await self.get_trending()
            data["trending"] = trending.get("coins", [])
            logger.info(f"✅ Трендовые монеты: {len(data['trending'])}")

            # Категории
            data["categories"] = await self.get_categories()
            logger.info(f"✅ Категорий: {len(data['categories'])}")

            # Деривативы
            data["derivatives"] = await self.get_derivatives()
            logger.info(f"✅ Деривативных бирж: {len(data['derivatives'])}")

        except Exception as e:
            logger.error(f"❌ Ошибка при сборе данных: {e}")

        return data


# Пример использования:
# async with CoinGeckoCollector() as collector:
#     data = await collector.get_all_data()
#     collector.save_data(data, "coingecko_full.json")
