"""
Token Terminal Parser
Собирает: revenue, fees, active users, P/S ratio, fundamental metrics
"""
import asyncio
from typing import Dict, List, Any
from datetime import datetime
import logging

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class TokenTerminalParser:
    """Парсер Token Terminal"""

    def __init__(self, proxy: str = None, auth_cookie: str = None):
        self.base_url = "https://tokenterminal.com"
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

    async def parse_protocol_metrics(self) -> List[Dict]:
        """Парсинг метрик протоколов"""
        logger.info("📊 Парсим protocol metrics...")

        await self.page.goto(f"{self.base_url}/terminal/projects", wait_until="networkidle")
        await asyncio.sleep(4)

        content = await self.page.content()
        soup = BeautifulSoup(content, 'html.parser')

        protocols = []

        # Ищем таблицу с метриками
        rows = soup.find_all('tr')
        for row in rows[1:51]:  # первые 50 протоколов
            try:
                cols = row.find_all('td')
                if len(cols) >= 6:
                    protocols.append({
                        "name": cols[0].get_text(strip=True),
                        "category": cols[1].get_text(strip=True),
                        "revenue": cols[2].get_text(strip=True),
                        "fees": cols[3].get_text(strip=True),
                        "active_users": cols[4].get_text(strip=True),
                        "ps_ratio": cols[5].get_text(strip=True),
                        "parsed_at": datetime.now().isoformat()
                    })
            except Exception:
                continue

        logger.info(f"✅ Найдено {len(protocols)} протоколов")
        return protocols

    async def get_all_data(self) -> Dict[str, Any]:
        """Сбор всех данных"""
        logger.info("🚀 Начинаем парсинг Token Terminal...")

        data = {
            "timestamp": datetime.now().isoformat(),
            "source": "tokenterminal",
            "protocol_metrics": []
        }

        try:
            data["protocol_metrics"] = await self.parse_protocol_metrics()
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")

        return data
