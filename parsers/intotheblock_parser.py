"""
IntoTheBlock Parser
Собирает: on-chain метрики, крупные транзакции, holder concentration
"""
import asyncio
from typing import Dict, List, Any
from datetime import datetime
import logging

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class IntoTheBlockParser:
    """Парсер IntoTheBlock (требует auth)"""

    def __init__(self, proxy: str = None, auth_cookie: str = None):
        self.base_url = "https://www.intotheblock.com"
        self.proxy = proxy
        self.auth_cookie = auth_cookie
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

        context_args = {"viewport": {"width": 1920, "height": 1080}}
        if self.auth_cookie:
            context_args["storage_state"] = self.auth_cookie

        self.context = await self.browser.new_context(**context_args)
        self.page = await self.context.new_page()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def parse_token_metrics(self, token: str = "bitcoin") -> Dict:
        """Парсинг on-chain метрик токена"""
        logger.info(f"📊 Парсим метрики {token}...")

        await self.page.goto(f"{self.base_url}/coin/{token}", wait_until="networkidle")
        await asyncio.sleep(4)

        content = await self.page.content()
        soup = BeautifulSoup(content, 'html.parser')

        metrics = {
            "token": token,
            "parsed_at": datetime.now().isoformat(),
            "indicators": []
        }

        # Ищем индикаторы
        indicator_cards = soup.find_all(['div', 'section'], 
                                       class_=lambda x: x and 'indicator' in str(x).lower())

        for card in indicator_cards:
            try:
                title = card.find(['h3', 'h4', 'span', 'div'])
                value = card.find(['span', 'div'], class_=lambda x: x and 'value' in str(x).lower())

                if title and value:
                    metrics["indicators"].append({
                        "name": title.get_text(strip=True),
                        "value": value.get_text(strip=True)
                    })
            except Exception:
                continue

        logger.info(f"✅ Найдено {len(metrics['indicators'])} индикаторов")
        return metrics

    async def get_all_data(self, tokens: List[str] = None) -> Dict[str, Any]:
        """Сбор всех данных"""
        logger.info("🚀 Начинаем парсинг IntoTheBlock...")

        if not tokens:
            tokens = ["bitcoin", "ethereum", "solana"]

        data = {
            "timestamp": datetime.now().isoformat(),
            "source": "intotheblock",
            "token_metrics": []
        }

        try:
            for token in tokens:
                metrics = await self.parse_token_metrics(token)
                data["token_metrics"].append(metrics)
                await asyncio.sleep(2)
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")

        return data
