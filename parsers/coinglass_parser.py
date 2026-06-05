"""
CoinGlass Parser
Собирает: фьючерсы, OI, funding rates, ликвидации, ETF
"""
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json

logger = logging.getLogger(__name__)


class CoinGlassParser:
    """Парсер CoinGlass (требует Playwright + прокси)"""

    def __init__(self, proxy: str = None):
        self.base_url = "https://www.coinglass.com"
        self.proxy = proxy
        self.browser = None
        self.context = None
        self.page = None

    async def __aenter__(self):
        self.playwright = await async_playwright().start()

        browser_args = {
            "headless": True,
            "args": [
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process"
            ]
        }

        if self.proxy:
            browser_args["proxy"] = {"server": self.proxy}

        self.browser = await self.playwright.chromium.launch(**browser_args)

        context_args = {
            "viewport": {"width": 1920, "height": 1080},
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        self.context = await self.browser.new_context(**context_args)

        # Stealth-скрипт
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
            window.chrome = { runtime: {} };
        """)

        self.page = await self.context.new_page()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def _wait_for_content(self, selector: str, timeout: int = 30000):
        """Ожидание загрузки контента"""
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except:
            return False

    async def parse_futures_data(self) -> Dict[str, Any]:
        """Парсинг данных по фьючерсам"""
        logger.info("📊 Парсим фьючерсные данные...")

        await self.page.goto(f"{self.base_url}/en/futures/LiquidationHeatMap", 
                            wait_until="networkidle")

        # Ждём загрузки таблицы
        if not await self._wait_for_content("table"):
            logger.warning("⚠️ Таблица не загрузилась")
            return {}

        content = await self.page.content()
        soup = BeautifulSoup(content, 'html.parser')

        data = {
            "timestamp": datetime.now().isoformat(),
            "source": "coinglass",
            "futures_data": []
        }

        # Парсим таблицу (структура может меняться!)
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows[1:]:  # skip header
                cols = row.find_all('td')
                if len(cols) >= 5:
                    data["futures_data"].append({
                        "symbol": cols[0].get_text(strip=True),
                        "price": cols[1].get_text(strip=True),
                        "oi": cols[2].get_text(strip=True),
                        "funding": cols[3].get_text(strip=True),
                        "liquidation": cols[4].get_text(strip=True)
                    })

        logger.info(f"✅ Получено {len(data['futures_data'])} записей фьючерсов")
        return data

    async def parse_etf_data(self) -> Dict[str, Any]:
        """Парсинг ETF данных"""
        logger.info("📊 Парсим ETF данные...")

        await self.page.goto(f"{self.base_url}/en/bitcoin-etf", 
                            wait_until="networkidle")

        if not await self._wait_for_content("table", timeout=20000):
            return {}

        content = await self.page.content()
        soup = BeautifulSoup(content, 'html.parser')

        data = {
            "timestamp": datetime.now().isoformat(),
            "source": "coinglass",
            "etf_data": []
        }

        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows[1:]:
                cols = row.find_all('td')
                if len(cols) >= 4:
                    data["etf_data"].append({
                        "etf_name": cols[0].get_text(strip=True),
                        "ticker": cols[1].get_text(strip=True),
                        "holdings": cols[2].get_text(strip=True),
                        "daily_flow": cols[3].get_text(strip=True)
                    })

        return data

    async def get_all_data(self) -> Dict[str, Any]:
        """Сбор всех данных"""
        logger.info("🚀 Начинаем парсинг CoinGlass...")

        data = {
            "timestamp": datetime.now().isoformat(),
            "source": "coinglass",
            "futures": {},
            "etf": {}
        }

        try:
            data["futures"] = await self.parse_futures_data()
            await asyncio.sleep(2)
            data["etf"] = await self.parse_etf_data()
        except Exception as e:
            logger.error(f"❌ Ошибка парсинга: {e}")

        return data
