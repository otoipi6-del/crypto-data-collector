"""
Token Unlocks Parser
Собирает: расписания разблокировок, vesting, allocations
"""
import asyncio
from typing import Dict, List, Any
from datetime import datetime
import logging

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class TokenUnlocksParser:
    """Парсер Token Unlocks"""

    def __init__(self, proxy: str = None):
        self.base_url = "https://token.unlocks.app"
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

    async def parse_upcoming_unlocks(self) -> List[Dict]:
        """Парсинг предстоящих разблокировок"""
        logger.info("🔓 Парсим предстоящие unlock'и...")

        await self.page.goto(f"{self.base_url}/upcoming", wait_until="networkidle")
        await asyncio.sleep(3)

        content = await self.page.content()
        soup = BeautifulSoup(content, 'html.parser')

        unlocks = []

        # Ищем карточки или таблицы с unlock данными
        cards = soup.find_all(['div', 'tr'], class_=lambda x: x and 'unlock' in str(x).lower())

        for card in cards[:50]:  # ограничиваем
            try:
                token_name = card.find(['h3', 'h2', 'span', 'div'], 
                                      class_=lambda x: x and 'name' in str(x).lower())
                date_elem = card.find(['time', 'span', 'div'], 
                                     class_=lambda x: x and 'date' in str(x).lower())
                amount_elem = card.find(['span', 'div'], 
                                       class_=lambda x: x and 'amount' in str(x).lower())

                if token_name:
                    unlocks.append({
                        "token": token_name.get_text(strip=True),
                        "unlock_date": date_elem.get_text(strip=True) if date_elem else "Unknown",
                        "amount": amount_elem.get_text(strip=True) if amount_elem else "Unknown",
                        "parsed_at": datetime.now().isoformat()
                    })
            except Exception as e:
                continue

        logger.info(f"✅ Найдено {len(unlocks)} предстоящих unlock'ов")
        return unlocks

    async def parse_token_allocation(self, token_slug: str) -> Dict:
        """Парсинг распределения токенов"""
        logger.info(f"📊 Парсим распределение {token_slug}...")

        await self.page.goto(f"{self.base_url}/{token_slug}", wait_until="networkidle")
        await asyncio.sleep(2)

        content = await self.page.content()
        soup = BeautifulSoup(content, 'html.parser')

        allocation = {
            "token": token_slug,
            "parsed_at": datetime.now().isoformat(),
            "allocations": [],
            "vesting_schedule": []
        }

        # Парсим allocation chart/bars
        allocation_items = soup.find_all(['div', 'span'], 
                                        class_=lambda x: x and 'allocation' in str(x).lower())
        for item in allocation_items:
            text = item.get_text(strip=True)
            if '%' in text:
                allocation["allocations"].append(text)

        return allocation

    async def get_all_data(self) -> Dict[str, Any]:
        """Сбор всех данных"""
        logger.info("🚀 Начинаем парсинг Token Unlocks...")

        data = {
            "timestamp": datetime.now().isoformat(),
            "source": "token_unlocks",
            "upcoming_unlocks": [],
            "sample_allocations": []
        }

        try:
            data["upcoming_unlocks"] = await self.parse_upcoming_unlocks()

            # Парсим несколько популярных токенов
            popular_tokens = ["ethereum", "optimism", "arbitrum", "aptos"]
            for token in popular_tokens:
                try:
                    alloc = await self.parse_token_allocation(token)
                    data["sample_allocations"].append(alloc)
                    await asyncio.sleep(1)
                except:
                    continue

        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")

        return data
