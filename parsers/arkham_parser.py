"""
Arkham Intelligence Parser
Собирает: entity labels, wallet tracking, whale alerts
"""
import asyncio
from typing import Dict, List, Any
from datetime import datetime
import logging

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class ArkhamParser:
    """Парсер Arkham Intelligence (требует auth + residential proxies)"""

    def __init__(self, proxy: str = None, auth_cookie: str = None):
        self.base_url = "https://platform.arkhamintelligence.com"
        self.proxy = proxy
        self.auth_cookie = auth_cookie
        self.browser = None

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        browser_args = {
            "headless": True,
            "args": [
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security"
            ]
        }
        if self.proxy:
            browser_args["proxy"] = {"server": self.proxy}

        self.browser = await self.playwright.chromium.launch(**browser_args)

        context_args = {"viewport": {"width": 1920, "height": 1080}}
        if self.auth_cookie:
            context_args["storage_state"] = self.auth_cookie

        self.context = await self.browser.new_context(**context_args)

        # Stealth
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            window.chrome = { runtime: {} };
        """)

        self.page = await self.context.new_page()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def parse_whale_transactions(self) -> List[Dict]:
        """Парсинг крупных транзакций (whale alerts)"""
        logger.info("🐋 Парсим whale transactions...")

        await self.page.goto(f"{self.base_url}/explorer", wait_until="networkidle")
        await asyncio.sleep(5)

        content = await self.page.content()
        soup = BeautifulSoup(content, 'html.parser')

        transactions = []

        # Ищем строки транзакций
        rows = soup.find_all('tr')
        for row in rows[1:31]:  # первые 30
            try:
                cols = row.find_all('td')
                if len(cols) >= 4:
                    transactions.append({
                        "entity": cols[0].get_text(strip=True),
                        "type": cols[1].get_text(strip=True),
                        "amount": cols[2].get_text(strip=True),
                        "asset": cols[3].get_text(strip=True),
                        "parsed_at": datetime.now().isoformat()
                    })
            except Exception:
                continue

        logger.info(f"✅ Найдено {len(transactions)} whale транзакций")
        return transactions

    async def parse_entity_labels(self) -> List[Dict]:
        """Парсинг labeled entities"""
        logger.info("🏷️ Парсим entity labels...")

        await self.page.goto(f"{self.base_url}/entities", wait_until="networkidle")
        await asyncio.sleep(4)

        content = await self.page.content()
        soup = BeautifulSoup(content, 'html.parser')

        entities = []
        cards = soup.find_all(['div', 'tr'], class_=lambda x: x and 'entity' in str(x).lower())

        for card in cards[:20]:
            try:
                name = card.find(['h3', 'h4', 'span', 'a'])
                balance = card.find(['span', 'div'], class_=lambda x: x and 'balance' in str(x).lower())

                if name:
                    entities.append({
                        "name": name.get_text(strip=True),
                        "balance": balance.get_text(strip=True) if balance else "Unknown",
                        "parsed_at": datetime.now().isoformat()
                    })
            except Exception:
                continue

        logger.info(f"✅ Найдено {len(entities)} entities")
        return entities

    async def get_all_data(self) -> Dict[str, Any]:
        """Сбор всех данных"""
        logger.info("🚀 Начинаем парсинг Arkham...")

        data = {
            "timestamp": datetime.now().isoformat(),
            "source": "arkham",
            "whale_transactions": [],
            "entities": []
        }

        try:
            data["whale_transactions"] = await self.parse_whale_transactions()
            await asyncio.sleep(3)
            data["entities"] = await self.parse_entity_labels()
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")

        return data
