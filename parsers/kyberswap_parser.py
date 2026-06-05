"""
KyberSwap Discover Parser
Собирает: trending tokens, trending soon, DEX метрики
"""
import asyncio
from typing import Dict, List, Any
from datetime import datetime
import logging

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class KyberSwapParser:
    """Парсер KyberSwap Discover"""

    def __init__(self, proxy: str = None):
        self.base_url = "https://kyberswap.com/discover"
        self.proxy = proxy
        self.browser = None

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        browser_args = {
            "headless": True,
            "args": ["--no-sandbox", "--disable-blink-features=AutomationControlled"]
        }
        if self.proxy:
            browser_args["proxy"] = {"server": self.proxy}

        self.browser = await self.playwright.chromium.launch(**browser_args)
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
        self.page = await self.context.new_page()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def parse_trending(self, tab: str = "trending") -> List[Dict]:
        """Парсинг trending tokens"""
        logger.info(f"🔥 Парсим {tab} tokens...")

        url = f"{self.base_url}?tab={tab}"
        await self.page.goto(url, wait_until="networkidle")
        await asyncio.sleep(3)

        content = await self.page.content()
        soup = BeautifulSoup(content, 'html.parser')

        tokens = []

        # Ищем карточки токенов
        cards = soup.find_all(['div', 'tr'], class_=lambda x: x and 'token' in str(x).lower())

        for card in cards[:50]:
            try:
                symbol = card.find(['span', 'div'], class_=lambda x: x and 'symbol' in str(x).lower())
                name = card.find(['span', 'div'], class_=lambda x: x and 'name' in str(x).lower())
                price = card.find(['span', 'div'], class_=lambda x: x and 'price' in str(x).lower())
                change = card.find(['span', 'div'], class_=lambda x: x and 'change' in str(x).lower())
                volume = card.find(['span', 'div'], class_=lambda x: x and 'volume' in str(x).lower())

                if symbol:
                    tokens.append({
                        "symbol": symbol.get_text(strip=True),
                        "name": name.get_text(strip=True) if name else "",
                        "price": price.get_text(strip=True) if price else "",
                        "change_24h": change.get_text(strip=True) if change else "",
                        "volume": volume.get_text(strip=True) if volume else "",
                        "parsed_at": datetime.now().isoformat()
                    })
            except Exception:
                continue

        logger.info(f"✅ Найдено {len(tokens)} {tab} токенов")
        return tokens

    async def get_all_data(self) -> Dict[str, Any]:
        """Сбор всех данных"""
        logger.info("🚀 Начинаем парсинг KyberSwap...")

        data = {
            "timestamp": datetime.now().isoformat(),
            "source": "kyberswap",
            "trending": [],
            "trending_soon": []
        }

        try:
            data["trending"] = await self.parse_trending("trending")
            await asyncio.sleep(2)
            data["trending_soon"] = await self.parse_trending("trending_soon")
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")

        return data
