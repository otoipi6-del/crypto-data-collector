"""
Nansen API Collector
Собирает: Smart Money, wallet profiles, token screener
"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from base_collector import BaseCollector

logger = logging.getLogger(__name__)


class NansenCollector(BaseCollector):
    """Коллектор данных Nansen (требует API ключ)"""

    def __init__(self, api_key: str):
        config = {
            "base_url": "https://api.nansen.ai",
            "api_key": api_key,
            "rate_limit": 100,  # depends on plan
        }
        super().__init__("nansen", config)
        self.rate_limit_delay = 0.6
        self.headers = {"Authorization": f"Bearer {api_key}"}

    async def fetch(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        await self._rate_limit()
        url = f"{self.config['base_url']}{endpoint}"
        async with self.session.get(url, params=params, headers=self.headers) as response:
            response.raise_for_status()
            return await response.json()

    async def get_wallet_profile(self, address: str) -> Dict:
        """Профиль кошелька"""
        return await self.fetch(f"/v2/wallets/{address}/profile")

    async def get_token_screener(self, filters: Dict = None) -> Dict:
        """Скринер токенов"""
        return await self.fetch("/v2/tokens/screener", filters)

    async def get_smart_money_flows(self) -> Dict:
        """Потоки Smart Money"""
        return await self.fetch("/v2/smart-money/flows")

    async def get_all_data(self, sample_address: str = None) -> Dict[str, Any]:
        logger.info("🚀 Собираем данные из Nansen...")

        data = {
            "timestamp": datetime.now().isoformat(),
            "source": "nansen",
            "wallet_profile": {},
            "token_screener": {},
            "smart_money": {}
        }

        try:
            if sample_address:
                data["wallet_profile"] = await self.get_wallet_profile(sample_address)
                logger.info("✅ Профиль кошелька получен")

            data["token_screener"] = await self.get_token_screener()
            logger.info("✅ Данные скринера получены")

            data["smart_money"] = await self.get_smart_money_flows()
            logger.info("✅ Smart Money потоки получены")

        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")

        return data
