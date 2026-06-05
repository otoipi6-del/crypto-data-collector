"""
Dune Analytics Parser
Собирает: public dashboards, query results
"""
import asyncio
from typing import Dict, List, Any
from datetime import datetime
import logging

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class DuneParser:
    """Парсер Dune Analytics (требует auth, лучше использовать API)"""

    def __init__(self, proxy: str = None, auth_cookie: str = None):
        self.base_url = "https://dune.com"
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

    async def parse_trending_dashboards(self) -> List[Dict]:
        """Парсинг трендовых дашбордов"""
        logger.info("📊 Парсим Dune trending dashboards...")

        await self.page.goto(f"{self.base_url}/home", wait_until="networkidle")
        await asyncio.sleep(4)

        content = await self.page.content()
        soup = BeautifulSoup(content, 'html.parser')

        dashboards = []

        cards = soup.find_all(['div', 'article'],
                             class_=lambda x: x and 'dashboard' in str(x).lower())

        for card in cards[:20]:
            try:
                title = card.find(['h3', 'h2', 'h4', 'a'])
                author = card.find(['span', 'div'], 
                                  class_=lambda x: x and 'author' in str(x).lower())
                views = card.find(['span', 'div'], 
                                 class_=lambda x: x and 'view' in str(x).lower())

                if title:
                    dashboards.append({
                        "title": title.get_text(strip=True),
                        "author": author.get_text(strip=True) if author else "Unknown",
                        "views": views.get_text(strip=True) if views else "Unknown",
                        "parsed_at": datetime.now().isoformat()
                    })
            except Exception:
                continue

        logger.info(f"✅ Найдено {len(dashboards)} дашбордов")
        return dashboards

    async def get_all_data(self) -> Dict[str, Any]:
        """Сбор всех данных"""
        logger.info("🚀 Начинаем парсинг Dune...")

        data = {
            "timestamp": datetime.now().isoformat(),
            "source": "dune",
            "dashboards": [],
            "note": "Рекомендуется использовать Dune API (платно) или embed public dashboards"
        }

        try:
            data["dashboards"] = await self.parse_trending_dashboards()
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")

        return data
