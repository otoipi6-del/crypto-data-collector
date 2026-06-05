"""
DeFi Llama API Collector
Собирает: TVL, revenue, fees, yields, stablecoins, chain metrics
"""
import asyncio
from typing import Dict, List, Any
from datetime import datetime
import logging

from base_collector import BaseCollector

logger = logging.getLogger(__name__)


class DeFiLlamaCollector(BaseCollector):
    """Коллектор данных из DeFi Llama API (бесплатный)"""

    def __init__(self):
        config = {
            "base_url": "https://api.llama.fi",
            "rate_limit": 0,  # no limit for open API
        }
        super().__init__("defillama", config)
        self.rate_limit_delay = 0.1  # небольшая задержка на всякий случай

    async def fetch(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """Выполнение API-запроса"""
        await self._rate_limit()

        url = f"{self.config['base_url']}{endpoint}"

        async with self.session.get(url, params=params) as response:
            response.raise_for_status()
            return await response.json()

    async def get_protocols(self) -> List[Dict]:
        """Список всех протоколов с TVL"""
        return await self.fetch("/protocols")

    async def get_protocol_data(self, protocol: str) -> Dict:
        """Детальные данные по протоколу"""
        return await self.fetch(f"/protocol/{protocol}")

    async def get_chains(self) -> List[Dict]:
        """Список чейнов с TVL"""
        return await self.fetch("/chains")

    async def get_global_tvl(self) -> float:
        """Глобальный TVL"""
        data = await self.fetch("/charts")
        if data and len(data) > 0:
            return data[-1].get("totalLiquidityUSD", 0)
        return 0

    async def get_stablecoins(self) -> Dict:
        """Данные по стейблкоинам"""
        return await self.fetch("/stablecoins")

    async def get_yields(self) -> List[Dict]:
        """Данные по доходности (yields)"""
        return await self.fetch("/yields")

    async def get_fees_revenue(self) -> Dict:
        """Данные по fees и revenue"""
        return await self.fetch("/overview/fees")

    async def get_all_data(self) -> Dict[str, Any]:
        """Сбор всех основных данных"""
        logger.info("🚀 Начинаем сбор данных из DeFi Llama...")

        data = {
            "timestamp": datetime.now().isoformat(),
            "source": "defillama",
            "protocols": [],
            "chains": [],
            "global_tvl": 0,
            "stablecoins": {},
            "yields": [],
            "fees_revenue": {}
        }

        try:
            data["protocols"] = await self.get_protocols()
            logger.info(f"✅ Протоколов: {len(data['protocols'])}")

            data["chains"] = await self.get_chains()
            logger.info(f"✅ Чейнов: {len(data['chains'])}")

            data["global_tvl"] = await self.get_global_tvl()
            logger.info(f"✅ Глобальный TVL: ${data['global_tvl']:,.0f}")

            data["stablecoins"] = await self.get_stablecoins()
            logger.info("✅ Данные по стейблкоинам получены")

            data["yields"] = await self.get_yields()
            logger.info(f"✅ Yield opportunities: {len(data['yields'])}")

            data["fees_revenue"] = await self.get_fees_revenue()
            logger.info("✅ Fees/Revenue данные получены")

        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")

        return data
