"""
TweetScout Parser
Собирает: Twitter analytics, engagement, community growth
"""
import asyncio
from typing import Dict, List, Any
from datetime import datetime
import logging

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class TweetScoutParser:
    """Парсер TweetScout (требует auth)"""

    def __init__(self, proxy: str = None, auth_cookie: str = None):
        self.base_url = "https://tweetscout.io"
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

    async def parse_project_analytics(self, project_handle: str = None) -> Dict:
        """Парсинг аналитики проекта"""
        logger.info("📱 Парсим TweetScout analytics...")

        if project_handle:
            url = f"{self.base_url}/project/{project_handle}"
        else:
            url = f"{self.base_url}/explore"

        await self.page.goto(url, wait_until="networkidle")
        await asyncio.sleep(4)

        content = await self.page.content()
        soup = BeautifulSoup(content, 'html.parser')

        analytics = {
            "project": project_handle or "explore",
            "parsed_at": datetime.now().isoformat(),
            "metrics": []
        }

        # Ищем метрики
        metric_cards = soup.find_all(['div', 'section'],
                                    class_=lambda x: x and 'metric' in str(x).lower())

        for card in metric_cards:
            try:
                label = card.find(['span', 'div'], class_=lambda x: x and 'label' in str(x).lower())
                value = card.find(['span', 'div'], class_=lambda x: x and 'value' in str(x).lower())

                if label and value:
                    analytics["metrics"].append({
                        "label": label.get_text(strip=True),
                        "value": value.get_text(strip=True)
                    })
            except Exception:
                continue

        logger.info(f"✅ Найдено {len(analytics['metrics'])} метрик")
        return analytics

    async def get_all_data(self) -> Dict[str, Any]:
        """Сбор всех данных"""
        logger.info("🚀 Начинаем парсинг TweetScout...")

        data = {
            "timestamp": datetime.now().isoformat(),
            "source": "tweetscout",
            "analytics": []
        }

        try:
            data["analytics"] = await self.parse_project_analytics()
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")

        return data
