"""
CryptoRank Parser
Собирает: ICO/IEO, fundraising, венчурные инвестиции, рейтинги
"""
import asyncio
from typing import Dict, List, Any
from datetime import datetime
import logging

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class CryptoRankParser:
    """Парсер CryptoRank"""

    def __init__(self, proxy: str = None):
        self.base_url = "https://cryptorank.io"
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

    async def parse_fundraising(self) -> List[Dict]:
        """Парсинг fundraising раундов"""
        logger.info("💰 Парсим fundraising данные...")

        await self.page.goto(f"{self.base_url}/fundraising", wait_until="networkidle")
        await asyncio.sleep(3)

        content = await self.page.content()
        soup = BeautifulSoup(content, 'html.parser')

        rounds = []

        # Ищем таблицы или карточки с fundraising
        rows = soup.find_all('tr')
        for row in rows[1:51]:  # первые 50
            try:
                cols = row.find_all('td')
                if len(cols) >= 5:
                    rounds.append({
                        "project": cols[0].get_text(strip=True),
                        "round": cols[1].get_text(strip=True),
                        "amount": cols[2].get_text(strip=True),
                        "date": cols[3].get_text(strip=True),
                        "investors": cols[4].get_text(strip=True),
                        "parsed_at": datetime.now().isoformat()
                    })
            except Exception:
                continue

        logger.info(f"✅ Найдено {len(rounds)} fundraising раундов")
        return rounds

    async def parse_ico_listings(self) -> List[Dict]:
        """Парсинг ICO/IEO листингов"""
        logger.info("📋 Парсим ICO/IEO...")

        await self.page.goto(f"{self.base_url}/ico", wait_until="networkidle")
        await asyncio.sleep(3)

        content = await self.page.content()
        soup = BeautifulSoup(content, 'html.parser')

        icos = []
        cards = soup.find_all(['div', 'tr'], class_=lambda x: x and 'ico' in str(x).lower())

        for card in cards[:30]:
            try:
                name = card.find(['h3', 'h2', 'span', 'a'])
                date = card.find(['time', 'span'], class_=lambda x: x and 'date' in str(x).lower())
                price = card.find(['span', 'div'], class_=lambda x: x and 'price' in str(x).lower())

                if name:
                    icos.append({
                        "name": name.get_text(strip=True),
                        "date": date.get_text(strip=True) if date else "TBA",
                        "price": price.get_text(strip=True) if price else "TBA",
                        "parsed_at": datetime.now().isoformat()
                    })
            except Exception:
                continue

        logger.info(f"✅ Найдено {len(icos)} ICO/IEO")
        return icos

    async def get_all_data(self) -> Dict[str, Any]:
        """Сбор всех данных"""
        logger.info("🚀 Начинаем парсинг CryptoRank...")

        data = {
            "timestamp": datetime.now().isoformat(),
            "source": "cryptorank",
            "fundraising": [],
            "ico_listings": []
        }

        try:
            data["fundraising"] = await self.parse_fundraising()
            await asyncio.sleep(2)
            data["ico_listings"] = await self.parse_ico_listings()
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")

        return data
